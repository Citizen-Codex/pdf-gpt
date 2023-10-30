import pandas as pd
import time
import utils
from utils import output_dir

# read urls_2022FD.xlsx 
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')

#filter for urls greater than 10000000
df_urls = df_urls[df_urls['DocID'] >= 10000000]

# load already completed urls
completed_urls = utils.read_completed_urls()

# filter out completed urls
df_urls = df_urls[~df_urls['URL'].isin(completed_urls)]

#new method will be to aggregate all pages before hand as a list of dictionaries. Include docid and page number in each dictionary.

#then send batchs to extract_properties function to run about 50-60 at a time 

#loop each url and extract properties
missed_urls = []
for index, row in df_urls.iterrows(): 
    url = row['URL']
    docid = row['DocID']
    last_name = row['Last']
    print(f'{index}: {last_name}')

    #loading pdf content before helps with trouble shooting
    pdf_content = utils.extract_pdf_content(url)

    #edit pdf content before extracting properties
    pdf_content_e = utils.edit_pdf_content(pdf_content,
                                           start_condition="Filing Date:",
                                           end_condition="For the complete list")
    
    utils.extract_properties(url,
                            pdf_content_e, 
                            docid,
                            the_props=utils.asset_props)
    
    #wait between each pdf
    time.sleep(5) 

    # if index >= 2: 
    #     break

#"D: L" - start 
#"F: A" - end
