import sys
from agents.architect import get_architect_chain
from agents.coder import get_coder_chain
import duckdb
import io
import contextlib

def execute_code(code):
    print("\n🐍 EXECUTING CODE...")
    # Clean code markdown
    code = code.replace("```python", "").replace("```", "").strip()
    
    # Capture stdout
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        try:
            exec(code, {'duckdb': duckdb})
            success = True
        except Exception as e:
            print(f"Runtime Error: {e}")
            success = False
            
    output = f.getvalue()
    return output, success

def main():
    print("🏀 Deep Stat AI: Ready for Queries (Type 'exit' to quit)")
    
    architect = get_architect_chain()
    coder = get_coder_chain()
    
    while True:
        q = input("\nQuery: ")
        if q.lower() in ['exit', 'quit']: break
        
        print("\n🤔 Architecting Plan...")
        plan = architect.invoke({"question": q})
        print(f"PLAN: {plan}")
        
        print("\n💻 Generating Code...")
        code = coder.invoke({"plan": plan, "question": q})
        print(f"CODE:\n{code}")
        
        result, success = execute_code(code)
        
        print("\n📊 RESULT:")
        print(result)

if __name__ == "__main__":
    main()
