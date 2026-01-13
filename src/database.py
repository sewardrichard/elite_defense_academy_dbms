import os
import psycopg2
from psycopg2.extras import RealDictCursor
from src.utils import load_env_from_file

# Load environment variables on module import
load_env_from_file()

DB_NAME = os.getenv("DB_NAME", "student_records_db")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    """Establish and return a database connection."""
    try:
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(query, params=None, fetch=False, commit=False):
    """
    Execute a generic SQL query.
    
    Args:
        query (str): SQL query.
        params (tuple, optional): Parameters for the query.
        fetch (bool, optional): If True, returns fetched results.
        commit (bool, optional): If True, commits the transaction.
        
    Returns:
        list/None: Query results if fetch is True, else None.
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    result = None
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
            if commit:
                conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()
        
    return result

def execute_proc(proc_name, params=None, fetch_result=False):
    """
    Call a stored procedure.
    
    Args:
        proc_name (str): Name of the stored procedure.
        params (tuple, optional): Parameters.
        fetch_result (bool, optional): whether to fetch a result (e.g. for RETURNING or scalar funcs).
    
    Returns:
        The result of the stored procedure if fetch_result is True.
    """
    conn = get_db_connection()
    if not conn:
        return None

    result = None
    try:
        with conn.cursor() as cur:
            # We use `callproc` for standard procedures, but for functions that return values
            # (generic query style) it's often easier to just SELECT function(args).
            # Given our sp_* functions return values (IDs, void), let's use SELECT or CALL.
            # Postgres functions are often called via SELECT.
            
            # Construct placeholder string
            placeholders = ', '.join(['%s'] * len(params)) if params else ''
            query = f"SELECT {proc_name}({placeholders})"
            
            cur.execute(query, params)
            
            if fetch_result:
                result = cur.fetchone()
                # Accessing the first column of the result which is normally the function return
                result = result[proc_name] if result and proc_name in result else (result[0] if result else None)
                
            conn.commit() # Functions with side effects need commit if called via SELECT
            
    except Exception as e:
        print(f"Error executing procedure {proc_name}: {e}")
        conn.rollback()
    finally:
        conn.close()
        
    return result
