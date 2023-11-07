import pandas as pd
import numpy as np
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
df_as['asset_type'] = df_as['acronyms'].str.extract(r'\[(\w{1,2})\]')

#filter out row where from df_l val col is "." 
df_l = df_l[df_l['Liability_value'] != '.']

#Remove na values from df_l val col
df_l = df_l.dropna(subset=['Liability_value'])

#convert val col to type int
df_l['Liability_value'] = df_l['Liability_value'].astype(int)

#read min_to_max. Change col Min to type int 
mtm_a = pd.read_excel('min_to_max_values.xlsx', sheet_name='Assets')
mtm_l = pd.read_excel('min_to_max_values.xlsx', sheet_name='Liabilities')

#inner join okay_asset_values with df_as 
#Ensures noise is removed. Helps remove made-up values
a = df_as.merge(mtm_a, left_on='asset_value', right_on='Min', how='inner')
l = df_l.merge(mtm_l, left_on='Liability_value', right_on='Min', how='inner')

#change asset_name to name and liability_name to name
a = a.rename(columns={'asset_name': 'name'})
l = l.rename(columns={'liability_name': 'name'})

#filter out real-estate items and calculate non-rp net worth
non_rp_a = utils.non_rp_assets(a)
non_rp_l = utils.non_rp_liabs(l)
net_worth = utils.net_worth_cal(non_rp_a, non_rp_l)

#combine net and url file   
agg = pd.merge(df_urls, net_worth, left_on='DocID', right_on='docid', how='left')

#write agg to excel. First row is col names
agg.to_excel(f'{output_dir}/net_worth.xlsx', index=False, header=True)
