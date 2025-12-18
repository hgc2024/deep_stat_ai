from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

def get_coder_chain():
    # Initialize the LLM with the SOTA coding model
    llm = ChatOllama(model="qwen2.5-coder:7b-instruct", temperature=0)
    
    # Define the Prompt Template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Python Data Scientist specialized in Pandas and DuckDB.
        Your goal is to write a script to answer the question below.
        
        DATABASE: 'nba.duckdb'
        TABLES (ONLY USE THESE):
        - games (GAME_ID, SEASON, HOME_TEAM_WINS, PTS_home, PTS_away)
        - game_stats (GAME_ID, TEAM_ID, PLAYER_NAME, PTS, REB, AST, STL, BLK, DREB, PF, MIN, PLUS_MINUS, FG_PCT, FG3_PCT, FT_PCT)
          * **CRITICAL**: No `SEASON` column here. JOIN with `games` on `GAME_ID`.
        - teams (TEAM_ID, ABBREVIATION, NICKNAME, CITY)
        
        STRICT RULES:
        1. **NO HALLUCINATIONS**: DO NOT USE `WIN_SHARES`, `DRAFT_YEAR`, `ROOKIE_STATUS`. They do not exist.
        2. **STRICT SCHEMA**: If a column is not above, it does not exist.
        3. **SQL JOIN**: Always join `games` to filter by `SEASON`.
        4. **EXECUTION**: Use `con.execute(query).df()` and `print(df)`.
        5. **Print**: Use `print(df)` to show the result.
        6. **Cast Numpy Types**: DuckDB fails on `numpy.int64`. ALWAYS cast to `int()` or `float()` before using in SQL.
        7. **Use Aliases**: ALWAYS use table aliases (e.g. `game_stats gs`). Select `gs.PTS`, not `PTS`.
        
        Example Pattern 1 (Championship):
        ```python
        import duckdb
        con = duckdb.connect('nba.duckdb')
        
        # Q: Who won the 2016 Championship? (Logic: Winner of last playoff game)
        query = \"\"\"
            SELECT t.NICKNAME, t.CITY
            FROM games g
            JOIN teams t ON (
                CASE WHEN g.HOME_TEAM_WINS = 1 THEN g.HOME_TEAM_ID ELSE g.VISITOR_TEAM_ID END = t.TEAM_ID
            )
            WHERE g.SEASON = 2016 
              AND cast(g.GAME_ID as VARCHAR) LIKE '4%' -- Playoffs
            ORDER BY g.GAME_ID DESC -- The game with Max ID is the Finals clincher
            LIMIT 1
        \"\"\"
        df = con.execute(query).df()
        print(df)
        ```
        
        Example Pattern 2 (Comparison):
        ```python
        # Q: Compare LeBron and Curry
        query = \"\"\"
            SELECT gs.PLAYER_NAME, 
                   COUNT(DISTINCT gs.GAME_ID) as GP,
                   SUM(gs.PTS) as Total_Points,
                   AVG(gs.PTS) as PPG
            FROM game_stats gs
            WHERE gs.PLAYER_NAME IN ('LeBron James', 'Stephen Curry')
            GROUP BY gs.PLAYER_NAME
            ORDER BY Total_Points DESC
        \"\"\"
        df = con.execute(query).df()
        print(df)
        ```
        """),
        ("user", "Plan: {plan}\n\nQuestion: {question}")
    ])
    
    return prompt | llm | StrOutputParser()
