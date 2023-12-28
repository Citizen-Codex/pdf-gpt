from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import concurrent.futures
import pandas as pd
import utils
from utils import output_dir
import datetime
import json

chat_model = utils.chat_model

#import pages.csv
df_pages = pd.read_csv(f'{output_dir}/asset_pages.csv') 
#add column with docid_page_number to match completed data
df_pages['docid_page_number'] = df_pages['docid'].astype(str) + '_' + df_pages['page_number'].astype(str)

#create aggreage data set from output/csv_files
df_comp = utils.read_assets()

#filter out those already completed
df = df_pages[~df_pages['docid_page_number'].isin(df_comp['docid_page_number'])]

# Convert dataframe to a list of dictionaries for easier processing (could simply store this way in the future)
rows = df.to_dict('records')

parser = PydanticOutputParser(pydantic_object=utils.Assets)

asset_prompt = PromptTemplate(
    template="Return information about assets. Ignore extra info. If 'None' is written, enter 0" + 
    "Do not make up values! Values only belong to 1 asset. Do not assign an individual value to multiple assets" + 
    "\n{format_instructions}\n{text}\n",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


# Define the work to be done by each worker in the pool
def process_row(row, prompt, chat_model, output_dir):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Started processing {row['docid']} at {timestamp}")
    
    docid = row['docid']
    page_number = row['page_number']
    content = row['page_content']
    _input = prompt.format_prompt(text=content)
    output = chat_model(messages=_input.to_messages())
    output_json = json.loads(output.content)
    output_json['docid'] = docid
    output_json['page_number'] = page_number
    results = pd.json_normalize(output_json, record_path=['assets'], meta=['docid', 'page_number'])
    results.to_csv(f'{output_dir}/assets/asset_{docid}_{page_number}.csv', index=False)
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Finished processing {row['docid']} at {timestamp}")


# Using ThreadPoolExecutor to process rows concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=utils.max_workers) as executor:
    # Submit tasks to the executor
    future_to_row = {executor.submit(process_row, row, asset_prompt, chat_model, output_dir): row for row in rows}
    
    # Process as tasks complete
    for future in concurrent.futures.as_completed(future_to_row):
        row = future_to_row[future]
        try:
            future.result()  # Output from process_row
        except Exception as exc:
            print(f'Row {row["docid"]} at url {row["url"]} page {row["page_number"]} generated an exception: {exc}')
        else:
            print(f'Row {row["docid"]} processed successfully.')
