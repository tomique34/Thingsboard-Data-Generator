import os
import sys

print("Python path:", sys.path)
print("Current directory:", os.getcwd())

try:
    from app import routes
    print("Import successful!")
except ImportError as e:
    print("Import error:", str(e))

print("Done.")
