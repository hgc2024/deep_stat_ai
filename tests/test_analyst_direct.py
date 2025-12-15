import sys
import os
sys.path.append(os.getcwd())
from agents.analyst import get_context_analyst

def test_analyst():
    print("Testing Analyst Chain...")
    try:
        chain = get_context_analyst()
        res = chain.invoke({
            "question": "Who won the 2016 NBA Championship?",
            "answer": "NICKNAME CITY\n0 Cavaliers Cleveland",
            "context": "Relevant Teams: Cleveland Cavaliers (2016 Champions, 3-1 comeback)\nRelevant Players: Lebron James"
        })
        print("--- RESULT ---")
        print(f"'{res}'")
        print("--------------")
        print(f"Length: {len(res)}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_analyst()
