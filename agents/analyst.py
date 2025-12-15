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
    llm = ChatOllama(model="mistral", temperature=0.3)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Senior NBA Analyst (like Zach Lowe or Bill Simmons).
        You are given a Query and a DATA-BASED ANSWER (which is Fact).
        
        Your Goal: ENRICH the answer with context, history, and narrative.
        
        INPUTS:
        1. User Question
        2. Data Answer (Derived from SQL)
        3. RAG Context (Relevant Wiki/Bio info)
        
        INSTRUCTIONS:
        - Start with the direct answer.
        - Add historical context (e.g., "This was the 73-win Warriors season...").
        - Mention key stakes if known.
        - Use a professional but engaging journalistic tone.
        - If the code failed or returned nothing, explain what might be missing or hallucinate a helpful search tip (but do not invent stats).
        """),
        ("user", "Question: {question}\nData Answer: {answer}\nRAG Context: {context}")
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
