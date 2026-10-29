"""Validate and retain all selected product records without deduplicating events."""
import csv,gzip,hashlib,json
from collections import Counter
from datetime import datetime
from config import ROOT,FIELDS,YEARS,CLASSES

def validate(rows):
    seen=set();coverage=Counter();cal=Counter()
    for r in rows:
        assert all(isinstance(r[k],str) and r[k] for k in FIELDS)
        assert r['recall_number'] not in seen,'Duplicate product identifier';seen.add(r['recall_number'])
        assert r['event_id'].isdigit() and int(r['event_id'])>0
        date=datetime.strptime(r['report_date'],'%Y%m%d');assert date.strftime('%Y%m%d')==r['report_date']
        assert date.year==int(r['source_year']) and date.year in YEARS
        assert r['classification'] in CLASSES and r['product_type']=='Food'
        coverage[date.strftime('%Y-%m')]+=1
        if date.year<=2021:cal[r['classification'],date.strftime('%Y-%m')]+=1
    expected={f'{y}-{m:02}' for y in YEARS for m in range(1,13)}
    assert set(coverage)==expected,'Missing month'
    nonzero={c:sum(1 for (cl,_),n in cal.items() if cl==c and n>0) for c in CLASSES}
    assert all(n>=20 for n in nonzero.values()),'Calibration class coverage'
    return {'status':'PASS','rows':len(rows),'months':len(coverage),'unique_products':len(seen),'annual_rows':{str(y):sum(n for m,n in coverage.items() if int(m[:4])==y) for y in YEARS},'class_nonzero_calibration_months':nonzero,'monthly_source_rows':dict(sorted(coverage.items()))}

def main():
    manifest=json.loads((ROOT/'data/source/manifest.json').read_text());rows=[]
    for p in manifest['pages']:
        path=ROOT/p['subset_file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==p['subset_sha256']
        with gzip.open(path,'rt',encoding='utf-8',newline='') as f:part=list(csv.DictReader(f))
        assert len(part)==p['rows'];rows.extend(part)
    result=validate(rows)
    for year,total in result['annual_rows'].items():assert total==next(p['annual_total'] for p in manifest['pages'] if p['year']==int(year))
    out=ROOT/'data/records.csv'
    with out.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=[*FIELDS,'source_year','source_skip','source_row'],lineterminator='\n');writer.writeheader();writer.writerows(rows)
    (ROOT/'results/SOURCE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','rows','months','class_nonzero_calibration_months']}))

if __name__=='__main__':main()
