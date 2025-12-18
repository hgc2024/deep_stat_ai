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
        
        DATA SCHEMA (ONLY USE THESE COLUMNS):
        1. games (GAME_ID, GAME_DATE_EST, HOME_TEAM_ID, VISITOR_TEAM_ID, SEASON, HOME_TEAM_WINS, PTS_home, PTS_away)
           - `SEASON` is ONLY here.
        2. game_stats (GAME_ID, TEAM_ID, TEAM_CITY, PLAYER_NAME, PTS, REB, AST, STL, BLK, DREB, PF, MIN, PLUS_MINUS, FG_PCT, FG3_PCT, FT_PCT)
           - NO `SEASON` here. Join with `games`.
        3. teams (TEAM_ID, ABBREVIATION, NICKNAME, CITY)
        
        CRITICAL: DO NOT USE `WIN_SHARES`, `DRAFT_YEAR`, `ROOKIE_STATUS`. THEY DO NOT EXIST.
        
        INSTRUCTIONS:
        1. Identify Core Tables.
        2. Specify Filters (e.g., SEASON=2016).
           - **GLOBAL SEARCH**: If no season is specified, do NOT filter by `SEASON`. Instead, `GROUP BY PLAYER_NAME, SEASON` to find the best instances in history.
        3. Specify Merge Logic (e.g., gs.GAME_ID = g.GAME_ID).
        4. **DERIVED TIME ATTRIBUTES**:
           - "Rookie" / "Debut" / "First Season" -> Calculate `MIN(SEASON)` per player.
           - "Retirement" / "Final Season" -> Calculate `MAX(SEASON)` per player.
           - You MUST instruct the Coder to compute these per player if not provided.
        5. Specify Aggregation (e.g., SUM(PTS)).
        6. Provide a broad perspective for "best" or "greatest" queries.
        
        Example Input: "Who won the 2008 Championship?"
        Example Output: 
        1. Load 'games' table (Filter: SEASON=2007 because user means June 2008 Finals, Playoffs).
        2. Order by GAME_ID DESC and LIMIT 1 to find the last game (The Finals).
        3. Identify the winner using 'HOME_TEAM_WINS'.
        4. Join with 'teams' table to get the Team Name.
        
        Example Input: "Who is the best defender in history?"
        Example Output:
        1. Load 'game_stats'.
        2. Group By PLAYER_NAME.
        3. Calculate Aggregates: SUM(STL) as Total_Steals, SUM(BLK) as Total_Blocks.
        4. Order by (Total_Steals + Total_Blocks) DESC.
        5. Select TOP 10 to provide a broad perspective.
        """),
        ("user", "{question}")
    ])
    
    return prompt | llm | StrOutputParser()
