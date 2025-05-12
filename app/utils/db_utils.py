import os
import sqlite3
import sys
from datetime import datetime

# Get database path from environment variables or use default
DATABASE_URL = os.environ.get('DATABASE_URL', 'app/data/visitor_stats.db')

def get_db_connection():
    """Create a database connection"""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(DATABASE_URL), exist_ok=True)
        connection = sqlite3.connect(DATABASE_URL)
        connection.row_factory = sqlite3.Row  # This enables column access by name
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}", file=sys.stderr)
        return None

def init_db():
    """Initialize the database with required tables"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visitor_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            connection.commit()
            return True
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr)
        return False
    finally:
        connection.close()

def get_visitor_stats(ip_address, device_info):
    """Get visitor stats based on IP address and device info"""
    print(f"[DB] Getting stats for visitor: {ip_address}, {device_info}", file=sys.stderr)
    connection = get_db_connection()
    if not connection:
        print("[DB] Failed to get database connection", file=sys.stderr)
        return None
    
    try:
        with connection:
            cursor = connection.cursor()
            # Check if the visitor exists
            cursor.execute(
                "SELECT * FROM visitor_stats WHERE ip_address = ? AND device_info = ?",
                (ip_address, device_info)
            )
            visitor = cursor.fetchone()
            
            if visitor:
                print(f"[DB] Existing visitor found: {visitor['id']}", file=sys.stderr)
                # Update the visitor stats
                cursor.execute(
                    """
                    UPDATE visitor_stats 
                    SET visit_count = visit_count + 1, 
                        last_visit_time = CURRENT_TIMESTAMP 
                    WHERE id = ? 
                    RETURNING *
                    """,
                    (visitor['id'],)
                )
                result = cursor.fetchone()
                print(f"[DB] Updated visitor stats: visit_count={result['visit_count']}", file=sys.stderr)
                return dict(result)
            else:
                print(f"[DB] Creating new visitor record", file=sys.stderr)
                # Create a new visitor record
                cursor.execute(
                    """
                    INSERT INTO visitor_stats 
                    (ip_address, device_info) 
                    VALUES (?, ?) 
                    RETURNING *
                    """,
                    (ip_address, device_info)
                )
                result = cursor.fetchone()
                print(f"[DB] Created new visitor with id={result['id']}", file=sys.stderr)
                return dict(result)
    except Exception as e:
        print(f"Error getting visitor stats: {e}", file=sys.stderr)
        return None
    finally:
        connection.close()

def increment_button_count(ip_address, device_info, button_type):
    """Increment button count for a specific visitor"""
    if button_type not in ['record', 'send', 'read']:
        return False
    
    connection = get_db_connection()
    if not connection:
        return False
    
    column_name = f"{button_type}_button_count"
    
    try:
        with connection:
            cursor = connection.cursor()
            # Update the visitor button count
            cursor.execute(
                f"""
                UPDATE visitor_stats 
                SET {column_name} = {column_name} + 1 
                WHERE ip_address = ? AND device_info = ? 
                RETURNING *
                """,
                (ip_address, device_info)
            )
            visitor = cursor.fetchone()
            return dict(visitor) if visitor else None
    except Exception as e:
        print(f"Error incrementing button count: {e}", file=sys.stderr)
        return False
    finally:
        connection.close()

def check_button_usage(ip_address, device_info, button_type):
    """Check if button usage limit is reached for a specific visitor"""
    if button_type not in ['record', 'send', 'read']:
        return {'allowed': False, 'remaining': 0}
    
    connection = get_db_connection()
    if not connection:
        return {'allowed': True, 'remaining': 10}  # Fallback to allowing usage if DB issue
    
    column_name = f"{button_type}_button_count"
    
    try:
        with connection:
            cursor = connection.cursor()
            # Get the current count
            cursor.execute(
                f"""
                SELECT {column_name} FROM visitor_stats 
                WHERE ip_address = ? AND device_info = ?
                """,
                (ip_address, device_info)
            )
            result = cursor.fetchone()
            
            if result:
                count = result[column_name]
                remaining = 10 - count
                return {
                    'allowed': count < 10,
                    'remaining': remaining if remaining > 0 else 0
                }
            else:
                # No visitor record yet, so full usage allowed
                return {'allowed': True, 'remaining': 10}
    except Exception as e:
        print(f"Error checking button usage: {e}", file=sys.stderr)
        return {'allowed': True, 'remaining': 10}  # Fallback to allowing usage if error
    finally:
        connection.close()

def get_total_visitors():
    """Get total unique visitors count"""
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM visitor_stats")
            result = cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        print(f"Error getting total visitors: {e}", file=sys.stderr)
        return 0
    finally:
        connection.close()

def get_usage_stats():
    """Get aggregate usage statistics"""
    connection = get_db_connection()
    if not connection:
        return {
            'total_visitors': 0,
            'total_visits': 0,
            'total_record_uses': 0,
            'total_send_uses': 0,
            'total_read_uses': 0
        }
    
    try:
        with connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_visitors,
                    SUM(visit_count) as total_visits,
                    SUM(record_button_count) as total_record_uses,
                    SUM(send_button_count) as total_send_uses,
                    SUM(read_button_count) as total_read_uses
                FROM visitor_stats
            """)
            row = cursor.fetchone()
            
            if row:
                stats = {
                    'total_visitors': row[0] if row[0] is not None else 0,
                    'total_visits': row[1] if row[1] is not None else 0,
                    'total_record_uses': row[2] if row[2] is not None else 0,
                    'total_send_uses': row[3] if row[3] is not None else 0,
                    'total_read_uses': row[4] if row[4] is not None else 0
                }
            else:
                stats = {
                    'total_visitors': 0,
                    'total_visits': 0,
                    'total_record_uses': 0,
                    'total_send_uses': 0,
                    'total_read_uses': 0
                }
            return stats
    except Exception as e:
        print(f"Error getting usage stats: {e}", file=sys.stderr)
        return {
            'total_visitors': 0,
            'total_visits': 0,
            'total_record_uses': 0,
            'total_send_uses': 0,
            'total_read_uses': 0
        }
    finally:
        connection.close()