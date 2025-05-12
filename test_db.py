import os
import psycopg2
import sys

# Get database connection string from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

def test_connection():
    """Test database connection"""
    print(f"Attempting to connect to database with URL: {DATABASE_URL[:10]}...")
    try:
        connection = psycopg2.connect(DATABASE_URL)
        print("Connection successful!")
        
        # Test creating the visitor_stats table
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS visitor_stats (
                            id SERIAL PRIMARY KEY,
                            ip_address TEXT NOT NULL,
                            device_info TEXT,
                            visit_count INTEGER DEFAULT 1,
                            record_button_count INTEGER DEFAULT 0,
                            send_button_count INTEGER DEFAULT 0,
                            read_button_count INTEGER DEFAULT 0,
                            first_visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    print("Created visitor_stats table successfully")
                    
                    # Insert a test record
                    cursor.execute("""
                        INSERT INTO visitor_stats (ip_address, device_info)
                        VALUES (%s, %s)
                        RETURNING id
                    """, ("127.0.0.1", "Test Device"))
                    
                    test_id = cursor.fetchone()[0]
                    print(f"Inserted test record with ID: {test_id}")
                    
                    # Test query to get visitors
                    cursor.execute("SELECT COUNT(*) FROM visitor_stats")
                    count = cursor.fetchone()[0]
                    print(f"Total visitors in database: {count}")
                    
        except Exception as e:
            print(f"Database operation error: {e}", file=sys.stderr)
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error connecting to the database: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)