import duckdb
import io
import sys

def verify_rookie_logic():
    # Capture stdout
    stdout_capture = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = stdout_capture

    try:
        con = duckdb.connect('nba.duckdb')
        
        print("\n--- Testing 'Rookie Logic' (First Season) ---")
        
        # This query mimics the pattern we taught the Coder agent
        query = """
            WITH player_milestones AS (
                SELECT gs.PLAYER_NAME, 
                       MIN(g.SEASON) as Rookie_Season
                FROM game_stats gs
                JOIN games g ON gs.GAME_ID = g.GAME_ID
                GROUP BY gs.PLAYER_NAME
            )
            SELECT gs.PLAYER_NAME, 
                   mil.Rookie_Season,
                   SUM(gs.PTS) as Rookie_Points
            FROM game_stats gs
            JOIN games g ON gs.GAME_ID = g.GAME_ID
            JOIN player_milestones mil ON gs.PLAYER_NAME = mil.PLAYER_NAME 
                                      AND g.SEASON = mil.Rookie_Season
            WHERE gs.PLAYER_NAME = 'LeBron James'
            GROUP BY gs.PLAYER_NAME, mil.Rookie_Season
        """
        
        df = con.execute(query).df()
        print(df)
        
        if df.empty:
            print("❌ Verification Failed: No data found for LeBron James.")
            return

        points = df.iloc[0]['Rookie_Points']
        season = df.iloc[0]['Rookie_Season']
        
        # LeBron scored 1654 points in his rookie season (2003-04)
        # But our DB might be partial or have slight diffs. 
        # Crucially, it should be < 3000. If it's 40,000+, it failed to filter.
        if points > 4000:
            print(f"❌ Verification Failed: Points ({points}) indicate Careeer Total, not Rookie Season.")
        elif points < 100:
             print(f"❌ Verification Failed: Points ({points}) seems too low.")
        else:
            print(f"✅ Verification Success: LeBron Rookie Points = {points} (Season {season})")

    except Exception as e:
        print(f"❌ Verification Failed with Error: {e}")
    finally:
        # Restore stdout
        sys.stdout = original_stdout
    
    # Write to file
    with open('tests/test_rookie_output.txt', 'w', encoding='utf-8') as f:
        f.write(stdout_capture.getvalue())

if __name__ == "__main__":
    verify_rookie_logic()
