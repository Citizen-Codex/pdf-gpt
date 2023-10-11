import pandas as pd
import json
import os

# load output/ files into dataframe
results = []
for filename in os.listdir('output/'):
    with open(f'output/{filename}') as f:
        print(filename)
        data = json.load(f)
        # check if Assets exists (if not, delete json file because should be empty)
        if 'Assets' not in data:
            #print filename
            print(f'No assets for: {filename}')
            # delete json file 
            os.remove(f'output/{filename}')
        # make data in Assets and Liabilites into lists if they are not already
        else: 
            if type(data['Assets']) != list:
                data['Assets'] = [data['Assets']]
            results.append(data)

# transform json data objects into dataframe
assets_df = pd.json_normalize(results, record_path=['Assets'], meta=['Name', 'URL'])

#remove brackets "[" "]" from Asset Type
assets_df['Asset Type'] = assets_df['Asset Type'].str.replace('[', '')
assets_df['Asset Type'] = assets_df['Asset Type'].str.replace(']', '')

liabilities_df = pd.json_normalize(results, record_path=['Liabilites'], meta=['Name', 'URL'])
