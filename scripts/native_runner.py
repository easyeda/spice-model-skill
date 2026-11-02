"""Execute reviewed native decks without a device/directive whitelist."""
from __future__ import annotations
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time


def relative_path(value):
    path = Path(value)
    if not value or path.is_absolute() or path.drive or '..' in path.parts:
        raise ValueError(f'Expected relative path without traversal: {value!r}')
    return path


def diagnostics(text):
    fatal = re.compile(r'timestep too small|simulation(?:\(s\))? aborted|fatal|^\s*error\b|^\s*(?:doanalyses|run):|unknown (?:device|model|parameter)|unrecogni[sz]ed.*parameter|(?:parameter|model|device).*ignored|ignored.*(?:parameter|model|device)|could not find a valid model|can.t (?:open|find)|no such (?:vector|file|command)|(?:measure|measurement).*failed|not enough parameters|no simulations run|syntax error|command.*not available|failed to load', re.I)
    warning = re.compile(r'warning|singular matrix|gmin|source stepping|convergence', re.I)
    errors, warnings = [], []
    for line in text.splitlines():
        # ngspice startup banner names its log file; the word "warnings" is not a diagnostic.
        if 'Comments and warnings go to log-file' in line: continue
        if fatal.search(line): errors.append(line.strip())
        elif warning.search(line): warnings.append(line.strip())
    solver = [w for w in warnings if re.search(r'singular matrix|gmin|source stepping|convergence',w,re.I)]
    return {'errors': errors, 'warnings': warnings, 'solver_recovery_diagnostics': solver,
            'other_warnings': [w for w in warnings if w not in solver]}


def execute(engine, root, entry, output, *, inputs=(), generated_deck=None,
            exports=(), startup=(), environment=None, timeout_s=60):
    engine, root, output = Path(engine).resolve(), Path(root).resolve(), Path(output).resolve()
    if not engine.is_file(): raise ValueError(f'Engine does not exist: {engine}')
    if timeout_s <= 0: raise ValueError('timeout_s must be positive')
    output.mkdir(parents=True, exist_ok=False)
    staged = output / 'work'
    staged.mkdir()
    for item in dict.fromkeys([entry, *inputs]):
        rel = relative_path(item)
        source = (root / rel).resolve()
        if not source.is_relative_to(root): raise ValueError('Input symlink escapes root')
        target = staged / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            if output == source or output.is_relative_to(source):
                raise ValueError('Run output must be outside every staged input directory')
            if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in source.rglob('*')):
                raise ValueError('Input bundle contains links/junctions; declare files explicitly')
            shutil.copytree(source, target, dirs_exist_ok=True)
        else: shutil.copyfile(source, target)
    deck = staged / relative_path(entry)
    if generated_deck is not None:
        deck = staged / '__analysis__.cir'
        if deck.exists(): raise ValueError('Input collides with __analysis__.cir')
        deck.write_text(generated_deck, encoding='utf-8')
    for name in exports:
        target = staged / relative_path(name)
        if target.exists(): raise ValueError(f'Export already present among staged inputs: {name}')
        target.parent.mkdir(parents=True, exist_ok=True)
    init = output / 'init'
    init.mkdir()
    (init / 'spinit').write_text('\n'.join(startup) + '\n', encoding='utf-8')
    env = os.environ.copy()
    env.update(environment or {})
    env['SPICE_SCRIPTS'] = str(init)
    command = [str(engine), '-n', '-b', '-o', str(output/'engine.log'), str(deck)]
    started = time.monotonic()
    options = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {'start_new_session': True}
    proc = subprocess.Popen(command, cwd=staged, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, **options)
    cleanup = None
    try:
        stdout, stderr = proc.communicate(timeout=timeout_s)
        code, status = proc.returncode, 'COMPLETED'
    except subprocess.TimeoutExpired as error:
        cleanup = {'scope': 'launched process tree' if os.name=='nt' else 'launched process group',
                   'pid': proc.pid, 'success': False}
        try:
            if os.name=='nt':
                # Only the PID returned by this Popen is eligible; never match executable names.
                killed = subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],
                    capture_output=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
                cleanup.update(success=killed.returncode==0, returncode=killed.returncode,
                               detail=(killed.stdout+killed.stderr).decode('mbcs', errors='replace'))
            else:
                os.killpg(proc.pid, signal.SIGKILL)
                cleanup['success'] = True
        except (OSError,subprocess.TimeoutExpired) as cleanup_error:
            cleanup['detail'] = str(cleanup_error)
        if proc.poll() is None:
            proc.kill()
        try:
            stdout, stderr = proc.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            # An escaped descendant may retain a pipe; do not block indefinitely.
            cleanup['success'] = False
            cleanup['detail'] = cleanup.get('detail','')+'; output pipe remained open after cleanup'
            stdout, stderr = error.stdout or b'', error.stderr or b''
            proc.stdout.close()
            proc.stderr.close()
        code, status = proc.returncode, 'TIMEOUT'
    log = (stdout + b'\n' + stderr).decode('utf-8', errors='replace')
    if (output/'engine.log').exists():
        log += '\n' + (output/'engine.log').read_text(encoding='utf-8', errors='replace')
    (output / 'ngspice.log').write_text(log, encoding='utf-8')
    diag = diagnostics(log)
    if status == 'COMPLETED' and (code != 0 or diag['errors']): status = 'EXECUTION_FAILED'
    return {'status': status, 'returncode': code, 'command': command, 'timeout_cleanup': cleanup,
            'elapsed_s': time.monotonic()-started, 'work': str(staged),
            'log': str(output/'ngspice.log'), 'startup': list(startup),
            'environment_overrides': environment or {}, **diag}

