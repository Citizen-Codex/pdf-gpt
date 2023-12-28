# pdf-gpt
Question PDF documents using AI

This project uses OpenAI and Langchain to allow users to ask questions about groups of pdf documents. It was specifically developed to return information from financial disclosure forms of U.S. congress members in a pandas dataframe. Users should find code ammendable to a wide array of use cases. 

The project is maintained by Citizen Codex. 

Areas we look to improve in the future: 
* Chunk text according to assets info. Don't allow page breaks to split up information about an individual asset
* The AI struggles to interpret both the word "None" and the number 0. It likes to look for the next number
* Implement a SQL database to write and manipulate data

Notes of inconsistency 
* The names of assets on page break may be truncated, e.g. simply saying SP 
* Asset types may not be able to be pulled for truncated asset names (only 200-300 of 15,000 assets)
* The AI sometimes will attach an income value to an asset with no value

How to repo works: 
* All scripts rely on functions from utils.py
* The script gen_pdf_urls.py uses metadata about financial disclosure submissions to create urls pointing towards the PDfs containing the data. This script matches each disclosue form with political information about a given congress member (e.g. their party, age, etc.). 
* The scripts beginning with extract_ comb through and extract the relevant pages from pdfs accessed via their urls.
* The scripts assets.py and liabilities.py send the extracted text to ChatGPT to be returned as structured json data.
* The script processing.py cleans the results of ChatGPT analyis and calculates the networth of congress members
