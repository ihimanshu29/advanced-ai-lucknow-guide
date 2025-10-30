import logging
import requests
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.tools.retriever import create_retriever_tool
from langchain.tools import Tool
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_agent_executor():
    """
    Creates and returns a LangChain AgentExecutor using Groq and Hugging Face.
    This is the core "brain" of the application.
    """
    logging.info("--- Initializing Agent Logic ---")

    # 1. Initialize LLM
    llm = ChatGroq(model_name="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0.5)
    
    # 2. Setup RAG Knowledge Base
    try:
        food_loader = TextLoader("./knowledge_base/lucknow_food.txt")
        history_loader = TextLoader("./knowledge_base/lucknow_history.txt")
        documents = food_loader.load() + history_loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        logging.info("Vector store created successfully.")
    except Exception as e:
        logging.error(f"Failed to create vector store: {e}")
        return None

    # 3. Define Tools
    
    # Tool 1: RAG Retriever for Lucknow Info
    retriever_tool = create_retriever_tool(
        retriever,
        "lucknow_knowledge_base",
        "Use this tool for questions about Lucknow's history, food, culture, monuments, and attractions. It is your primary source for building itineraries."
    )
    
    # Tool 2: Weather Tool
    def get_weather(city: str = "Lucknow") -> str:
        """Fetches real-time weather for Lucknow, India."""
        latitude, longitude = 26.8467, 80.9462
        BASE_URL = "https://api.open-meteo.com/v1/forecast"
        params = {"latitude": latitude, "longitude": longitude, "current_weather": "true"}
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json().get('current_weather', {})
            return (f"The current temperature in Lucknow is {data.get('temperature', 'N/A')}°C "
                    f"with a wind speed of {data.get('windspeed', 'N/A')} km/h.")
        except requests.exceptions.RequestException as e:
            return f"Failed to retrieve weather data: {e}"

    weather_tool = Tool(
        name="get_weather",
        func=get_weather,
        description="Use this tool to get the current, real-time weather in Lucknow, India."
    )

    tools = [retriever_tool, weather_tool]

    # 4. Create the Agent Prompt (Updated for Itinerary Planning)
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a world-class AI travel planner specializing in Lucknow. Your goal is to create personalized, detailed itineraries for users. "
            "You have two tools:\n"
            "1. `lucknow_knowledge_base`: Your primary source for historical sites, food places, cultural spots, and activity recommendations.\n"
            "2. `get_weather`: To check the current weather conditions.\n\n"
            "When a user asks for a travel plan, follow these steps:\n"
            "1. Use the `lucknow_knowledge_base` to find relevant attractions, restaurants, and activities that match the user's request (e.g., 'heritage trip', 'food lover').\n"
            "2. Structure the output as a clear, day-by-day itinerary. For each day, suggest morning, afternoon, and evening activities.\n"
            "3. For each suggested place, provide a brief, engaging description.\n"
            "4. Check the current weather using the `get_weather` tool and add a practical tip to the itinerary, like 'Weather will be warm, carry light clothes.'\n"
            "5. If a query is unsafe or completely irrelevant to Lucknow travel, politely decline to answer."
        )),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 5. Create the Agent
    agent = create_tool_calling_agent(llm, tools, agent_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    return agent_executor