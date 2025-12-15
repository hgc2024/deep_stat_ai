from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb
import os

# Initialize Vector DB Client
CHROMA_PATH = "nba_chroma"
client = chromadb.PersistentClient(path=CHROMA_PATH)

def get_context_analyst():
    """
    Returns a chain that adds "Color Commentary" and "Context" to the raw SQL data.
    """
    llm = ChatOllama(model="qwen2.5-coder:7b-instruct", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Senior NBA Sports Journalist (like Zach Lowe).
        You will receive a RAW DATA snippet and RAG CONTEXT.
        
        YOUR GOAL: Write a compelling, 1-paragraph narrative answer.
        
        RULES:
        1. **STORYTELLING FIRST**: You are a journalist. Start with a hook. (e.g., "In a historic Game 7...")
        2. **SEASON LOGIC**: Data `SEASON=X` usually means `Year X+1 Finals`. (e.g. 2015 -> 2016 Finals). Check the RAG context to confirm the year.
        3. **Combined Knowledge**: Use the RAG info to flesh out the "Why".
        
        NEGATIVE CONSTRAINTS (CRITICAL):
        - **DO NOT OUTPUT TABLES**.
        - **DO NOT OUTPUT DATAFRAMES**.
        - **DO NOT START WITH "Based on the data..."**.
        - **NO HALLUCINATIONS**: Do not invent games (e.g. 2023) if not in data.
        - If the input is a table row "Cleveland", your output must be a SENTENCE "The Cleveland Cavaliers...".
        
        INPUTS:
        - Question: {question}
        - Raw Data: {answer}
        - RAG Context: {context}
        """),
        ("user", "Explain this result to the user.")
    ])
    
    return prompt | llm | StrOutputParser()

def retrieve_rag_context(query: str, n_results=3):
    """
    Simple retrieval from ChromaDB to find relevant Players/Teams.
    """
    context_str = ""
    try:
        # Search Players
        p_coll = client.get_collection("nba_players")
        p_results = p_coll.query(query_texts=[query], n_results=n_results)
        if p_results['documents']:
            context_str += "Relevant Players: " + ", ".join(p_results['documents'][0]) + "\n"
            
        # Search Teams
        t_coll = client.get_collection("nba_teams")
        t_results = t_coll.query(query_texts=[query], n_results=n_results)
        if t_results['documents']:
             context_str += "Relevant Teams: " + ", ".join(t_results['documents'][0]) + "\n"
             
    except Exception as e:
        print(f"RAG Error: {e}")
        
    return context_str
