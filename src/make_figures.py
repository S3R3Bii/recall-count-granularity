"""Original figures from retained complete monthly tables; no selected outcomes."""
import csv,shutil
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from config import ROOT,PANELS
from accounting import write_csv

def load(name):
    with (ROOT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def main():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#243447','text.color':'#243447','svg.hashsalt':'recall-grain-v1','pdf.fonttype':42})
    counts=[r for phase in ['development','evaluation'] for r in load(f'results/{phase}/monthly_counts.csv') if r['panel']=='All'];dates=[datetime.strptime(r['month'],'%Y-%m') for r in counts];plot=[]
    def save(fig,name):
        fig.savefig(ROOT/f'figures/{name}.png',dpi=180,bbox_inches='tight')
        fig.savefig(ROOT/f'figures/{name}.pdf',bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None})
        fig.savefig(ROOT/f'figures/{name}.svg',bbox_inches='tight',metadata={'Date':None})
        shutil.copy2(ROOT/f'figures/{name}.pdf',ROOT/f'paper/images/{name}.pdf');plt.close(fig)
    def timeaxis(ax):
        ax.axvline(datetime(2022,1,1),color='#697784',ls='--',lw=1);ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'));ax.grid(axis='y',color='#e0e5e9',lw=.7);ax.set_axisbelow(True);ax.set_xlim(dates[0],dates[-1])
    fig,ax=plt.subplots(figsize=(10,4.3));
    for key,label,color in [('products','Products','#bd4a18'),('events','Distinct events in month','#006b72')]:
        values=[int(r[key]) for r in counts];ax.plot(dates,values,lw=1.6,label=label,color=color)
        plot.extend(dict(figure='monthly-counts',panel='All',month=r['month'],q='',policy='',series=key,value=r[key]) for r in counts)
    timeaxis(ax);ax.set_ylim(bottom=0);ax.set_ylabel('Records / distinct event IDs per month');ax.set_title('One recall event can contain many product records',loc='left',fontweight='bold');ax.legend(frameon=False);ax.text(.01,.96,'Calibration: 2017–2021',transform=ax.transAxes,va='top',fontsize=9);ax.text(.58,.96,'Evaluation: 2022–2025',transform=ax.transAxes,va='top',fontsize=9);fig.tight_layout();save(fig,'monthly-counts')
    fig,axes=plt.subplots(2,1,figsize=(10,5.5),sharex=True)
    for ax,key,label,color in [(axes[0],'fanout','Products per event-month','#006b72'),(axes[1],'top5_product_fraction','Products in five largest events (%)','#835aa0')]:
        values=[float(r[key])*(100 if key=='top5_product_fraction' else 1) for r in counts];ax.plot(dates,values,color=color,lw=1.6);timeaxis(ax);ax.set_ylim(bottom=0,top=100 if key=='top5_product_fraction' else None);ax.set_ylabel(label,fontsize=9)
        plot.extend(dict(figure='event-fanout',panel='All',month=r['month'],q='',policy='',series=key,value=val) for r,val in zip(counts,values))
    axes[0].set_title('Monthly multiplicity and concentration vary',loc='left',fontweight='bold');axes[0].annotate('March 2023: 560 products / 46 events',xy=(datetime(2023,3,1),560/46),xytext=(datetime(2019,6,1),10.5),arrowprops={'arrowstyle':'-','color':'#6a7680'},fontsize=9);fig.tight_layout();save(fig,'event-fanout')
    summary=load('results/evaluation/flag_summary.csv');fig,axes=plt.subplots(2,2,figsize=(11,7.4),sharex=True)
    colors={'neither':'#dce2e7','both':'#006b72','product_only':'#b84a18','event_only':'#466fbb'}
    labels={'neither':'Neither policy','both':'Both policies','product_only':'Product policy only','event_only':'Event policy only'}
    for ax,panel in zip(axes.flat,PANELS):
        rows=[r for r in summary if r['panel']==panel and r['omitted_year']==''];y=np.arange(6);left=np.zeros(6)
        for key in ['both','product_only','event_only','neither']:
            values=[int(r[key]) for r in rows];ax.barh(y,values,left=left,color=colors[key],height=.7,label=labels[key]);left+=values
            plot.extend(dict(figure='flag-agreement',panel=panel,month='',q=r['q'],policy=r['product_policy'],series=key,value=v) for r,v in zip(rows,values))
        ax.set_yticks(y,[('Event threshold' if r['product_policy']=='same_event_threshold' else 'Own threshold')+' · '+{'9/10':'90th','19/20':'95th','99/100':'99th'}[r['q']] for r in rows],fontsize=8);ax.invert_yaxis();ax.set_xlim(0,48);ax.set_xticks([0,12,24,36,48]);ax.set_xlabel('Evaluation months (of 48)');ax.set_title(panel,loc='left',fontweight='bold');ax.spines['left'].set_visible(False)
    handles,labs=axes[0,0].get_legend_handles_labels();fig.legend(handles,labs,loc='lower center',ncol=4,frameon=False,fontsize=9);fig.suptitle('Separate calibration reduces volume disagreement; flagged months can still differ',x=.07,ha='left',fontsize=12,fontweight='bold');fig.tight_layout(rect=[0,.05,1,.95]);save(fig,'flag-agreement')
    write_csv(ROOT/'figures/PLOT_DATA.csv',plot);print('Saved3original figures and528plotted values.')

if __name__=='__main__':main()
