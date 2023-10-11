# pdf-gpt
Question PDF documents using AI

Currently, this code works as a sandox to try out new ideas with scraping data from pdfs. The aim to extract structured json data from pdf ran into limitations from openai tokens limits. Eventually OpenAI will release a 32k token gpt-4 model that will work better for this type of work. One of the issues is that a full report of a congress person's finances often requires sevel pages data, which seems to be too much for gpt-4 to handle.

This project uses OpenAI and Langchain to allow users to ask questions about groups of pdf documents. It was specifically developed to return information from financial disclosure forms of U.S. congress members in a pandas dataframe. Users should find code ammendable to a wide array of use cases. 

The project is maintained the team at Citizen Codex. 
