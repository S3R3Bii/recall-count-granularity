"""Independent complete raw-response to minimized-field comparison."""
import argparse,csv,gzip,hashlib,json
from pathlib import Path
from config import ROOT,FIELDS,YEARS
from accounting import save_json

def main():
    p=argparse.ArgumentParser();p.add_argument('originals',type=Path);args=p.parse_args();raw=args.originals
    manifest=json.loads((ROOT/'data/source/manifest.json').read_text());checks=0;versions=set();flat=[]
    for year in YEARS:
        pages=[p for p in manifest['pages'] if p['year']==year];assert [p['skip'] for p in pages]==list(range(0,pages[0]['annual_total'],1000))
        total=0
        for page in pages:
            data=(raw/page['original_file']).read_bytes();assert hashlib.sha256(data).hexdigest()==page['original_sha256']
            doc=json.loads(data);versions.add(doc['meta']['last_updated']);assert doc['meta']['results']['total']==page['annual_total']
            subset=(ROOT/page['subset_file']).read_bytes();assert hashlib.sha256(subset).hexdigest()==page['subset_sha256']
            with gzip.open(ROOT/page['subset_file'],'rt',encoding='utf-8',newline='') as f:selected=list(csv.DictReader(f))
            assert len(selected)==len(doc['results'])==page['rows']
            for i,(source,target) in enumerate(zip(doc['results'],selected)):
                for field in FIELDS:assert source[field]==target[field];checks+=1
                assert (target['source_year'],target['source_skip'],target['source_row'])==(str(year),str(page['skip']),str(i));checks+=3
            flat.extend(selected);total+=len(selected)
        assert total==pages[0]['annual_total']
    for probe in manifest['final_probes']:
        data=(raw/probe['original_file']).read_bytes();assert hashlib.sha256(data).hexdigest()==probe['original_sha256']
        m=json.loads(data)['meta'];assert m['last_updated']==manifest['version'] and m['results']['total']==probe['annual_total']
    with (ROOT/'data/records.csv').open(encoding='utf-8',newline='') as f:normalized=list(csv.DictReader(f))
    assert flat==normalized;checks+=len(flat)*8
    assert versions=={manifest['version']}
    cert={'status':'PASS','selected_and_normalized_field_checks':checks,'products':len(flat),'pages':len(manifest['pages']),'final_count_probes':len(manifest['final_probes']),'source_version':manifest['version'],'originals_excluded_from_git':True}
    save_json(ROOT/'results/INDEPENDENT_SOURCE_CHECK.json',cert);print(json.dumps(cert))

if __name__=='__main__':main()
