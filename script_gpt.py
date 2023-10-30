import pandas as pd
import utils

#read example string 
pdf_content = utils.extract_pdf_content(url='https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2022/10053116.pdf')

pdf_content_e = utils.edit_pdf_content(pdf_content,
                                       start_condition="Filing Date:",
                                       end_condition="For the complete list")

pdf_content[0]
pdf_content_e[0]

#read desired csv format
eg = pd.read_csv('output/csv_files/assets_10053968.csv')


#script provided. This does not work but does get somewhat close
import re
import csv

# Input data
data = pdf_content_e

# Step 1: Join the data to form a single string
joined_data = " ".join(data)

# Step 2: Split into lines
lines = joined_data.split("\n")

# Filtering out lines that are not relevant
lines = [line.strip() for line in lines if line.strip() and not line.startswith('Asset OwnerValue of Asset')]

# To store extracted assets
assets = []

for i, line in enumerate(lines):
    # Look for lines that seem to start with an asset description
    if re.search(r'\[\w+\]', line):
        asset = {
            'name': line.split('[')[0].strip(),
            'type_owner': re.search(r'\[\w+\]', line).group().strip('[]'),
            'min_val': 0.0,
            'max_val': 0.0,
            'income_type': None,
            'income_min': 0.0,
            'income_max': 0.0
        }
        
        # Value extraction (assuming value is in format like "$1,000 - $5,000")
        val_match = re.search(r'\$(\d+[,]*\d*)\s*-\s*\$(\d+[,]*\d*)', line)
        if val_match:
            asset['min_val'] = float(val_match.group(1).replace(',', ''))
            asset['max_val'] = float(val_match.group(2).replace(',', ''))

        # Income extraction
        if i+1 < len(lines) and ("$" in lines[i+1] or "None" in lines[i+1]):
            income_info = lines[i+1]
            asset['income_type'] = income_info.split('$')[0].strip()
            income_val_match = re.search(r'\$(\d+[,]*\d*)\s*-\s*\$(\d+[,]*\d*)', income_info)
            if income_val_match:
                asset['income_min'] = float(income_val_match.group(1).replace(',', ''))
                asset['income_max'] = float(income_val_match.group(2).replace(',', ''))

        assets.append(asset)

# Write to CSV
filename = "assets.csv"
with open(filename, 'w', newline='') as csvfile:
    fieldnames = ['Asset Name', 'Minimum value', 'Maximum value', 'Income Type', 'Income Minimum', 'Income Maximum', 'Asset Type and Owner', 'URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    url = "https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2022/10053968.pdf"
    for idx, asset in enumerate(assets):
        writer.writerow({
            'Asset Name': asset['name'],
            'Minimum value': asset['min_val'],
            'Maximum value': asset['max_val'],
            'Income Type': asset['income_type'],
            'Income Minimum': asset['income_min'],
            'Income Maximum': asset['income_max'],
            'Asset Type and Owner': asset['type_owner'],
            'URL': url
        })

print(f"Data written to {filename}")
