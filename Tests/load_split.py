import os
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.indexes import VectorstoreIndexCreator

from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# OnlinePDFLoader and UnstructuredPDFLoader broken since Pythono 3.9, would need to revert
loader = UnstructuredPDFLoader("test.pdf")
loaders = [loader]

# create index from loaders
index = VectorstoreIndexCreator().from_loaders(loaders)

# query index
query = "Look through each page of the pdf and list all assets in the table schedule A and the min and max value for each asset."
result = index.query(query)
