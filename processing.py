import pandas as pd
import numpy as np
import utils
from utils import output_dir

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

#fill in values for Christopher H. Smith who somehow has a different scale (causing issues)
df_as['asset_value'] = np.where((df_as['asset_name'] == "Synchrony Bank") & (df_as['docid'] == 10054556), 50001, df_as['asset_value'])
df_as['asset_value'] = np.where((df_as['asset_name'] == "Vanguard Money Market (inherited IRA)") & (df_as['docid'] == 10054556), 15001, df_as['asset_value'])

#fill in 0 for Min and Max values that are null when DocID greater than 10000000
#this ensures congress members with 0 networth are counted 
df_as['asset_value'] = np.where((df_as['asset_value'].isna()) & (df_as['docid'] > 10000000), 0, df_as['asset_value'])
df_l['Liability_value'] = np.where((df_l['Liability_value'].isna()) & (df_l['docid'] > 10000000), 0, df_l['Liability_value'])

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

#read in manual data
#need to exlude real estate items (make sure to call lower() on the search string)
am_og = pd.read_excel('manual_data/assets_2022FD_manual.xlsx')
lm_og = pd.read_excel('manual_data/liabilities_2022FD_manual.xlsx')

#add col whether RP or not
#If search_string is in x_name, then set col to True
search_string = 'mortgage|home|residence|property|rental|real estate|real-estate'
am_og['asset_type'] = np.where(am_og['name'].str.lower().str.contains(search_string), "RP", None)

#join manual data with df_urls to get docids 
am = df_urls.merge(am_og, left_on='URL', right_on='url', how='inner')
lm = df_urls.merge(lm_og, left_on='URL', right_on='URL', how='inner')

#change DocID to docid
am = am.rename(columns={'DocID': 'docid'})
lm = lm.rename(columns={'DocID': 'docid'})

#subset to get Min, Max, name, docid
am = am[['Min', 'Max', 'name', 'docid', 'asset_type']]
lm = lm[['Min', 'Max', 'name', 'liability_type', 'docid']]

#subset l and a the same way
a = a[['Min', 'Max', 'name', 'docid','asset_type']]
l = l[['Min', 'Max', 'name', 'liability_type', 'docid']]

#concat a and am, l and lm
a_agg = pd.concat([a, am])
l_agg = pd.concat([l, lm])

#filter out real-estate items and calculate non-rp net worth
non_rp_a = utils.non_rp_assets(a_agg)
non_rp_l = utils.non_rp_liabs(l_agg)
net_worth = utils.net_worth_cal(non_rp_a, non_rp_l)

#combine net and url file   
agg = pd.merge(df_urls, net_worth, left_on='DocID', right_on='docid', how='left')

#if DocID greater than 10000000 and Min is NA
#then set Min, Max and avg_value to 0 to account for congress members with no assets or liabilities (so 0 net worth)
agg.loc[(agg['DocID'] > 10000000) & (agg['Min'].isna()), ['Min', 'Max', 'avg_value']] = 0

#label which net worth were calculated with manual data based on docid
agg['manual'] = np.where(agg['DocID'] < 10000000, 'manual', 'auto') 

#write agg to excel. First row is col names
agg.to_excel(f'{output_dir}/net_worth.xlsx', index=False, header=True)

#label asset types 
#where a_agg['asset_type'] is "P", label as '5P'
a_agg['asset_type'] = np.where(a_agg['asset_type'] == 'P', '5P', a_agg['asset_type'])
at = pd.read_excel('asset_types.xlsx')
a_agg = a_agg.merge(at, on='asset_type', how='left')
a_agg['asset_name'] = a_agg['asset_name'].fillna('Other')

#merge a and l datasets with df_url     
af = pd.merge(df_urls, a_agg, left_on='DocID', right_on='docid', how='left')
lf = pd.merge(df_urls, l_agg, left_on='DocID', right_on='docid', how='left')

#write as separate files (for record-keeping)
af.to_excel(f'{output_dir}/assets.xlsx', index=False, header=True)
lf.to_excel(f'{output_dir}/liabilities.xlsx', index=False, header=True)

