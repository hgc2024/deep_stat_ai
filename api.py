from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import io
import contextlib
import os

# Import Agents
# Import Agents
from agents.architect import get_architect_chain
from agents.coder import get_coder_chain
from agents.analyst import get_context_analyst, retrieve_rag_context

app = FastAPI()

# Allow CORS for React (Vite usually runs on 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    plan: str
    code: str
    result: str
    success: bool

# Initialize Chains (Lazy load to allow time for pip install)
architect_chain = None
coder_chain = None
analyst_chain = None

def get_chains():
    global architect_chain, coder_chain, analyst_chain
    if not architect_chain:
        architect_chain = get_architect_chain()
    if not coder_chain:
        coder_chain = get_coder_chain()
    if not analyst_chain:
        analyst_chain = get_context_analyst()
    return architect_chain, coder_chain, analyst_chain

import pandas as pd 

def execute_code(code):
    print("\n🐍 EXECUTING CODE...")
    code = code.replace("```python", "").replace("```", "").strip()
    
    f = io.StringIO()
    f_err = io.StringIO()
    success = False
    exec_globals = {'duckdb': duckdb, 'pd': pd}
    
    with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f_err):
        try:
            exec(code, exec_globals)
            success = True
        except Exception as e:
            print(f"RUNTIME ERROR: {e}")
            import traceback
            traceback.print_exc()
            success = False
            
    output = f.getvalue()
    errors = f_err.getvalue()
    
    if errors: output += f"\n[STDERR]\n{errors}"

    if not output.strip() and success:
        if 'result' in exec_globals: output = f"[Captured 'result']:\n{exec_globals['result']}"
        elif 'df' in exec_globals: output = f"[Captured 'df']:\n{exec_globals['df']}"
        else: output = "(No output. Try assigning 'result' variable.)"
            
    return output, success

import re

@app.post("/api/query", response_model=QueryResponse)
async def run_query(req: QueryRequest):
    try:
        architect, coder, analyst = get_chains()
        
        # 1. Plan
        print(f"🤔 Planning: {req.question}")
        plan = architect.invoke({"question": req.question})
        
        # 2. Code
        print(f"💻 Coding...")
        code_raw = coder.invoke({"plan": plan, "question": req.question})
        
        # Robust Extraction: Find content strictly inside ```python ... ```
        match = re.search(r"```python(.*?)```", code_raw, re.DOTALL)
        if match:
            code_clean = match.group(1).strip()
        else:
            # Fallback: Just strip fences if regex fails
            code_clean = code_raw.replace("```python", "").replace("```", "").strip()
        
        # 3. Execute with Retry
        max_retries = 2
        attempt = 0
        success = False
        result_output = ""
        
        while attempt <= max_retries:
            print(f"🐍 Executing (Attempt {attempt+1}/{max_retries+1})...")
            result_output, success = execute_code(code_clean)
            
            if success:
                break
            
            attempt += 1
            if attempt <= max_retries:
                print(f"⚠️ Runtime Error. Requesting Fix from Coder...")
                error_hint = f"\n\nPREVIOUS CODE FAILED WITH ERROR:\n{result_output}\n\nFIX THE CODE. DO NOT REPEAT MISTAKES."
                
                # Ask Coder to Fix
                code_raw = coder.invoke({
                    "plan": plan, 
                    "question": req.question + error_hint
                })
                
                # Extract
                match = re.search(r"```python(.*?)```", code_raw, re.DOTALL)
                if match:
                    code_clean = match.group(1).strip()
                else:
                    code_clean = code_raw.replace("```python", "").replace("```", "").strip()
        
        # 4. Analyst Augmentation
        print(f"🎙️ Analyzing...")
        narrative = ""
        if success:
            rag_context = retrieve_rag_context(req.question)
            narrative = analyst.invoke({
                "question": req.question,
                "answer": result_output,
                "context": rag_context
            })
            
        return QueryResponse(
            plan=plan,
            code=code_clean,
            result=result_output,
            narrative=narrative,
            success=success
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "db": os.path.exists("nba.duckdb")}

if __name__ == "__main__":
    import uvicorn
    # Init DB if needed
    if not os.path.exists("nba.duckdb"):
        print("⚠️ Warning: nba.duckdb not found. Run utils/init_db.py first!")
        
    uvicorn.run(app, host="0.0.0.0", port=8000)
