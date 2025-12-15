import requests
import json
import time

URL = "http://localhost:8000/api/query"

def test_query(question):
    print(f"Testing Question: {question}")
    try:
        start = time.time()
        res = requests.post(URL, json={"question": question})
        duration = time.time() - start
        
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Success ({duration:.2f}s)")
            print(f"Goal: {data['success']}")
            print(f"Narrative: {data.get('narrative', '')[:100]}...")
            return True
        else:
            print(f"❌ Failed: {res.status_code}")
            print(f"Error: {res.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    # Test valid query
    test_query("Who won the 2016 NBA Championship?")
