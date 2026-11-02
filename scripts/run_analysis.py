"""Run a native ngspice deck or generated analysis and evaluate its fresh exports."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import analyses
import native_runner
import results


def run_case(manifest, engine, output):
    manifest, output = Path(manifest).resolve(), Path(output).resolve()
    m = results.load_json(manifest)
    if m.get('schema_version') != 'ngspice-run/2': raise ValueError('Expected schema_version ngspice-run/2; see execution/runner.md migration')
    allowed = {'schema_version','entry','inputs','analysis','vectors','exports','metrics','temperature_degC','startup','environment','timeout_s','test_id'}
    if set(m)-allowed: raise ValueError(f'Unknown manifest fields: {set(m)-allowed}')
    deck, exports = None, m.get('exports',[])
    if 'analysis' in m:
        if exports: raise ValueError('Structured analysis generates its export contract')
        deck, export = analyses.build(m['entry'],m['analysis'],m.get('vectors',[]),m.get('temperature_degC'))
        exports = [export]
    if not exports: raise ValueError('Declare at least one fresh numeric export and its domain')
    if len({e['id'] for e in exports})!=len(exports) or len({e['path'] for e in exports})!=len(exports): raise ValueError('Duplicate export id/path')
    for e in exports: native_runner.relative_path(e['path'])
    metrics = m.get('metrics',[])
    if len({q['id'] for q in metrics})!=len(metrics): raise ValueError('Duplicate metric id')
    execution = native_runner.execute(engine, manifest.parent, m['entry'], output,
        inputs=m.get('inputs',[]), generated_deck=deck, exports=[e['path'] for e in exports],
        startup=m.get('startup',[]), environment=m.get('environment',{}),
        timeout_s=analyses.finite(m.get('timeout_s',60)))
    report = {'schema_version':'ngspice-result/2', 'test_id':m.get('test_id',manifest.stem),
              'execution':execution, 'status':execution['status'], 'metrics':[]}
    if execution['status']=='COMPLETED':
        try:
            tables = {e['id']:results.read_export(Path(execution['work'])/e['path'],e) for e in exports}
            report['exports'] = {name:{'points':len(t['rows']), 'columns':t['columns']} for name,t in tables.items()}
            report['metrics'] = [results.evaluate_metric(tables[q.get('export','analysis')],q) for q in metrics]
            if any(q['status']=='FAIL' for q in report['metrics']): report['status']='FAIL'
            elif not metrics: report['status']='EXECUTED'
            elif execution['warnings']: report['status']='REVIEW_REQUIRED'
            else: report['status']='PASS'
            if execution['warnings']:
                report['warning_disposition']='Numeric contract completed; inspect retained warnings for recovered solver steps versus changed model semantics. No automatic warning waiver.'
        except (ValueError,KeyError,TypeError,OSError,OverflowError) as error:
            report['status'], report['error'] = 'RESULT_ERROR', str(error)
    (output/'result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--engine',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True,help='New output directory; existing paths are refused')
    args = parser.parse_args()
    try: report = run_case(args.manifest,args.engine,args.output)
    except (OSError,ValueError,KeyError,TypeError,OverflowError) as error:
        print(json.dumps({'status':'INPUT_ERROR','error':str(error)})); return 2
    print(json.dumps({'status':report['status'],'result':str(args.output.resolve()/'result.json')}))
    return 0 if report['status'] in {'PASS','EXECUTED'} else 1


if __name__=='__main__': raise SystemExit(main())
