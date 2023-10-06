import requests
import pandas as pd
import zipfile
import io

#load a zip file from url and specify to use .txt file in zip
r = requests.get('https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2022FD.zip')
z = zipfile.ZipFile(io.BytesIO(r.content))
data = pd.read_csv(z.open('2022FD.txt'), sep = '\t')

# Subset to only include original FD filings
subset_df = data[(data['FilingType'] == 'O')].reset_index(drop=True)

# Make URL for each PDF
subset_df['URL'] = 'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2022/' + subset_df['DocID'].astype(str) + '.pdf'

subset_df.to_excel('pdf_urls/urls_2022FD.xlsx', index=False)