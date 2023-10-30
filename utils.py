from dotenv import load_dotenv
from doctran import Doctran, ExtractProperty
import requests
import PyPDF2
import io
import os
import json
import asyncio
import pandas as pd

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#this way exceeds whatever their max token limit is
OPENAI_TOKEN_LIMIT = 50000

output_dir = "output"

# load doctran and select OPENAI model 
doctran = Doctran(openai_api_key=OPENAI_API_KEY, openai_model="gpt-3.5-turbo", openai_token_limit=OPENAI_TOKEN_LIMIT)

# define properties to extract
liab_props = [
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

asset_props = [
        ExtractProperty(
            name="Assets",
            description="If no assets are found, return empty array with item keys only. Ignore assets with no values or other information.",
            type="array",
            items={
                "type": "object",
                "properties": {
                    "Asset Name": {
                        "type": "string",
                        "description": "The whole name of the asset. Must include letters between brackets [ and ]."
                    },
                    "Acronyms": {
                        "type": "string",
                        "description": "All acronyms following Asset Name. Include brackets."
                    },
                    "Minimum value": {
                        "type": "integer",
                        "description": "The minimum value of the asset without dollar sign"
                    },
                    "Maximum value": {
                        "type": "integer",
                        "description": "The maximum value of the asset without dollar sign"
                    },
                    "Income Type": {
                        "type": "string",
                        "description": "The type of income stated."
                    },
                    "Income Minimum": {
                        "type": "integer",
                        "description": "The minimum income without dollar sign"
                    },
                    "Income Maximum": {
                        "type": "integer",
                        "description": "The maximum income without dollar sign"
                    }
                }
            },
            required=True 
        )
]

def extract_pdf_content(url):
    # Fetch the content of the PDF
    response = requests.get(url)
    response.raise_for_status()  # Check if request was successful

    # Use io.BytesIO to handle the fetched content as a byte stream
    with io.BytesIO(response.content) as open_pdf_file:

        # Use PyPDF2 to read the PDF
        reader = PyPDF2.PdfReader(open_pdf_file)
        pdf_content = []

        # Extract text from each page and store text from each page as separate string in list
        for page_num in range(len(reader.pages)):
            pdf_content.append(reader.pages[page_num].extract_text())

    return(pdf_content)

# extract pages and text from pdf based on start and end conditions
def edit_pdf_content(pdf_content, start_condition, end_condition):
    # initialize list to store results
    results = []

    # iterate through list
    for page in pdf_content:

        #identify index of page with last
        # remove instances of "⇒" followed by a line break ("⇒\n"). Remove both the "⇒" and the line break.
        page = page.replace("⇒\n", "")

        #remove all "⇒"
        page = page.replace("⇒", "")

        # if condition appears in page, remove everything before after it
        if start_condition in page:
            page = page.split(start_condition)[1]

        # if condition appears in page, remove everything before after it
        if end_condition in page:
            page = page.split(end_condition)[0]
            results.append(page)
            break

        # add page to results
        results.append(page)

    return(results)

# extract properties from document
async def extract_content(the_page, the_props):
    # parse pdf content into doctran document
    document = doctran.parse(content=the_page)
    transformed_document = await document.extract(properties=the_props).execute()
    extracted_text = json.dumps(transformed_document.extracted_properties, indent=2)
    return(extracted_text)

def extract_properties(url, pdf_content_e, docid, the_props):
    # initialize list to store results
    results = []
    save_results = True
    # iterate through list
    for i, page in enumerate(pdf_content_e):

        try:
            # run async function and confirm that it ran successfully
            extracted_props = asyncio.run(extract_content(the_page=page, the_props=the_props))
            extracted_props = json.loads(extracted_props)
            # add url to json object (for joining later)
            extracted_props['URL'] = url
            # save results to list
            results.append(extracted_props)

        except Exception as e:
            #original page number is lost in case of liabilities
            print(f'Error extracting properties at ~page {i+1} of doc {url}: {e}')
            save_results = False
            break
        

    #format and save results if no error occurs
    if save_results:
        df = pd.json_normalize(results, record_path=['Assets'], meta=['URL'])
        df.to_csv(f'{output_dir}/csv_files2/assets_{docid}.csv')

    # open completed.csv and append the url
    with open(f'{output_dir}/completed2.csv', 'a') as f:
        f.write(f'{url}\n')

#create function to read urls from completed.csv
def read_completed_urls():
    with open(f'{output_dir}/completed2.csv', 'r') as f:
        completed_urls = f.read().splitlines()
    return(completed_urls)