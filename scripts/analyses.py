"""Optional analysis generation. Full native decks bypass this convenience layer."""
from __future__ import annotations
import math
import re


def finite(value, label='number'):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f'{label} must be finite numeric')
    return float(value)


def numeric(value): return format(finite(value), '.17g')


def token(value):
    if not isinstance(value, str) or not value or re.search(r'\s', value):
        raise ValueError('Analysis argument must be one token')
    return value


def resolved_grid(values, direction=1):
    if any(not math.isfinite(v) for v in values) or any((b-a)*direction <= 0 for a,b in zip(values,values[1:])):
        raise ValueError('Requested distinct sweep points are not resolvable in floating-point arithmetic')
    return values


def sweep_grid(s):
    if set(s) != {'source','start','stop','step'}: raise ValueError('DC sweep requires only source/start/stop/step')
    start, stop, step = [finite(s[k], k) for k in ('start', 'stop', 'step')]
    if step == 0 or (stop-start)*step < 0: raise ValueError('DC step must advance toward stop')
    count = math.floor((stop-start)/step + 1e-9)+1
    if not 1 <= count <= 1000000: raise ValueError('Convenience sweep too large; use native deck')
    return resolved_grid([start+i*step for i in range(count)],1 if step > 0 else -1)


def frequency_grid(a):
    start, stop, points = finite(a['start']), finite(a['stop']), a['points']
    if type(points) is not int or not 1 <= points <= 1000000 or start <= 0 or stop < start:
        raise ValueError('Invalid frequency range or point count')
    mode = a['spacing']
    if mode == 'lin':
        return [start] if points == 1 else resolved_grid([start+i*(stop-start)/(points-1) for i in range(points)])
    if mode not in {'dec', 'oct'}: raise ValueError('spacing must be lin, dec or oct')
    base = 10 if mode == 'dec' else 2
    count = math.floor(math.log(stop/start, base)*points+1e-9)+1
    if count > 1000000: raise ValueError('Convenience sweep too large; use native deck')
    return resolved_grid([start*base**(i/points) for i in range(count)])


def build(entry, a, vectors, temperature=None):
    kind = a['type'].lower()
    allowed = {'op': {'type'}, 'dc': {'type','sweeps'},
               'ac': {'type','spacing','points','start','stop'},
               'noise': {'type','output','source','spacing','points','start','stop'},
               'tran': {'type','step','stop','start','max_step','ic','uic'}}
    if kind in allowed and set(a)-allowed[kind]:
        raise ValueError(f'Unknown {kind} analysis fields: {set(a)-allowed[kind]}')
    cards = [] if temperature is None else ['.temp '+numeric(temperature)]
    if kind == 'op':
        command, axis, domain = 'op', 'index', {'count': 1}
    elif kind == 'dc':
        sweeps = a['sweeps']
        if len(sweeps) not in (1, 2): raise ValueError('DC supports one or two sweeps')
        grids = [sweep_grid(s) for s in sweeps]
        command = 'dc '+' '.join(f"{token(s['source'])} {numeric(s['start'])} {numeric(s['stop'])} {numeric(s['step'])}" for s in sweeps)
        source = sweeps[0]['source'].lower()
        axis = 'temp-sweep' if source == 'temp' else ('i-sweep' if source.startswith('i') else 'v-sweep')
        domain = {'grid': grids[0]*(len(grids[1]) if len(grids)==2 else 1), 'segments': len(grids[1]) if len(grids)==2 else 1}
    elif kind in {'ac', 'noise'}:
        frequency = f"{a['spacing']} {a['points']} {numeric(a['start'])} {numeric(a['stop'])}"
        command = f'ac {frequency}' if kind == 'ac' else f"noise {token(a['output'])} {token(a['source'])} {frequency}\nsetplot noise1"
        axis, domain = 'frequency', {'grid': frequency_grid(a), 'positive': True}
    elif kind == 'tran':
        step, stop = finite(a['step']), finite(a['stop'])
        start, maximum = finite(a.get('start', 0)), finite(a.get('max_step', step))
        if step <= 0 or maximum <= 0 or not 0 <= start < stop: raise ValueError('Invalid transient interval/timestep')
        if type(a.get('uic', False)) is not bool: raise ValueError('uic must be boolean')
        for node, value in a.get('ic', {}).items(): cards.append(f'.ic v({token(node)})={numeric(value)}')
        command = f'tran {numeric(step)} {numeric(stop)} {numeric(start)} {numeric(maximum)}'+(' uic' if a.get('uic') else '')
        axis, domain = 'time', {'start': start, 'stop': stop, 'max_step': maximum, 'monotonic': 'increasing', 'start_coverage': 'at_or_after'}
    else: raise ValueError('Unsupported convenience analysis: supply a native deck without analysis')
    if not vectors: raise ValueError('Structured analysis needs exported vectors')
    columns, commands, names = [axis], [], []
    for vector in vectors:
        if set(vector)-{'name','expression','complex'}: raise ValueError('Unknown vector fields')
        if 'complex' in vector and type(vector['complex']) is not bool: raise ValueError('complex must be boolean')
        name, expression = vector['name'], vector['expression']
        if not re.fullmatch(r'[a-z][a-z0-9_]*', name): raise ValueError('Export alias must be lowercase identifier')
        if not isinstance(expression, str) or '\n' in expression or '\r' in expression: raise ValueError('Expression must be one line')
        parts = [(name+'_re', f'real({expression})'), (name+'_im', f'imag({expression})')] if vector.get('complex', kind=='ac') else [(name, expression)]
        for alias, expr in parts:
            if alias in columns: raise ValueError('Duplicate export alias')
            columns.append(alias)
            names.append(alias)
            commands.append(f'let {alias} = {expr}')
    if kind == 'op': commands.extend(['let index = 0', 'setscale index'])
    deck = '\n'.join(['* Native structured analysis', f'.include "{entry}"', *cards, '.control',
        'set numdgt=17', 'set wr_singlescale', 'set wr_vecnames', command, *commands,
        'wrdata analysis.tsv '+' '.join(names), 'quit', '.endc', '.end', ''])
    return deck, {'id': 'analysis', 'path': 'analysis.tsv', 'columns': columns, 'domain': domain}
