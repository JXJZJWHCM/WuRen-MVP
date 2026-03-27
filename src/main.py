import uvicorn
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # If running directly, we need to make sure uvicorn can find 'src'
    # We are already in src/main.py, so adding parent to path helps python imports,
    # but uvicorn loads by string.
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
