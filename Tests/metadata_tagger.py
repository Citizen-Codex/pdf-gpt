from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.document_transformers.openai_functions import create_metadata_tagger
from langchain.document_loaders import PyPDFLoader
import os

from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

loader = PyPDFLoader('Tests/test.pdf')
document = loader.load()

# create schema with name and assets
from typing import Literal
from pydantic import BaseModel, Field
from typing import List
from langchain.prompts import ChatPromptTemplate
import json

class Properties(BaseModel):
    Name: str
    Assets: List[str] = Field(description="List of assets.")

# Must be an OpenAI model that supports functions
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")

prompt = ChatPromptTemplate.from_template(
    """Extract relevant information from the table under section A: A.
{input}
"""
)

document_transformer = create_metadata_tagger(metadata_schema=Properties, llm=llm, prompt=prompt)

enhanced_documents = document_transformer.transform_documents(document)

print(
    *[d.page_content + "\n\n" + json.dumps(d.metadata) for d in enhanced_documents],
    sep="\n\n---------------\n\n"
)
