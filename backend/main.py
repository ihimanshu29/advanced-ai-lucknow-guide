from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from agent_logic import get_agent_executor
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Lucknow Tour Guide API",
    description="API for the AI-powered Lucknow travel planner.",
    version="1.0.0"
)

# Initialize the agent once when the server starts
agent_executor = get_agent_executor()

class QueryRequest(BaseModel):
    """Request model for user queries."""
    query: str

class QueryResponse(BaseModel):
    """Response model for the agent's answer."""
    response: str

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Receives a user query, processes it with the LangChain agent,
    and returns the structured response.
    """
    if not agent_executor:
        return {"response": "Agent not initialized. Please check server logs."}
    
    try:
        # Invoke the agent with the user's query
        result = agent_executor.invoke({"input": request.query})
        return {"response": result.get("output", "Sorry, I couldn't process that.")}
    except Exception as e:
        print(f"Error during agent invocation: {e}")
        return {"response": f"An error occurred: {e}"}

if __name__ == "__main__":
    # This allows you to run the server directly for testing
    uvicorn.run(app, host="0.0.0.0", port=8000)