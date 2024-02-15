import requests
import pandas as pd
import zipfile
import io
import utils

#load a zip file from url and specify to use .txt file in zip
r = requests.get('https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2022FD.zip')
z = zipfile.ZipFile(io.BytesIO(r.content))
data = pd.read_csv(z.open('2022FD.txt'), sep = '\t')

# Subset to only include original FD filings and newfilers, types O and H
subset_df = data[(data['FilingType'] == 'O') | (data['FilingType'] == 'H')]

#subset subset_df to duplicate StateDst 
subset_df[subset_df.duplicated(['StateDst'])]

#adjust for duplicates
#change StateDst where last == Gonzalez and first == Vicente to TX34
subset_df.loc[(subset_df['StateDst'] == 'TX15') & (subset_df['Last'] == 'Gonzalez') & (subset_df['First'] == 'Vicente'), 'StateDst'] = 'TX34'

#confirm change worked 
print(subset_df[subset_df['StateDst'] == 'TX15'])

# Make URL for each PDF
subset_df.loc[:,'URL'] = 'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2022/' + subset_df['DocID'].astype(str) + '.pdf'

legis = utils.get_political_info()

#left join subset_df and legis on StateDst
subset_df_pp = subset_df.merge(legis, left_on='StateDst', right_on='statedst', how='left')

#not sure why there are 5 extra documents. May be for house members who died or resigned?
subset_df_pp.to_excel('pdf_urls/urls_2022FD.xlsx', index=False)