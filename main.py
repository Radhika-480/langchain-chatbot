import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from tools import add_contract_tool  # your custom tool
from jose import jwt, JWTError

# Load .env
load_dotenv()

# Constants
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# FastAPI app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    query: str

# Token decode utility
def decode_token_and_get_ids(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise ValueError("Authorization header missing")
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("store_id"), payload.get("org_id")
    except JWTError as e:
        raise ValueError(f"Token decode error: {e}")

# Set Gemini API key
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("Google API key not found in .env file!")
os.environ["GOOGLE_API_KEY"] = google_api_key

# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=1024
)

# Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that manages vendor contracts."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# Tools
tools = [add_contract_tool]

# LangChain agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    prompt=prompt,
    memory=memory,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# POST /chatbot endpoint
# @app.post("/chatbot")
# async def chatbot(req: ChatRequest, request: Request):
#     try:
#         # Get store/org ID from token
#         store_id = "ST001"
#         org_id = "ORG001"

#         # Inject into user prompt
#         user_query = f"{req.query}\nStore ID: {store_id}, Org ID: {org_id}"

#         # Run agent

#         result = agent.run(user_query)
#         return {"response": result}
#     except Exception as e:
#         return {"error": str(e)}

@app.post("/chatbot")
async def chatbot(req: ChatRequest, request: Request):
    try:
        # Get store/org ID from token
        store_id = "ST001"  # Replace with actual logic to extract from token
        org_id = "ORG001"   # Replace with actual logic to extract from token

        # Inject into user prompt
        user_query = f"{req.query}\nStore ID: {store_id}, Org ID: {org_id}"

        # Prepare the contents in the correct format for Gemini
        contents = {
            "input": user_query  # Use 'input' key instead of 'contents' or 'query'
        }

        # Run agent (now passing the correctly structured content)
        result = agent.run(contents)

        return {"response": result}
    except Exception as e:
        return {"error": str(e)}

# import os
# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from fastapi.middleware.cors import CORSMiddleware
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.memory import ConversationBufferMemory
# from langchain.agents import initialize_agent, AgentType
# from tools import add_contract_tool
# from jose import jwt, JWTError

# # Load environment variables
# load_dotenv()

# # Constants
# SECRET_KEY = "your-secret-key"
# ALGORITHM = "HS256"

# # FastAPI app
# app = FastAPI()

# # CORS setup
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Input model
# class ChatRequest(BaseModel):
#     input: str  # changed from `query` to `input`

# # Token utility
# def decode_token_and_get_ids(request: Request):
#     auth_header = request.headers.get("Authorization")
#     if not auth_header:
#         raise ValueError("Authorization header missing")
#     try:
#         token = auth_header.split(" ")[1]
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload.get("store_id"), payload.get("org_id")
#     except JWTError as e:
#         raise ValueError(f"Token decode error: {e}")

# # Google API key
# google_api_key = os.getenv("GOOGLE_API_KEY")
# if not google_api_key:
#     raise ValueError("Google API key not found in .env file!")
# os.environ["GOOGLE_API_KEY"] = google_api_key

# # Initialize Gemini LLM
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     temperature=0.7,
#     max_tokens=1024
# )

# # Conversation memory
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# # Prompt template
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful assistant that manages vendor contracts."),
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("human", "{input}")
# ])

# # Tools
# tools = [add_contract_tool]

# # Agent
# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     prompt=prompt,
#     memory=memory,
#     agent=AgentType.OPENAI_FUNCTIONS,
#     verbose=True
# )

# # Route
# @app.post("/chatbot")
# async def chatbot(req: ChatRequest, request: Request):
#     try:
#         store_id, org_id = decode_token_and_get_ids(request)

#         user_query = f"{req.input}\nStore ID: {store_id}, Org ID: {org_id}"

#         result = agent.run(user_query)
#         return {"response": result}
#     except Exception as e:
#         return {"error": str(e)}
