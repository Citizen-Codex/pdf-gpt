import json
from doctran import Doctran, ExtractProperty
import os 
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
import os

from dotenv import load_dotenv
import asyncio
import pandas as pd

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4" #gpt-3.5-turbo works for small pdfs but not larger ones 
OPENAI_TOKEN_LIMIT = 20000

doctran = Doctran(openai_api_key=OPENAI_API_KEY, openai_model=OPENAI_MODEL, openai_token_limit=OPENAI_TOKEN_LIMIT)

# load urls from excel file
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')

#filter for only urls greater than 10000000
df_urls = df_urls[df_urls['DocID'] > 10000000]



loader = PyPDFLoader("https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2022/10053968.pdf")
pdf_document = loader.load()

# extract text from each page of pdf and save as one string
# this is necessary because doctran only takes one string as input
# you could also use pypdf2 to extract text from pdf directly
pdf_content = []
for page in pdf_document:
    pdf_content.append(page.page_content)
pdf_content = ''.join(pdf_content)

# parse pdf content into doctran document
document = doctran.parse(content=pdf_content)

# define properties to extract
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
                        "description": "The initials of the type of asset named between brackets"
                    },
                    "Minimum value": {
                        "type": "string",
                        "description": "The minimum value of the asset"
                    },
                    "Maximum value": {
                        "type": "string",
                        "description": "The maximum value of the asset"
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
                        "type": "string",
                        "description": "The minimum amount of liability"
                    },
                    "Maximum value": {
                        "type": "string",
                        "description": "The maximum amount of liability"
                    }
                }
            },
            required=True
        )
]

# extract properties from document
async def main():
    transformed_document = await document.extract(properties=properties).execute()
    extracted_text = json.dumps(transformed_document.extracted_properties, indent=2)
    return(extracted_text)

extracted_props = asyncio.run(main())

# turn json into pandas dataframe
assets_df = pd.json_normalize(json.loads(extracted_props), record_path=['Assets'], meta=['Name'])
liabilities_df = pd.json_normalize(json.loads(extracted_props), record_path=['Liabilites'], meta=['Name'])

print(assets_df)

# save to excel
assets_df.to_excel("assets.xlsx")
