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
           - **CHAMPIONSHIP**: The winner of the Playoff game with the MAX(GAME_ID) is the Season Champion.
           - **SEASONS**: Data uses Start Year. (e.g. 2015-16 Season is `SEASON=2015`).
             - "2016 Championship" -> June 2016 -> `SEASON=2015`.
             - "2016 Season" -> Ambiguous, usually means 2016-17 (`SEASON=2016`). Default to Title Year logic if strictly asking "Who won".
        2. game_stats (GAME_ID, TEAM_ID, TEAM_CITY, PLAYER_NAME, PTS, REB, AST, MIN)
        3. teams (TEAM_ID, ABBREVIATION, NICKNAME, CITY)
        
        INSTRUCTIONS:
        1. Identify the Core Tables needed.
        2. Specify the Filters (Season=2016, Player='Curry').
        3. Specify the Merge Logic (e.g., "Merge games and stats on GAME_ID").
        4. Specify the Aggregation logic (e.g., "Sum PTS grouped by Player").
        
        Example Input: "Who won the 2016 Championship?"
        Example Output: 
        1. Load 'games' table (Filter: SEASON=2015 because user means June 2016 Finals, Playoffs).
        2. Order by GAME_ID DESC and LIMIT 1 to find the last game (The Finals).
        3. Identify the winner using 'HOME_TEAM_WINS'.
        4. Join with 'teams' table to get the Team Name.
        """),
        ("user", "{question}")
    ])
    
    return prompt | llm | StrOutputParser()
