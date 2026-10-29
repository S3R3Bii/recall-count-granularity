"""Verify paper numbers/tables, approved bytes and bounded PDF exclusions."""
import csv,hashlib,json,re,unicodedata
from pathlib import Path
from pypdf import PdfReader
from config import ROOT

def load(name):
    with (ROOT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def main():
    scope=json.loads((ROOT/'paper/PUBLICATION_SCOPE.json').read_text());assert scope['scope']=='independent-program-study' and scope['formal_submission_target'] is False
    assert len(scope['public_files'])==5
    for name,digest in scope['public_files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    tex=(ROOT/'paper/main.tex').read_text(encoding='utf-8');checks=0
    summary=load('results/evaluation/flag_summary.csv');cal=json.loads((ROOT/'results/calibration.json').read_text())['thresholds'];source=json.loads((ROOT/'results/SOURCE_CHECK.json').read_text());fig=json.loads((ROOT/'results/FIGURE_CHECK.json').read_text());assert fig['status']=='PASS'
    def require(value):
        nonlocal checks
        assert value in tex,value;checks+=1
    def lookup(panel,q,policy,omit=''):return next(r for r in summary if r['panel']==panel and r['q']==q and r['product_policy']==policy and r['omitted_year']==omit)
    for y,n in source['annual_rows'].items():require(f"{y} & {n:,} & {'Calibration' if int(y)<=2021 else 'Evaluation'}")
    for panel in ['All','Class I','Class II','Class III']:
        ts=[t for t in cal if t['panel']==panel and t['omitted_year'] is None and t['q_numerator']==19];et=next(t for t in ts if t['grain']=='events');pt=next(t for t in ts if t['grain']=='products')
        require(f"{panel} & {et['numerator']/et['denominator']:.2f} & {pt['numerator']/pt['denominator']:.2f}")
    for panel,q,label,omit in [('All',q,label,'') for q,label in [('9/10','90th'),('19/20','95th'),('99/100','99th')]]+[(p,'19/20',p,'') for p in ['All','Class I','Class II','Class III']]+[('All','19/20',str(y),str(y)) for y in range(2017,2022)]:
        a=lookup(panel,q,'same_event_threshold',omit);b=lookup(panel,q,'own_product_threshold',omit)
        require(' & '.join([label,a['event_flags'],a['product_flags'],b['product_flags'],b['both'],b['product_only'],b['event_only']]))
    dev=json.loads((ROOT/'results/development/summary.json').read_text());ev=json.loads((ROOT/'results/evaluation/summary.json').read_text());ind=[json.loads((ROOT/f'results/{p}/INDEPENDENT_CHECK.json').read_text()) for p in ['development','evaluation']];rep=json.loads((ROOT/'results/REPRODUCTION.json').read_text())
    for value in [source['rows'],dev['source_products'],ev['source_products'],dev['event_months'],ev['event_months'],fig['global_distinct_events'],ind[0]['independent_value_checks'],ind[1]['independent_value_checks'],rep['exact_fields_or_json_documents'],rep['floating_fields']]:require(f'{value:,}')
    assert (fig['global_multi_month_event_ids'],fig['global_multi_class_event_ids'])==(0,98)
    for value in ['261,184','528','64 thresholds','twelve dependencies','71.15 events','453.20 products','41 / 48','1 / 48','June 2022','March 2023','409 products',r'85.5\%',r'12.17',r'3.59',r'3.50','zero to four','41 to 45','not confidence intervals','not false-positive','not a public recall-alert','not peer reviewed','No human-audited linkage','No source row was discarded']:
        # Capitalization of the publication-status line is intentional.
        if value=='not peer reviewed':assert value in tex.lower();checks+=1
        else:require(value)
    for command in ['python -m pip install -r requirements.txt','python -m unittest discover -s tests -v','python src/check_reproduction.py','python src/verify_figures.py','python src/verify_paper.py','python src/verify_public_package.py']:require(command)
    reader=PdfReader(ROOT/'paper/manuscript.pdf');assert len(reader.pages)==7 and not reader.is_encrypted
    page_text=[unicodedata.normalize('NFKC',p.extract_text() or '') for p in reader.pages]
    titles=['Decision and verified finding','1. Source, rights and observation unit','2. Fixed protocol and comparison','3. All-class results and multiplicity','4. Policy agreement and secondary panels','5. Sensitivity, implications and limits','6. Reproduction and independent evidence']
    for page,title in zip(page_text,titles):assert title in re.sub(r'\s+',' ',page),title
    text='\n'.join(page_text)
    normalized=re.sub(r'\s+',' ',text)
    for command in ['python -m pip install -r requirements.txt','python -m unittest discover -s tests -v','python src/check_reproduction.py','python src/verify_figures.py','python src/verify_paper.py','python src/verify_public_package.py']:assert command in normalized;checks+=1
    assert not re.search(r'(?:[Cc]:\\[Uu]sers\\|/[Uu]sers/|/[Hh]ome/|github_pat_|ghp_[A-Za-z0-9]{20,})',text)
    catalog=reader.trailer['/Root'];assert not any(k in catalog for k in ['/AA','/AcroForm','/Collection'])
    assert not reader.attachments
    names=catalog.get('/Names',{});names=names.get_object() if hasattr(names,'get_object') else names;assert '/JavaScript' not in names
    if '/OpenAction' in catalog:
        action=catalog['/OpenAction'];assert isinstance(action,list),'Active open action rejected'
    for page in reader.pages:
        assert '/AA' not in page
        for ref in page.get('/Annots',[]):
            annot=ref.get_object();assert '/AA' not in annot
            action=annot.get('/A')
            if action:
                action=action.get_object();assert action['/S'] in ['/URI','/GoTo']
                if action['/S']=='/URI':assert str(action['/URI']).startswith('https://')
    result={'status':'PASS','manuscript_pages':7,'numeric_table_and_text_checks':checks,'public_file_hashes_checked':5,'pdf_security':'No active code, attachments, form or additional actions; ordinary HTTPS links and navigation allowed','text_scope':'Bounded high-confidence machine-path/token scan; visual and source review separate'}
    (ROOT/'results/PAPER_CHECK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))

if __name__=='__main__':main()
