




import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from tools import add_contract_tool
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
    allow_origins=["*"],
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

# Gemini LLM with tools
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=1024
)

# Simple in-memory conversation history
conversation_history = []

# Tools
tools = [add_contract_tool]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# Prompt template - Simplified for direct tool calling
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that manages vendor contracts. 
    You have access to tools to help users create and manage vendor contracts.
    When a user wants to add a contract, use the add_contract_tool with the provided information.
    Always ask for missing required information before proceeding.
    
    Be conversational and helpful. If the user provides contract information, 
    extract the relevant details and use the add_contract_tool to create the contract."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

def process_tool_calls(ai_message):
    """Process tool calls from AI message and return results"""
    if hasattr(ai_message, 'tool_calls') and ai_message.tool_calls:
        results = []
        for tool_call in ai_message.tool_calls:
            if tool_call['name'] == 'add_contract_tool':
                try:
                    # Call the tool function directly
                    result = add_contract_tool.invoke(tool_call['args'])
                    results.append(result)
                except Exception as e:
                    results.append(f"Error calling tool: {str(e)}")
        return results
    return []

@app.post("/chatbot")
async def chatbot(req: ChatRequest, request: Request):
    try:
        global conversation_history  # Add this line to access global variable
        
        # Get store/org ID from token (or use defaults)
        store_id = "ST001"  # Replace with actual logic to extract from token
        org_id = "ORG001"   # Replace with actual logic to extract from token

        # Add store_id and org_id to the user query
        user_input = f"{req.query}\nStore ID: {store_id}, Org ID: {org_id}"
        
        # Add user message to history
        conversation_history.append(HumanMessage(content=user_input))
        
        # Invoke the chain
        ai_message = llm_with_tools.invoke(
            prompt.format_messages(
                input=user_input,
                chat_history=conversation_history[:-1]  # Exclude current message
            )
        )
        
        # Process any tool calls
        tool_results = process_tool_calls(ai_message)
        
        # If tools were called, get a final response
        if tool_results:
            # Add tool results to conversation and get final response
            tool_context = f"Tool results: {'; '.join(tool_results)}"
            final_message = llm.invoke(
                prompt.format_messages(
                    input=f"{user_input}\n\nTool results: {tool_context}\n\nProvide a helpful response based on the tool results.",
                    chat_history=conversation_history[:-1]
                )
            )
            response = final_message.content
        else:
            response = ai_message.content
        
        # Add AI response to history
        conversation_history.append(AIMessage(content=response))
        
        # Keep history manageable (last 20 messages)
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]

        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)