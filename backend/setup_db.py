import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user="postgres",
        password="root",  # Your existing password
        host="localhost",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Create a cursor
    cur = conn.cursor()
    
    try:
        # Create database if it doesn't exist
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'delivery_system'")
        exists = cur.fetchone()
        if not exists:
            cur.execute('CREATE DATABASE delivery_system')
            print("Database 'delivery_system' created successfully")
        else:
            print("Database 'delivery_system' already exists")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_database() 