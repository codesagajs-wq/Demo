import os
import httpx
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()


MODEL = "azure_ai/genailab-maas-DeepSeek-V3-0324" 


def get_llm(model: str = MODEL) -> ChatOpenAI:
    client = httpx.Client(verify=False) 

    llm = ChatOpenAI(
        base_url="https://genailab.tcs.in",
        model=model,
        api_key=os.getenv("OPENAI_API_KEY"),
        http_client=client
    )
    return llm