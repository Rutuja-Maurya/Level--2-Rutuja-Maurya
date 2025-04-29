import os
import sys
from waitress import serve

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.app import app
from backend.app.config import HOST, PORT

if __name__ == '__main__':
    print(f"Starting server on {HOST}:{PORT}")
    serve(app, host=HOST, port=PORT) 