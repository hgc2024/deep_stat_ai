from pathlib import Path
import duckdb
import chromadb
import pandas as pd
import os
import sys

# Paths (Robust resolution)
SCRIPT_DIR = Path(__file__).resolve().parent # deep_stat_ai/utils
PROJECT_ROOT = SCRIPT_DIR.parent         # deep_stat_ai
REPO_ROOT = PROJECT_ROOT.parent          # sports_edit_ai

DATA_DIR = REPO_ROOT / "data" / "archive"
DB_PATH = str(PROJECT_ROOT / "nba.duckdb")
CHROMA_PATH = str(PROJECT_ROOT / "nba_chroma")

def init_duckdb():
    print("🦆 Initializing DuckDB...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    con = duckdb.connect(DB_PATH)
    
    # Load Tables
    files = {
        'games': 'games.csv',
        'game_stats': 'games_details.csv', 
        'players': 'players.csv',
        'teams': 'teams.csv',
        'ranking': 'ranking.csv'
    }
    
    for table, filename in files.items():
        csv_path = os.path.join(DATA_DIR, filename)
        print(f"   -> Loading {table} from {filename}...")
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{csv_path}')")
    
    print("   -> Creating Indexes...")
    con.execute("CREATE INDEX idx_game_id ON games(GAME_ID)")
    con.execute("CREATE INDEX idx_stats_game_id ON game_stats(GAME_ID)")
    con.execute("CREATE INDEX idx_stats_player ON game_stats(PLAYER_NAME)")
    con.close()
    print("✅ DuckDB Ready.")

def init_chroma():
    print("🦁 Initializing ChromaDB (Vector Store)...")
    # Using local embedding model (all-MiniLM-L6-v2 is default for Chroma/SentenceTransformers)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # 1. Players Collection (For fuzzy name lookup)
    try:
        client.delete_collection("nba_players")
    except: pass
    
    player_coll = client.create_collection("nba_players")
    
    # Deduplicate Players
    players_df = pd.read_csv(DATA_DIR / 'players.csv')
    players_df = players_df.drop_duplicates(subset=['PLAYER_ID'])
    print(f"   -> Embedding {len(players_df)} players...")
    
    # Prepare Batches
    ids = players_df['PLAYER_ID'].astype(str).tolist()
    documents = players_df['PLAYER_NAME'].fillna("Unknown").tolist()
    metadatas = [{'team_id': str(tid), 'season': str(s)} for tid, s in zip(players_df['TEAM_ID'], players_df['SEASON'])]
    
    # Batch add (Chroma limit is usually 5k-40k, safe to batch 500)
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        end = min(i+batch_size, len(ids))
        player_coll.add(
            ids=ids[i:end],
            documents=documents[i:end],
            metadatas=metadatas[i:end]
        )
        sys.stdout.write(f"\r      Processed {end}/{len(ids)}")
    print("\n✅ Players Embedded.")

    # 2. Teams Collection
    try:
        client.delete_collection("nba_teams")
    except: pass
    
    team_coll = client.create_collection("nba_teams")
    teams_df = pd.read_csv(DATA_DIR / 'teams.csv')
    teams_df = teams_df.drop_duplicates(subset=['TEAM_ID'])
    print(f"   -> Embedding {len(teams_df)} teams...")
    
    # Embed full text: "Atlanta Hawks (ATL) founded in 1949..."
    t_docs = []
    t_ids = teams_df['TEAM_ID'].astype(str).tolist()
    t_metas = []
    
    for _, row in teams_df.iterrows():
        text = f"{row['CITY']} {row['NICKNAME']} ({row['ABBREVIATION']}) founded {row['YEARFOUNDED']}. Arena: {row['ARENA']}."
        t_docs.append(text)
        t_metas.append({'abbrev': row['ABBREVIATION']})
        
    team_coll.add(ids=t_ids, documents=t_docs, metadatas=t_metas)
    print("✅ Teams Embedded.")

if __name__ == "__main__":
    init_duckdb()
    init_chroma()
