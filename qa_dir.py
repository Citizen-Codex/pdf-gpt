import os
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
import pandas as pd
from langchain.chat_models import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# load and split pdfs from directory
pdf_dir = 'pdf_dir'
loader = PyPDFDirectoryLoader(pdf_dir)
loaders = loader.load_and_split()

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

vectorstore = Chroma.from_documents(documents=loaders, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

question = "What are the assets for Colin Allred as listed under table A? Take your time."
docs = vectorstore.similarity_search(question)
len(docs)

from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate

template = """Do not include any explanations, only provide a RFC8259 compliant JSON response. 
{context}
Question: {question}
Helpful Answer:"""


rag_prompt_custom = PromptTemplate.from_template(template)

#issue seems to be with the retriever. It's pulling up assets for the wrong person
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()} 
    | rag_prompt_custom 
    | llm 
)

output = rag_chain.invoke("List assets for asset names and values for each individual. Include name of individual in json response.")

print(output.content)
