import json
import os 
import asyncio
import pandas as pd
import time
from dotenv import load_dotenv
from doctran import Doctran, ExtractProperty
from langchain.document_loaders import PyPDFLoader

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4" #gpt-3.5-turbo works for small pdfs but not larger ones
# consider changing models based on pdf size
# could also cut costs by trimming pdfs to only the relevant sections (might lose on labor costs)
OPENAI_TOKEN_LIMIT = 12000 # we will exceed this limit if we try to run on 300+ pdfs? 

doctran = Doctran(openai_api_key=OPENAI_API_KEY, openai_model=OPENAI_MODEL, openai_token_limit=OPENAI_TOKEN_LIMIT)

# load urls from excel file
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')

#filter for only urls greater than 10000000
df_urls = df_urls[df_urls['DocID'] > 10000000]

# define properties to extract
properties = [
        ExtractProperty(
            name="Name", 
            description="The name of the person",
            type="string",
            required=True
        ),
        ExtractProperty(
            name="Filing ID", 
            description="The filing ID without the #",
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
                        "description": "The initials of the type of asset named between brackets"
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
                        "description": "The name of the liability"
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

#loop each url and extract properties
results = []
for index, row in df_urls.iterrows():
    url = row['URL']
    print(row['Last'])

    # extract text from each page of pdf and save as one string
    # this is necessary because doctran only takes one string as input
    # you could also use pypdf2 to extract text from pdf directly
    loader = PyPDFLoader(url)
    pdf_document = loader.load()
    pdf_content = []
    for page in pdf_document:
        pdf_content.append(page.page_content)
    pdf_content = ''.join(pdf_content)

    # parse pdf content into doctran document
    document = doctran.parse(content=pdf_content)

    # extract properties from document
    async def extract_content():
        transformed_document = await document.extract(properties=properties).execute()
        extracted_text = json.dumps(transformed_document.extracted_properties, indent=2)
        return(extracted_text)
    
    extracted_props = asyncio.run(extract_content())

    # converrt  json
    extracted_props = json.loads(extracted_props)

    # save results to list
    results.append(extracted_props)
    time.sleep(5) #wait between each pdf

    #break after X pdfs, this is for testing purposes
    if index == 3:
        break

# save results to json file
with open('output/results.json', 'w') as f:
    json.dump(results, f, indent=2)

# transform json data objects into dataframe
assets_df = pd.json_normalize(results, record_path=['Assets'], meta=['Name','Filing ID'])
liabilities_df = pd.json_normalize(results, record_path=['Liabilites'], meta=['Name', 'Filing ID'])

# save to excel
assets_df.to_excel('output/assets.xlsx')
liabilities_df.to_excel('output/liabilities.xlsx')
