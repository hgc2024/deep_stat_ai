import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from agents.architect import get_architect_chain
from agents.coder import get_coder_chain

def test_sql_joins():
    question = "List some of the greatest rookie seasons in NBA history."
    
    print(f"Testing Question: {question}")
    
    architect = get_architect_chain()
    plan = architect.invoke({"question": question})
    print("\n--- ARCHITECT PLAN ---")
    print(plan)
    
    coder = get_coder_chain()
    code = coder.invoke({"plan": plan, "question": question})
    print("\n--- CODER CODE ---")
    print(code)
    
    # Check for correct join logic (case-insensitive, handles newlines)
    code_normalized = " ".join(code.upper().split())
    assert "JOIN GAMES" in code_normalized or "FROM GAMES" in code_normalized, "Code should include a join with the games table to determine seasons."
    assert "GS.GAME_ID = G.GAME_ID" in code_normalized or "GS.GAME_ID = GAMES.GAME_ID" in code_normalized or "GS.\"GAME_ID\" = G.\"GAME_ID\"" in code_normalized, "Code should include the join condition."
    
    # Check for hallucinated columns
    forbidden = ["WIN_SHARES", "DRAFT_YEAR", "ROOKIE_STATUS"]
    for f in forbidden:
        if f in code_normalized:
            print(f"Found forbidden column: {f}")
            assert f not in code_normalized, f"Code hallucinated non-existent column: {f}"
    
    print("\n✅ Verification Success: Code includes correct join logic and adheres to schema.")

if __name__ == "__main__":
    import io
    output_f = io.StringIO()
    # Capture all output in a string buffer
    old_stdout = sys.stdout
    sys.stdout = output_f
    try:
        test_sql_joins()
        res = output_f.getvalue()
        with open("tests/test_output.txt", "w", encoding="utf-8") as f:
            f.write(res)
    except Exception as e:
        sys.stdout = old_stdout # Restore stdout to print error to terminal
        print(f"\n❌ Verification Failed: {e}")
        res = output_f.getvalue()
        with open("tests/test_output.txt", "w", encoding="utf-8") as f:
            f.write(res)
            f.write(f"\n❌ Verification Failed: {e}")
        sys.exit(1)
    finally:
        sys.stdout = old_stdout
