"""Parse fresh ngspice numeric exports and evaluate independent numeric oracles."""
from __future__ import annotations
import bisect
import json
import math
from pathlib import Path
from analyses import finite


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result: raise ValueError(f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    def invalid(value): raise ValueError(f'Nonfinite JSON constant: {value}')
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique, parse_constant=invalid)


def scale_allowance(value, resolution=None):
    allowance = 1e-14 + 1e-8*abs(value)
    if resolution is not None: allowance = min(allowance, resolution*1e-3)
    return allowance


def grid_allowances(grid):
    """Rounding must not make adjacent distinct requested points interchangeable.

    Repeated scales remain valid for declared nested sweeps. Compare each row
    against its requested position, using the nearest distinct scale spacing.
    """
    distinct = sorted(set(grid))
    allowances = {}
    for i, value in enumerate(distinct):
        allowance = scale_allowance(value)
        if i: allowance = min(allowance, (value-distinct[i-1])/4)
        if i+1 < len(distinct): allowance = min(allowance, (distinct[i+1]-value)/4)
        allowances[value] = allowance
    return allowances


def read_export(path, spec):
    lines = [line.split() for line in Path(path).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    columns = spec['columns']
    if not lines or lines[0] != columns or len(set(columns)) != len(columns):
        raise ValueError(f"Export {spec['id']}: missing/duplicate/wrong column header")
    rows = []
    for i, line in enumerate(lines[1:]):
        if len(line) != len(columns): raise ValueError(f'Malformed export row {i}')
        rows.append([finite(float(value), 'export value') for value in line])
    if not rows: raise ValueError('Export contains no rows')
    domain = spec['domain']
    x = [r[0] for r in rows]
    if not any(k in domain for k in ('grid', 'count')) and not {'start','stop','monotonic'} <= domain.keys():
        raise ValueError('Export needs expected grid, count, or start/stop/monotonic domain')
    if 'count' in domain and (type(domain['count']) is not int or len(rows) != domain['count']):
        raise ValueError('Export point count mismatch')
    if 'grid' in domain:
        grid = [finite(v) for v in domain['grid']]
        allowances = grid_allowances(grid)
        if len(x) != len(grid) or any(abs(v-t) > allowances[t] for v,t in zip(x,grid)):
            raise ValueError('Export grid mismatch or incomplete sweep')
    if domain.get('positive') and any(v <= 0 for v in x): raise ValueError('Nonpositive export scale')
    order = domain.get('monotonic')
    if order:
        sign = {'increasing':1, 'decreasing':-1}[order]
        if any((b-a)*sign <= 0 for a,b in zip(x,x[1:])): raise ValueError('Duplicate or unordered export scale')
    resolution = None
    if 'max_step' in domain:
        maximum = finite(domain['max_step'])
        if maximum <= 0: raise ValueError('Export max_step must be positive')
        resolution = maximum
    if 'start' in domain and 'stop' in domain:
        span = abs(finite(domain['stop'])-finite(domain['start']))
        if math.isfinite(span) and span > 0:
            resolution = min(resolution,span) if resolution is not None else span
    if 'start' in domain:
        start = finite(domain['start'])
        allowance = scale_allowance(start,resolution)
        if domain.get('start_coverage') == 'at_or_after':
            # ngspice tstart suppresses points before start; first saved step may follow it.
            maximum = finite(domain['max_step'])
            if x[0] < start-allowance or x[0]-start > maximum+scale_allowance(maximum,resolution): raise ValueError('Transient initial coverage missing')
        elif abs(x[0]-start) > allowance: raise ValueError('Export start mismatch')
    if 'stop' in domain:
        stop = finite(domain['stop'])
        if abs(x[-1]-stop) > scale_allowance(stop,resolution): raise ValueError('Export terminated early')
    if 'max_step' in domain:
        maximum = finite(domain['max_step'])
        if any(b-a > maximum+scale_allowance(maximum,resolution) for a,b in zip(x,x[1:])): raise ValueError('Export timestep exceeds maximum')
    return {'columns': columns, 'rows': rows, 'domain': domain}


def interpolate(x, y, targets):
    if any(b <= a for a,b in zip(x,x[1:])): raise ValueError('Interpolation requires increasing scale; select one sweep segment')
    result = []
    for t in targets:
        t = finite(t)
        if t < x[0] or t > x[-1]: raise ValueError('Metric sampling would extrapolate')
        k = bisect.bisect_left(x,t)
        if k < len(x) and x[k] == t: result.append(y[k])
        else:
            f = (t-x[k-1])/(x[k]-x[k-1])
            result.append(finite(y[k-1]+f*(y[k]-y[k-1])))
    return result


def metric_actual(table, m):
    rows, columns = table['rows'], table['columns']
    segments = table['domain'].get('segments',1)
    if 'segment' in m:
        segment = m['segment']
        if type(segment) is not int or not 0 <= segment < segments: raise ValueError('Invalid sweep segment')
        n = len(rows)//segments
        rows = rows[segment*n:(segment+1)*n]
    elif segments > 1 and m['operation'] not in {'points','min','max','bounds'}:
        raise ValueError('Select a sweep segment for scalar/integral/timing metrics')
    x = [r[0] for r in rows]
    component = m.get('component', 'value')
    if component in {'magnitude','phase_deg','phase_rad'}:
        real, imag = columns.index(m['real']), columns.index(m['imag'])
        y = [abs(complex(r[real],r[imag])) if component=='magnitude' else math.atan2(r[imag],r[real]) for r in rows]
        if component.startswith('phase') and m.get('unwrap',False):
            for i in range(1,len(y)):
                while y[i]-y[i-1] > math.pi: y[i] -= 2*math.pi
                while y[i]-y[i-1] < -math.pi: y[i] += 2*math.pi
        if component=='phase_deg': y = [v*180/math.pi for v in y]
    elif component == 'value': y = [r[columns.index(m['column'])] for r in rows]
    else: raise ValueError('Unknown metric component')
    if 'at' in m:
        if not isinstance(m['at'],list) or not m['at']:
            raise ValueError('Metric at must select at least one sample')
        y, x = interpolate(x,y,m['at']), m['at']
    op = m['operation']
    if op in {'points','bounds'}: return y
    if op == 'scalar':
        if len(y)!=1: raise ValueError('Scalar requires one result or one sampling point')
        return y[0]
    if op == 'min': return min(y)
    if op == 'max': return max(y)
    if op == 'integral':
        if len(x)<2 or any(b<=a for a,b in zip(x,x[1:])): raise ValueError('Integral needs increasing scale')
        return finite(sum((b-a)*(v+w)/2 for a,b,v,w in zip(x,x[1:],y,y[1:])))
    if op == 'crossing':
        level = finite(m['level'])
        direction, occurrence = m.get('direction','rising'), m.get('occurrence',1)
        if direction not in {'rising','falling','either'} or type(occurrence) is not int or occurrence<1: raise ValueError('Invalid crossing selector')
        if len(x)<2 or any(b<=a for a,b in zip(x,x[1:])): raise ValueError('Timing requires increasing scale')
        hits = []
        for a,b,v,w in zip(x,x[1:],y,y[1:]):
            rising, falling = v < level <= w, v > level >= w
            if (rising and direction in {'rising','either'}) or (falling and direction in {'falling','either'}):
                hits.append(a+(b-a)*(level-v)/(w-v))
        if len(hits)<occurrence: raise ValueError('Required threshold crossing absent')
        return hits[occurrence-1]
    raise ValueError('Unsupported metric; use a separate deterministic evaluator on fresh exports')


def evaluate_metric(table, m):
    allowed = {'id','export','column','operation','at','segment','component','real','imag','unwrap',
               'expected','atol','rtol','minimum','maximum','level','direction','occurrence','unit','source','tolerance_basis'}
    if set(m)-allowed: raise ValueError(f"Unknown metric keys (caller actual is forbidden): {set(m)-allowed}")
    for key in ('id','unit','source','tolerance_basis'):
        if not isinstance(m.get(key),str) or not m[key].strip(): raise ValueError(f'Metric requires {key}')
    actual = metric_actual(table,m)
    values = actual if isinstance(actual,list) else [actual]
    if not values: raise ValueError('Metric selected no samples')
    for v in values: finite(v)
    if 'expected' in m:
        expected = m['expected'] if isinstance(m['expected'],list) else [m['expected']]
        if len(values)!=len(expected): raise ValueError('Expected/actual point count differs')
        atol, rtol = finite(m.get('atol',0)), finite(m.get('rtol',0))
        if atol<0 or rtol<0: raise ValueError('Tolerance cannot be negative')
        failed = [i for i,(v,e) in enumerate(zip(values,expected)) if abs(v-finite(e)) > finite(atol+rtol*abs(e))]
    elif 'minimum' in m or 'maximum' in m:
        lower = finite(m['minimum']) if 'minimum' in m else -math.inf
        upper = finite(m['maximum']) if 'maximum' in m else math.inf
        if lower>upper: raise ValueError('Reversed metric bounds')
        failed = [i for i,v in enumerate(values) if not lower<=v<=upper]
    else: raise ValueError('Metric needs independent expected or numeric bounds')
    return {'id':m['id'], 'status':'FAIL' if failed else 'PASS', 'actual':actual,
            'failed_points':failed, 'unit':m['unit'], 'source':m['source'], 'tolerance_basis':m['tolerance_basis']}
