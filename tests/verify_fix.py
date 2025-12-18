import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from agents.architect import get_architect_chain
from agents.coder import get_coder_chain
from agents.analyst import get_context_analyst

def test_best_defender():
    question = "Which NBA player is arguably the best defender in history?"
    
    print(f"Testing Question: {question}")
    
    architect = get_architect_chain()
    plan = architect.invoke({"question": question})
    print("\n--- ARCHITECT PLAN ---")
    print(plan)
    
    coder = get_coder_chain()
    code = coder.invoke({"plan": plan, "question": question})
    print("\n--- CODER CODE ---")
    print(code)
    
    assert "STL" in code or "BLK" in code, "Code should include defensive stats (STL or BLK)"
    print("\n✅ Verification Success: Code includes defensive stats.")

if __name__ == "__main__":
    try:
        test_best_defender()
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        sys.exit(1)
