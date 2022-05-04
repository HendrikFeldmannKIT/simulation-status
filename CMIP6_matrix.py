#!/usr/bin/env python3
import datetime
from pyesgf.search import SearchConnection
import natsort as ns
import numpy as np
import pandas as pd
import re

df = pd.read_csv('../CMIP6_downscaling_plans.csv')

# Drop unnecessary columns
df.drop(
  ['contact', 'estimated_completion_date', 'comments'],
  axis = 'columns', inplace = True
)
df.drop_duplicates(inplace = True)

collapse_institutions = True

domains = sorted(list(set(df.domain)))

f = open(f'CMIP6_matrix.html','w')
f.write(f'''<!DOCTYPE html>
<html><head>
<style>
body {{ padding-bottom: 600px; }}
tr:hover {{background-color:#f5f5f5;}}
th, td {{text-align: center; padding: 3px;}}
table {{border-collapse: collapse;}}
span.planned {{color: #FF9999}}
span.running {{color: #009900}}
span.completed {{color: black; font-weight: bold}}
span.published {{color: #3399FF; font-weight: bold}}
a {{color: DodgerBlue}}
a:link {{ text-decoration: none; }}
a:visited {{ text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
a:active {{ text-decoration: underline;}}
</style>
</head><body>
<h1> CORDEX-CMIP6 downscaling plans summary tables (split by SSP)</h1>
<p style="text-align: right;">(Version: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})</p>
<p style="text-align: justify;">
Simulation status according to CORDEX-CMIP6 downscaling plans reported by the groups and collected in <a href="https://github.com/jesusff/cmip6-for-cordex/blob/main/CMIP6_downscaling_plans.csv">CMIP6_downscaling_plans.csv</a>. Check that file for further details.
To contribute/update simulations use this <a href="https://docs.google.com/document/d/1Jy53yvB9SDOiWcwKRJc_HpWVgmjxZhy-qVviHl6ymDM/edit?usp=sharing">Google doc</a>.
<p style="text-align: justify;">
See also the SSP-collapsed tables <a href="https://jesusff.github.io/cmip6-for-cordex/CMIP6_downscaling_plans_tables.html">here</a>.
<p style="text-align:left"> Domains: |
''')
[f.write(f'<a href="#{dom}">{dom}</a> | ') for dom in domains]
d1 = dict(selector=".level0", props=[('min-width', '100px')])
for domain in domains:
  f.write(f'''<h2 id="{domain}">{domain}</h2>''')
  for exp in ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp585']:
    dom_df = df[(df.domain == domain) & (df.experiment == exp)]
    dom_df = dom_df.assign(htmlstatus=pd.Series('<span class="' + dom_df.status + '">' + dom_df.experiment + '</span>', index=dom_df.index))
    dom_df = dom_df.assign(instmodel=pd.Series(dom_df.institute + '-' + dom_df.rcm_name, index=dom_df.index))
    column_id = 'rcm_name' if collapse_institutions else 'instmodel'
    dom_plans_matrix = dom_df.pivot_table(
      index = ('driving_model', 'ensemble'),
      columns = column_id,
      values = 'htmlstatus',
      aggfunc = lambda x: ' '.join(x.dropna())
    )
    if collapse_institutions:
      inst = dom_df.drop_duplicates(subset=['institute','rcm_name']).pivot_table(
        index = ('driving_model', 'ensemble'),
        columns = 'rcm_name',
        values = 'institute',
        aggfunc = lambda x: ', '.join(x.dropna())
      ).agg(lambda x: ', '.join(x.dropna()))
      inst.name = ('','Institutes')
      dom_plans_matrix = dom_plans_matrix.append(inst)
      dom_plans_matrix = dom_plans_matrix.T.set_index([('','Institutes'),dom_plans_matrix.columns]).T
      dom_plans_matrix.columns.names = ['Institution(s)','RCM']
    f.write(f'''<h3>{exp}</h3>
      <p style="font-size: smaller;"> Colour legend:
        <span class="planned">planned</span>
        <span class="running">running</span>
        <span class="completed">completed</span>
        <span class="published">published</span>
      </p>
    ''')
    f.write(dom_plans_matrix.style
       .set_properties(**{'font-size':'8pt', 'border':'1px lightgrey solid !important'})
       .set_table_styles([d1,{
          'selector': 'th',
          'props': [('font-size', '8pt'),('border-style','solid'),('border-width','1px')]
        }])
       .render()
       .replace('nan','')
       .replace('historical','hist')
    )
f.write('</body></html>')
f.close()
