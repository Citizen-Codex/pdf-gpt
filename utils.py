from dotenv import load_dotenv
import requests
import PyPDF2
import io
import os
import pandas as pd
import re
from langchain.chat_models import ChatOpenAI
from typing import List
from langchain.pydantic_v1 import BaseModel, Field

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#this way exceeds whatever their max token limit is
OPENAI_TOKEN_LIMIT = 50000

output_dir = "output"

chat_model = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.0,
    max_tokens=1000
)

#define pydantic model
class AssetItem(BaseModel):
    asset_name: str = Field(description="The name of the asset. Ignore content above asset name." + 
                            "Ignore comments beginning with 'D:', 'C:' or 'L:'.")
    asset_value: int = Field(description="The dollar value of the asset. Drop dollar sign.")
    # max_asset_value: int = Field(description="The maximum dollar value of the asset. Drop the dollar sign.")
    acronyms: str = Field(description="All acronyms between asset name and asset value. Must Include brackets. E.g. [IR], [RP], or [PE]")

#make it into a list
class Assets(BaseModel):
    assets: List[AssetItem]

#define pydantic model
class LiabilityItem(BaseModel):
    liability_name: str = Field(description="The name of the liability. Ignore comments beginning with 'D:', 'C:' or 'L:'.")
    liability_type: str = Field(description="The type of the liability")
    Liability_value: int = Field(description="The dollar value of the liability. Don't include the dollar sign. Do not make up values or assign a single value to multiple liabilities. Do not round or change values! If value ends in 1, keep 1")

#make it into a list
class Liabilities(BaseModel):
    liabilities: List[LiabilityItem]

# Setup for ThreadPoolExecutor
max_workers = 10  # Maximum number of threads. Expect 1000 words per request. Could be as high as 2000

def pull_pdf_content(url):
    # Fetch the content of the PDF
    response = requests.get(url)
    response.raise_for_status()  # Check if request was successful

    # Use io.BytesIO to handle the fetched content as a byte stream
    with io.BytesIO(response.content) as open_pdf_file:

        # Use PyPDF2 to read the PDF
        reader = PyPDF2.PdfReader(open_pdf_file)
        pages = []

        #apply extract_text() to reader.pages
        pages = [page.extract_text() for page in reader.pages]

    return(pages)

def clean_content(page):

    #remove all "\x00"
    page = page.replace("\x00", "")

    #remove commas 
    page = page.replace(',', '')

    # replace "Over $50000000" with "$50000001-$100000000"
    page = page.replace('Over $50000000', '$50000001-$100000001')

    #remove line break between Over and $1000000
    page = page.replace('Over\n$1000000', 'Over $1000000')

    # replace "Over $1000000" with "$1000000-$5000000"
    page = page.replace('Over $1000000', '$1000000-$5000000')

    #remove "Spouse/DC"
    page = page.replace('Spouse/DC', '')

    # replace "None" with "$0-$0"
    # page = page.replace('None', '$0-$100') #this catches a lot of none disclosed

    # replace "Undetermined" with "$0-$0"
    page = page.replace('Undetermined', '$0-$0')

    #clean up comments with "⇒"
    page_lines = page.split('\n')

    #if a line contains "⇒" but not $ or [, then combine with follow (AI interprets these as separate assets)
    #we can't delete them outright becauses sometimes they are the only info for the line
    for index, line in enumerate(page_lines):
        #adding $ and [ ensures you don't combine a line with asset info with something random 
        if "⇒" in line and not "$" in line and not "[" in line and index < len(page_lines) - 1:
            page_lines[index + 1] = line + ' ' + page_lines[index + 1]
            page_lines[index] = ''

    page = '\n'.join(page_lines)

    # #remove instances of "⇒" followed by a line break ("⇒\n"). Remove both the "⇒" and the line break.
    page = page.replace("⇒\n", "")

    #remove all "⇒"
    page = page.replace("⇒", "")

    # Remove line breaks that are in front of "$" dollar signs
    page = re.sub(r'[\n\r]\$', '$', page)

    #remove any spaces between a dash and $
    page = re.sub(r'-\s\$', '-$', page)

    #remove any spaces betweeb a digit and a dash. Don't delete digit
    page = re.sub(r'(\d)\s\-', r'\1-', page)

    #need to use compile to remove numbers with no dash following. This helps to deal with page breaks
    reg = re.compile(r'\D+|(?<=\$)\d+(?=\-)')
    page = ''.join(reg.findall(page))

    #remove -$ with re
    page = re.sub(r'\-\$', '', page)

    return(page)

#should break cleaning into a separate loop for clarity (vectorize?)
def extract_pdf_content(url, docid, start_condition, end_condition1, end_condition2):
    pages = pull_pdf_content(url)
    results = []
    #get index of first page in list with start_condition
    start_index = [index for index, item in enumerate(pages) if start_condition in item][0]

    #remove top of the start page
    pages[start_index] = pages[start_index].split(start_condition)[1]

    for index, page in enumerate(pages[start_index:len(pages)]):
        #page contains no $ signs, skip it 
        page_dict = {}
        page_dict['url'] = url
        page_dict['docid'] = docid
        #adjust page number to match original document   
        page_dict['page_number'] = index + start_index + 1
        if end_condition1 in page:
            #remove bottom of the end page
            page = page.split(end_condition1)[0]
            page = clean_content(page)
            page_dict['page_content'] = page
            results.append(page_dict)
            break
        if end_condition2 in page:
            #remove bottom of the end page
            page = page.split(end_condition2)[0]
            page = clean_content(page)
            page_dict['page_content'] = page.split(end_condition2)[0]
            results.append(page_dict)
            break
        else:
            page = clean_content(page)
            page_dict['page_content'] = page
            results.append(page_dict)

    return(results)

def read_assets():
    df_list = []
    for filename in os.listdir(f'{output_dir}/assets'):
        if filename.startswith('asset'):
            df_temp = pd.read_csv(f'{output_dir}/assets/{filename}')
            df_list.append(df_temp)
    df_comp = pd.concat(df_list, ignore_index=True)
    df_comp['docid_page_number'] = df_comp['docid'].astype(str) + '_' + df_comp['page_number'].astype(str)
    return(df_comp)

def read_liabs():
    df_list = []
    for filename in os.listdir(f'{output_dir}/liabs'):
        if filename.startswith('liab'):
            df_temp = pd.read_csv(f'{output_dir}/liabs/{filename}')
            df_list.append(df_temp)
    df_comp = pd.concat(df_list, ignore_index=True)
    df_comp['docid_page_number'] = df_comp['docid'].astype(str) + '_' + df_comp['page_number'].astype(str)
    #change val col to type int
    return(df_comp)


#call function to output real-estate net worth and asset networth
def non_rp_assets(assets):
    #split df with asset_type != RP
    not_rp = assets[assets['asset_type'] != 'RP']
    return not_rp

def non_rp_liabs(liabilities):
    search_string = 'mortgage|home|residence|property|rental|real estate|real-estate'
    liabilities['name_type'] = liabilities['name'] + liabilities['liability_type']
    liabilities['rp'] = liabilities['name_type'].str.contains(search_string, case=False)
    #split df with rp = False
    not_rp = liabilities[liabilities['rp'] == False]
    return not_rp

def net_worth_cal(assets, liabilities):
    assets = assets[['Min', 'Max', 'docid']]
    liabilities = liabilities[['Min', 'Max', 'docid']]
    #make cols negative
    liabilities.loc[:, 'Min'] = liabilities['Min'] * -1
    liabilities.loc[:, 'Max'] = liabilities['Max'] * -1
    #concat assets and liabilities
    net = pd.concat([assets, liabilities])
    #group by docid
    net = net.groupby('docid').sum()
    #take average 
    net['avg_value'] = (net['Min'] + net['Max']) / 2
    return(net)