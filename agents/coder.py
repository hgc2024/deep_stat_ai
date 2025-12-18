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
        4. **SAFE MIN PARSING**: `MIN` contains dirty data like strings. ALWAYS use this pattern to parse minutes:
           - `CAST(CASE WHEN MIN LIKE '%:%' THEN SPLIT_PART(MIN, ':', 1) ELSE '0' END AS INTEGER)`
        5. **EXECUTION**: Use `con.execute(query).df()` and `print(df)`.
        6. **Print**: Use `print(df)` to show the result.
        6. **Cast Numpy Types**: DuckDB fails on `numpy.int64`. ALWAYS cast to `int()` or `float()` before using in SQL.
        7. **Use Aliases**: ALWAYS use table aliases (e.g. `game_stats gs`). Select `gs.PTS`, not `PTS`.
        
        Example Pattern 1 (Global/Historical Best - No Specific Year):
        ```python
        # Q: Best Scoring Season in History (All Time)
        query = \"\"\"
            SELECT gs.PLAYER_NAME, 
                   g.SEASON,
                   SUM(gs.PTS) as Total_Points,
                   AVG(gs.PTS) as PPG
            FROM game_stats gs
            JOIN games g ON gs.GAME_ID = g.GAME_ID
            GROUP BY gs.PLAYER_NAME, g.SEASON
            ORDER BY Total_Points DESC
            LIMIT 10
        \"\"\"
        df = con.execute(query).df()
        print(df)
        ```
        ```python
        # Q: Who had the best carry job? (Best Playoff vs Reg Season improvement)
        query = \"\"\"
            WITH reg_season AS (
                SELECT gs.PLAYER_NAME, AVG(gs.PTS) as Reg_PPG
                FROM game_stats gs JOIN games g ON gs.GAME_ID = g.GAME_ID
                WHERE CAST(g.GAME_ID AS VARCHAR) LIKE '2%'
                GROUP BY gs.PLAYER_NAME
            ),
            playoffs AS (
                SELECT gs.PLAYER_NAME, AVG(gs.PTS) as Playoff_PPG, COUNT(DISTINCT gs.GAME_ID) as Games
                FROM game_stats gs JOIN games g ON gs.GAME_ID = g.GAME_ID
                WHERE CAST(g.GAME_ID AS VARCHAR) LIKE '4%'
                GROUP BY gs.PLAYER_NAME
            )
            SELECT p.PLAYER_NAME, 
                   r.Reg_PPG, 
                   p.Playoff_PPG, 
                   (p.Playoff_PPG - r.Reg_PPG) as Elevation
            FROM playoffs p
            JOIN reg_season r ON p.PLAYER_NAME = r.PLAYER_NAME
            WHERE p.Games > 10 -- Minimum sample size
            ORDER BY Elevation DESC
            LIMIT 10
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

        Example Pattern 3 (Derived Time Attributes - Rookie/Retirement):
        ```python
        # Q: Best Rookie Seasons (First Season)
        query = \"\"\"
            WITH player_milestones AS (
                SELECT gs.PLAYER_NAME, 
                       MIN(g.SEASON) as Rookie_Season,
                       MAX(g.SEASON) as Final_Season
                FROM game_stats gs
                JOIN games g ON gs.GAME_ID = g.GAME_ID
                GROUP BY gs.PLAYER_NAME
            )
            SELECT gs.PLAYER_NAME, 
                   mil.Rookie_Season as Season,
                   SUM(gs.PTS) as Rookie_Points
            FROM game_stats gs
            JOIN games g ON gs.GAME_ID = g.GAME_ID
            JOIN player_milestones mil ON gs.PLAYER_NAME = mil.PLAYER_NAME 
                                      AND g.SEASON = mil.Rookie_Season -- Filter for FIRST season
            GROUP BY gs.PLAYER_NAME, mil.Rookie_Season
            ORDER BY Rookie_Points DESC
            LIMIT 10
        \"\"\"
        df = con.execute(query).df()
        print(df)
        ```
        """),
        ("user", "Plan: {plan}\n\nQuestion: {question}")
    ])
    
    return prompt | llm | StrOutputParser()
