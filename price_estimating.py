import pandas as pd
from langchain.document_loaders import PyPDFLoader

# load urls from excel file
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')

#filter for only urls greater than 10000000
df_urls = df_urls[df_urls['DocID'] > 10000000]

pdf_content = []
for index, row in df_urls.iterrows():
    url = row['URL']
    print(row['Last'])

    # extract text from each page of pdf and save as one string
    # this is necessary because doctran only takes one string as input
    # you could also use pypdf2 to extract text from pdf directly
    loader = PyPDFLoader(url)
    pdf_document = loader.load()
    for page in pdf_document:
        pdf_content.append(page.page_content)

pdf_content = ''.join(pdf_content)

# content number of tokens
words = len(pdf_content.split())

# 1,000 tokens is about 750 words, adjust
tokens = words/750*1000

# GPT 4 pricing
tokens/1000*.03