import os
from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# load urls from excel file
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')

#filter for only urls greater than 10000000
df_urls = df_urls[df_urls['DocID'] > 10000000]

#drop the first row
df_urls = df_urls.drop(df_urls.index[0]) #for testing. This 2nd pdf is more complicated than the others

# loop through urls and append loaders as list
loaders = []
for index, row in df_urls.iterrows():
    url = row['URL']
    print(row['Last'])
    loader = PyPDFLoader(url)
    loaders.append(loader)
    #break after X pdfs, this is for testing purposes
    if index == 1:
        break

# create index from loaders
index = VectorstoreIndexCreator().from_loaders(loaders)

# query index
query = "Look through each page of the pdf and list all assets in the table schedule A and the min and max value for each asset."
result = index.query(query)

# remove whitespace from result at beginning and end and period
result_slim = result.strip().replace(".", "")

# Split the input string into a list of individual asset-amount pairs
pairs = result_slim.split('; ')

# Initialize lists to store asset, min_amount, and max_amount values
assets = []
min_amounts = []
max_amounts = []

# Extract and separate asset, min_amount, and max_amount values
for pair in pairs:
    parts = pair.split(']')
    if len(parts) == 2:
        asset = parts[0].strip() + ']'  # Include the "]" character in the asset
        amounts = parts[1].strip().split('-')
        if len(amounts) == 2:
            min_amount = amounts[0].strip().replace('$', '').replace(',', '')
            max_amount = amounts[1].strip().replace('$', '').replace(',', '')
            assets.append(asset)
            min_amounts.append(float(min_amount))
            max_amounts.append(float(max_amount))

# Create a DataFrame from the lists
df = pd.DataFrame({'Asset': assets, 'Min Amount': min_amounts, 'Max Amount': max_amounts})

# Display the DataFrame
print(df)