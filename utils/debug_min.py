import duckdb

def check_min_column():
    con = duckdb.connect('nba.duckdb')
    print("Checking for empty or invalid MIN values...")
    
    query = """
    SELECT MIN, COUNT(*) as Count
    FROM game_stats 
    WHERE MIN IS NULL 
       OR MIN = '' 
       OR NOT CAST(MIN AS VARCHAR) LIKE '%:%'
    GROUP BY MIN
    LIMIT 20;
    """
    
    df = con.execute(query).df()
    print(df)

if __name__ == "__main__":
    check_min_column()
