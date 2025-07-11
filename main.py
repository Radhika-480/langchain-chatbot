import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

# Get your Google API key
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("Google API key not found in .env file!")

# Set the API key in environment
os.environ["GOOGLE_API_KEY"] = google_api_key

# Initialize the Gemini model using langchain-google-genai
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # or "gemini-2.5-flash-preview-04-17"
    temperature=0.7,
    max_tokens=1024
)

# Optional prompt template for better chaining
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}")
])

# Build the prompt-chain
chain = prompt | llm

# CLI chatbot loop
print("🤖 Gemini Pro Chatbot (type 'exit' to quit):")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    try:
        response = chain.invoke({"input": user_input})
        print("Gemini:", response.content)
    except Exception as e:
        print("Error:", e)
