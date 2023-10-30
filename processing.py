import pandas as pd
import os
from utils import output_dir

# read url file
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')

# read and combine csv files from output2/csv_files
files = os.listdir(f'{output_dir}/csv_files')

csv_data = []

for f in files: 
    df = pd.read_csv(f'{output_dir}/csv_files/{f}')
    #drop index column
    df = df.drop(columns=['Unnamed: 0'])
    csv_data.append(df)

agg = pd.concat(csv_data, ignore_index=True)

#if [ and ] in asset type, take the letters between them and strip everything else
agg['Asset Type'] = agg['Asset Type'].str.extract(r'\[(.*?)\]')

#combine agg and url file   
agg_url = pd.merge(df_urls, agg, on='URL')

#write agg_url to excel 
agg_url.to_excel(f'{output_dir}/agg_url.xlsx', index=False)

#create main dataset with all assets and liabilities?