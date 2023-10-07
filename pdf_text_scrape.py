import PyPDF2
import re
import pandas as pd

# Replace this with the path to your PDF file
pdf_file_path = 'https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2022/10053968.pdf'

# read and extract text from url of pdf
import requests
import io

r = requests.get(pdf_file_path)
f = io.BytesIO(r.content)
pdf_reader = PyPDF2.PdfReader(f)
    
# Initialize a string to store extracted text
extracted_text = ''

# Loop through each page in the PDF
for page_number in range(len(pdf_reader.pages)):
    page = pdf_reader.pages[page_number]
    extracted_text += page.extract_text()

# Print the extracted text
print(extracted_text)

#locating the text between the two strings
start = '$1,000?'
end = '* For'
assets_text = extracted_text[extracted_text.find(start)+len(start):extracted_text.rfind(end)].replace('\n', ' ') #removing line breaks helps with regex for values

#locate name 
name_start = 'Name: '
name_end = '\nStatus'
name = extracted_text[extracted_text.find(name_start)+len(name_start):extracted_text.rfind(name_end)]

# Define a regular expression pattern to capture the values
pattern = r'\[(.*?)\]\s*(\$[\d,]+ - \$[\d,]+)'

# Find all matches using the pattern
matches = re.findall(pattern, assets_text)

# Initialize lists to store extracted data
values_in_brackets = []
lower_estimates = []
upper_estimates = []

# Extracted values
for match in matches:
    value_in_brackets = match[0]
    value_with_currency = match[1]
    
    # Split the value_with_currency based on the dash "-"
    lower_estimate, upper_estimate = value_with_currency.split(' - ')
    
    values_in_brackets.append(value_in_brackets)
    lower_estimates.append(lower_estimate)
    upper_estimates.append(upper_estimate)

# Create a pandas DataFrame from the extracted data
df = pd.DataFrame({
    'Name': name,
    'Asset Type': values_in_brackets,
    'Lower Estimate': lower_estimates,
    'Upper Estimate': upper_estimates
})

# Print the resulting DataFrame
print(df)

# Save the DataFrame to a excel file
df.to_excel('output.xlsx', index=False)
