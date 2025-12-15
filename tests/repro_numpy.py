import duckdb
import numpy as np
import pandas as pd

try:
    con = duckdb.connect(':memory:')
    con.execute("CREATE TABLE test (id INTEGER)")
    con.execute("INSERT INTO test VALUES (1)")
    
    # Create a numpy int64
    val = np.int64(1)
    print(f"Value type: {type(val)}")
    
    print("Attempting to pass numpy.int64 as parameter...")
    con.execute("SELECT * FROM test WHERE id = ?", [val])
    print("Success!")
    
except Exception as e:
    print(f"Caught expected error: {e}")
