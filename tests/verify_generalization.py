import duckdb
import pandas as pd

def verify_carry_job_pattern():
    print("--- Verifying 'Carry Job' SQL Pattern ---")
    con = duckdb.connect('nba.duckdb')
    
    # This is the EXACT SQL pattern we added to coder.py
    query = """
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
               CAST(r.Reg_PPG as DECIMAL(10,1)) as Reg_PPG, 
               CAST(p.Playoff_PPG as DECIMAL(10,1)) as Playoff_PPG, 
               CAST(p.Playoff_PPG - r.Reg_PPG as DECIMAL(10,1)) as Elevation
        FROM playoffs p
        JOIN reg_season r ON p.PLAYER_NAME = r.PLAYER_NAME
        WHERE p.Games > 10 -- Minimum sample size
        ORDER BY Elevation DESC
        LIMIT 10
    """
    
    try:
        df = con.execute(query).df()
        print(df)
        
        # Validation checks
        if df.empty:
             print("❌ Failed: No results returned.")
             return

        top_player = df.iloc[0]['PLAYER_NAME']
        elevation = df.iloc[0]['Elevation']
        
        print(f"✅ Success: Query ran. Top carry job: {top_player} (+{elevation} PPG).")
        
    except Exception as e:
        print(f"❌ Failed with error: {e}")

if __name__ == "__main__":
    verify_carry_job_pattern()
