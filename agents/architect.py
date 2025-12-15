from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

# The Architect plans the analysis but does NOT write code.
# It identifies the Entities (Curry, Warriors) and the Metrics (PTS, REB).

def get_architect_chain():
    llm = ChatOllama(model="qwen2.5-coder:7b-instruct", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Data Architect for an NBA Analytics Engine.
        Your goal is to translate a natural language question into a LOGICAL PLAN for a Python Coder (who uses Pandas).
        
        DATA SCHEMA (Exact Columns):
        1. games (GAME_ID, GAME_DATE_EST, HOME_TEAM_ID, VISITOR_TEAM_ID, SEASON, HOME_TEAM_WINS, PTS_home, PTS_away)
           - **IMPORTANT**: To filter for PLAYOFFS, check if `GAME_ID` starts with '4' (e.g. `CAST(GAME_ID AS VARCHAR) LIKE '4%'`).
           - Regular Season GAME_IDs start with '2'. Preseason with '1'.
        2. game_stats (GAME_ID, TEAM_ID, TEAM_CITY, PLAYER_NAME, PTS, REB, AST, MIN)
        3. teams (TEAM_ID, ABBREVIATION, NICKNAME, CITY)
        
        INSTRUCTIONS:
        1. Identify the Core Tables needed.
        2. Specify the Filters (Season=2016, Player='Curry').
        3. Specify the Merge Logic (e.g., "Merge games and stats on GAME_ID").
        4. Specify the Aggregation logic (e.g., "Sum PTS grouped by Player").
        
        Example Input: "Who had the most points in a playoff game in 2016?"
        Example Output: 
        1. Load 'games' table and filter for SEASON=2016 AND `CAST(GAME_ID AS VARCHAR) LIKE '4%'` (Playoffs).
        2. Load 'game_stats' table.
        3. Merge 'games' and 'game_stats' on GAME_ID.
        4. Sort by PTS descending.
        5. Print the top row (Player Name + PTS).
        """),
        ("user", "{question}")
    ])
    
    return prompt | llm | StrOutputParser()
