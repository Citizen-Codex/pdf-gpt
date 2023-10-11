import pandas as pd
from langchain.document_loaders import PyPDFLoader

# load urls from excel file
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')

#filter for only urls greater than 10000000
df_urls = df_urls[df_urls['DocID'] > 10000000]

# use tiktoken to estimate price
import tiktoken

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
encoding = tiktoken.encoding_for_model("gpt-4")
tokens = len(encoding.encode(pdf_content))

# GPT 4 pricing
tokens/1000*.03

# GPT 3-16k pricing
tokens/1000*.003

properties = [
        ExtractProperty(
            name="Name", 
            description="The name of the person",
            type="string",
            required=True
        ),
        ExtractProperty(
            name="Assets",
            description="The name of each asset in table A",
            type="array",
            items={
                "type": "object",
                "properties": {
                    "Asset": {
                        "type": "string",
                        "description": "The name of the asset"
                    },
                    "Asset Type": {
                        "type": "string",
                        "description": "The two letters between brackets to the right of the asset name"
                    },
                    "Minimum value": {
                        "type": "integer",
                        "description": "The minimum value of the asset without the dollar sign"
                    },
                    "Maximum value": {
                        "type": "integer",
                        "description": "The maximum value of the asset without the dollar sign"
                    }
                }
            },
            required=True
        ),
        ExtractProperty(
            name="Liabilites",
            description="The name of each liability in table D",
            type="array",
            items={
                "type": "object",
                "properties": {
                    "Creditor": {
                        "type": "string",
                        "description": "The name of the creditor. Exclude the owner information"
                    },
                    "Minimum value": {
                        "type": "integer",
                        "description": "The minimum amount of liability without the dollar sign"
                    },
                    "Maximum value": {
                        "type": "integer",
                        "description": "The maximum amount of liability without the dollar sign"
                    }
                }
            },
            required=True
        )
]
tokens = len(encoding.encode(str(properties)))

