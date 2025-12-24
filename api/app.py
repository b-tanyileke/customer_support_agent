"""
FastAPI application for the support agent
"""

# Import necessary libraries
from fastapi import FastAPI
from pydantic import BaseModel
from agent.support_agent import handle_query

# Initialize FastAPI app
app = FastAPI(title="Enterprise AI Support Agent")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    response: str


@app.post("/query", response_model=QueryResponse)
def query_agent(request: QueryRequest):
    """
    Docstring for query_agent
    
    :param request: User question
    :type request: QueryRequest
    """
    answer = handle_query(request.question)
    return QueryResponse(response=answer)
