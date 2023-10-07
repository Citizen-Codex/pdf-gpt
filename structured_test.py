from langchain.document_loaders import PyPDFLoader
import os
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Define a new Pydantic model with field descriptions and tailored for Twitter.
class assets(BaseModel):
    name: str = Field(description="Name on pdf.")
    assets: str = Field(description="list of assets.")
    min_amount: str = Field(description="min amount for each asset.")
    max_amount: str = Field(description="max amount for each asset.")


parser = PydanticOutputParser(pydantic_object=assets)

chat_model = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=1000
)

# Update the prompt to match the new query and desired format.
prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(
            "answer the users question as best as possible.\n{format_instructions}\n{question}"
        )
    ],
    input_variables=["question"],
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
    },
)


loader = PyPDFLoader("https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2022/10053968.pdf")
document = loader.load()

document_query = "Create a description of assets based on Schedule A in this pdf: " + document[0].page_content

_input = prompt.format_prompt(question=document_query)
output = chat_model(_input.to_messages())
parsed = parser.parse(output.content)

