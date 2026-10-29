"""Rebuild every scientific output offline in an isolated minimized-source copy."""
import csv,gzip,hashlib,json,math,shutil,subprocess,sys,tempfile
from pathlib import Path
from config import ROOT

def csvrows(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def main():
    freeze=json.loads((ROOT/'results/CODE_FREEZE.json').read_text())
    for name,digest in freeze['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==digest,name
    exact=floating=0
    with tempfile.TemporaryDirectory(prefix='recall-replay-') as temp:
        out=Path(temp)
        for name in ['src','data']:shutil.copytree(ROOT/name,out/name)
        (out/'results').mkdir()
        for args in [['ingest.py'],['calibrate.py'],['analyze.py','development'],['verify_analysis.py','development'],['analyze.py','evaluation'],['verify_analysis.py','evaluation']]:
            subprocess.run([sys.executable,str(out/'src'/args[0]),*args[1:]],check=True,capture_output=True,text=True)
        targets=['data/records.csv','results/SOURCE_CHECK.json','results/calibration.json',*[f'results/{phase}/{name}' for phase in ['development','evaluation'] for name in ['monthly_counts.csv','event_memberships.csv','monthly_flags.csv','flag_summary.csv','summary.json']]]
        float_columns={'fanout','top5_product_fraction','product_hhi'}
        for name in targets:
            a=ROOT/name;b=out/name
            if a.suffix=='.csv':
                left=csvrows(a);right=csvrows(b);assert len(left)==len(right),name
                for x,y in zip(left,right):
                    assert x.keys()==y.keys()
                    for k in x:
                        if k in float_columns:assert math.isclose(float(x[k]),float(y[k]),abs_tol=1e-12,rel_tol=0);floating+=1
                        else:assert x[k]==y[k],(name,k);exact+=1
            else:assert json.loads(a.read_text())==json.loads(b.read_text()),name;exact+=1
        for phase in ['development','evaluation']:
            cert=json.loads((out/f'results/{phase}/INDEPENDENT_CHECK.json').read_text());assert cert['status']=='PASS'
    result={'status':'PASS','exact_fields_or_json_documents':exact,'floating_fields':floating,'scope':'Offline normalized source, calibration, all counts/memberships/flags/summaries and two independent SQL reconstructions; no full original or live network needed','freeze_hashes_checked':len(freeze['sha256'])}
    (ROOT/'results/REPRODUCTION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))

if __name__=='__main__':main()
