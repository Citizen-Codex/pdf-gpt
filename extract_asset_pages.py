import pandas as pd
import utils
from utils import output_dir
from importlib import reload
reload(utils)

#read pdf_urls
df_urls = pd.read_excel('pdf_urls/urls_2022FD.xlsx')

#filter for urls greater than 10000000
df_urls = df_urls[df_urls['DocID'] >= 10000000]

#iterate through urls and extract content 
pages = []
test_count = 0
for index, row in df_urls.iterrows():
    url = row['URL']
    docid = row['DocID']
    pdf_pages = utils.extract_pdf_content(url, 
                                          docid, 
                                          start_condition="Filing Date:", 
                                          end_condition1="For the complete list",
                                          end_condition2="None disclosed")
    #some of these are cases where they have assets, but the end marker occurs on the following page. 
    #running through each page indivudally will ensure only pages with assets/liabilites are sent to OpenAI
    for page in pdf_pages:
        if '$' in page['page_content']: 
            pages.append(page)
    # test_count += 1
    # if test_count > 10:
    #     break

#convert list of dictionaries to pandas dataframe
df_pages = pd.DataFrame(pages)

#save dataframe to csv
df_pages.to_csv(f'{output_dir}/asset_pages.csv', index=False)
