import json
import os 
import asyncio
import pandas as pd
import time
from dotenv import load_dotenv
from doctran import Doctran, ExtractProperty
from langchain.document_loaders import PyPDFLoader
import tiktoken

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TOKEN_LIMIT = 50000 

# get encoding for model 
encoding = tiktoken.encoding_for_model("gpt-4")

# filter urls for only those that have not been extracted
# load output/*.json files into dataframe
all_results = []
for filename in os.listdir('output/'):
    with open(f'output/{filename}') as f:
        data = json.load(f)
        all_results.append(data)

# pull urls from results object 
urls = []
for result in all_results:
    urls.append(result['URL'])

# filter df_urls for urls not in results
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')
df_urls= df_urls[~df_urls['URL'].isin(urls)]

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

#loop each url and extract properties
results = []
missed_urls = []
for index, row in df_urls.iterrows(): 
    url = row['URL']
    docid = row['DocID']
    last_name = row['Last']
    print(f'{index}: {last_name}')

    # extract text from each page of pdf and save as one string 
    loader = PyPDFLoader(url)
    pdf_document = loader.load()
    pdf_content = []
    for page in pdf_document:
        pdf_content.append(page.page_content) #consider removing non-word characters
    pdf_content = ''.join(pdf_content)

    # content number of tokens
    tokens = len(encoding.encode(pdf_content))

    #print number of tokens
    print(f'Number of tokens: {tokens}')

    if tokens < 7500:
        doctran = Doctran(openai_api_key=OPENAI_API_KEY, openai_model="gpt-4", openai_token_limit=OPENAI_TOKEN_LIMIT)
    else: 
        doctran = Doctran(openai_api_key=OPENAI_API_KEY, openai_model="gpt-3.5-turbo-16k", openai_token_limit=OPENAI_TOKEN_LIMIT)

    # parse pdf content into doctran document
    document = doctran.parse(content=pdf_content)

    # extract properties from document (could move out of loop)
    async def extract_content():
        transformed_document = await document.extract(properties=properties).execute()
        extracted_text = json.dumps(transformed_document.extracted_properties, indent=2)
        return(extracted_text)
    
    try:
        # run async function and confirm that it ran successfully
        extracted_props = asyncio.run(extract_content())
        extracted_props = json.loads(extracted_props)
        # add url to json object
        extracted_props['URL'] = url
        # save results to list
        results.append(extracted_props)
        # write results with json to individual files
        with open(f'output/{docid}.json', 'w') as f:
            json.dump(extracted_props, f, indent=2)

    except Exception as e:
        print(f'Error extracting properties at index {index} and docid {docid} corresponding to {url}: {e}')

        
    time.sleep(30) #wait between each pdf

    # break after 100 urls (avoid bad gateway error)
    if index == 50:
        break
