import os
import sys
import uvicorn
from app.main import app
from app.utils.db_utils import get_db_connection, get_visitor_stats, get_usage_stats

# Test the database connection
connection = get_db_connection()
if connection:
    print("Database connection successful!")
    connection.close()
else:
    print("Failed to connect to database!", file=sys.stderr)
    sys.exit(1)

# Test visitor stats
test_stats = get_visitor_stats("127.0.0.1", "Test Browser")
if test_stats:
    print(f"Visitor stats retrieved: {test_stats}")
else:
    print("Failed to get visitor stats!", file=sys.stderr)
    sys.exit(1)

# Test usage stats
usage = get_usage_stats()
print(f"Usage stats: {usage}")

# Run the app directly for testing
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Running app on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)