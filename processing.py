import pandas as pd
import utils
from utils import output_dir
from importlib import reload
reload(utils)

# read url file
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')

# read and combine csv files from output2/csv_files
df_as = utils.read_assets()
df_l = utils.read_liabs()

#if [ and ] in asset type, take the letters between them and strip everything else
df_as['asset_type'] = df_as['acronyms'].str.extract(r'\[(\w{2})\]')

#read min_to_max 
mtm_a = pd.read_excel('min_to_max_values.xlsx', sheet_name='Assets')
mtm_l = pd.read_excel('min_to_max_values.xlsx', sheet_name='Liabilities')

okay_asset_values = mtm_a['Min']
okay_liab_values = mtm_l['Min']

#ensures noise is removed 
df_as = df_as[df_as['asset_value'].isin(okay_asset_values)]
df_l = df_l[df_l['Liability_value'].isin(okay_liab_values)]

#combine agg and url file   
agg_url = pd.merge(df_urls, df_as, on='URL')

#write agg_url to excel 
agg_url.to_excel(f'{output_dir}/agg_url.xlsx', index=False)

#filter df_l for liability_value containing "Country Bank October"
#convert Liability_value to string 
df_l['Liability_value'] = df_l['Liability_value'].astype(str)

df_l[df_l['Liability_value'].str.contains('Old National Bank')]

#filter df_l for docid == 10053013
df_l[df_l['docid'] == 10054244]
