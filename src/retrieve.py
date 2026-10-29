"""Sequential official retrieval; originals are explicitly outside this checkout."""
import argparse,csv,gzip,hashlib,io,json,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen,Request
from config import ROOT,FIELDS,YEARS

def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'IndependentRecallCountingResearch/1.0'}),timeout=90) as response:
        assert response.status==200
        data=response.read()
    return data,json.loads(data)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('originals',type=Path);args=parser.parse_args()
    raw=args.originals.resolve();assert not raw.is_relative_to(ROOT)
    raw.mkdir(parents=True,exist_ok=False)
    manifest=[];global_version=None
    for year in YEARS:
        total=None;skip=0;previous=None;records=[]
        while total is None or skip<total:
            assert skip<=25000,'Published pagination limit reached'
            url='https://api.fda.gov/food/enforcement.json?'+urlencode({'search':f'report_date:[{year}0101 TO {year}1231]','sort':'recall_number.exact:asc','limit':1000,'skip':skip})
            data,doc=fetch(url);meta=doc['meta'];current=meta['results']['total'];version=meta['last_updated']
            if total is None:total=current
            assert current==total and (global_version is None or version==global_version),'Snapshot changed during retrieval'
            global_version=version;rows=doc['results'];assert len(rows)==min(1000,total-skip)
            name=f'{year}-{skip:05d}.json';(raw/name).write_bytes(data)
            selected=[]
            for i,row in enumerate(rows):
                selected.append({**{k:row[k] for k in FIELDS},'source_year':str(year),'source_skip':str(skip),'source_row':str(i)})
                key=row['recall_number'];assert previous is None or key>previous,'Ordering/identity gate failed'
                previous=key
            out=ROOT/'data/source'/name.replace('.json','.csv.gz')
            buf=io.StringIO(newline='');writer=csv.DictWriter(buf,fieldnames=[*FIELDS,'source_year','source_skip','source_row'],lineterminator='\n');writer.writeheader();writer.writerows(selected)
            out.write_bytes(gzip.compress(buf.getvalue().encode(),mtime=0))
            manifest.append({'year':year,'skip':skip,'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'original_file':name,'original_bytes':len(data),'original_sha256':hashlib.sha256(data).hexdigest(),'subset_file':out.relative_to(ROOT).as_posix(),'subset_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'rows':len(rows),'annual_total':total,'last_updated':version})
            records.extend(selected);skip+=1000
            time.sleep(0.25)
        print(json.dumps({'year':year,'retrieved_product_rows':len(records),'version':global_version}),flush=True)
    probes=[]
    for year in YEARS:
        url='https://api.fda.gov/food/enforcement.json?'+urlencode({'search':f'report_date:[{year}0101 TO {year}1231]','limit':1})
        data,doc=fetch(url);meta=doc['meta'];expected=next(p['annual_total'] for p in manifest if p['year']==year)
        assert meta['last_updated']==global_version and meta['results']['total']==expected
        name=f'{year}-final-probe.json';(raw/name).write_bytes(data)
        probes.append({'year':year,'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'original_file':name,'original_sha256':hashlib.sha256(data).hexdigest(),'annual_total':expected,'last_updated':global_version})
        time.sleep(0.25)
    (ROOT/'data/source/manifest.json').write_text(json.dumps({'source':'openFDA food enforcement','version':global_version,'fields':FIELDS,'pages':manifest,'final_probes':probes},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
