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
        TABLES (Exact Columns):
        - games (GAME_ID, GAME_DATE_EST, HOME_TEAM_ID, VISITOR_TEAM_ID, SEASON, HOME_TEAM_WINS, PTS_home, PTS_away)
          * **PLAYOFFS**: filter where `cast(GAME_ID as VARCHAR) LIKE '4%'`
          * **REGULAR SEASON**: filter where `cast(GAME_ID as VARCHAR) LIKE '2%'`
          * `GAME_TYPE` column DOES NOT EXIST. Do not use it.
        - game_stats (GAME_ID, TEAM_ID, TEAM_CITY, PLAYER_NAME, PTS, REB, AST, MIN)
        - teams (TEAM_ID, ABBREVIATION, NICKNAME, CITY)
        
        GUIDELINES:
        1. **USE SQL FOR LOGIC**: Perform all filtering, joining, and aggregation inside the `con.execute("...")` query.
           - DuckDB is faster and safer than generating complex Pandas logic.
        2. **Load Final Result**: Only convert to `.df()` when you have the computed answer.
        3. **Print**: Use `print(df)` to show the result.
        4. **Cast Numpy Types**: DuckDB fails on `numpy.int64`. ALWAYS cast to `int()` or `float()` before using in SQL.
        5. **Use Aliases**: ALWAYS use table aliases (e.g. `game_stats gs`). Select `gs.PTS`, not `PTS`.
        
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
