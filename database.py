"""
Database module for Hostel Management System
Handles SQLite connection, schema execution, and common helpers.
Supports local execution and Vercel serverless deployment (/tmp writable storage).
"""

import sqlite3
import os
import shutil
from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')
LOCAL_DB = os.path.join(BASE_DIR, 'hostel.db')

# On Vercel serverless functions, only /tmp is writable
IS_SERVERLESS = bool(
    os.environ.get('VERCEL') or 
    os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or 
    not os.access(BASE_DIR, os.W_OK)
)

if IS_SERVERLESS:
    DATABASE = '/tmp/hostel.db'
else:
    DATABASE = os.environ.get('DATABASE_PATH', LOCAL_DB)


def ensure_db_ready():
    """Ensure writable database exists with schema and seed data on serverless cold starts."""
    if IS_SERVERLESS:
        if not os.path.exists(DATABASE):
            # Try to copy pre-seeded database to /tmp
            if os.path.exists(LOCAL_DB):
                try:
                    shutil.copyfile(LOCAL_DB, DATABASE)
                    os.chmod(DATABASE, 0o666)
                except Exception as e:
                    print("Notice: Error copying bundled db to /tmp:", e)

            # If still not present, initialize schema and seed
            if not os.path.exists(DATABASE):
                try:
                    conn = sqlite3.connect(DATABASE)
                    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                        conn.executescript(f.read())
                    conn.commit()
                    conn.close()
                    import seed_data
                    seed_data.seed()
                except Exception as e:
                    print("Notice: Error initializing /tmp database:", e)

    # Always ensure schema and required columns are present on any environment
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='users'")
        has_users_table = cur.fetchone()[0]
        if not has_users_table:
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
            import seed_data
            seed_data.seed()
        else:
            # Check user count; if 0, run seed
            cur.execute("SELECT count(*) FROM users")
            user_count = cur.fetchone()[0]
            if user_count == 0:
                import seed_data
                seed_data.seed()

            # Ensure outpasses table has all columns
            cur.execute("PRAGMA table_info(outpasses)")
            outpass_cols = [row[1] for row in cur.fetchall()]
            if 'parent_approval' not in outpass_cols:
                try:
                    cur.execute("ALTER TABLE outpasses ADD COLUMN parent_approval TEXT DEFAULT 'Pending'")
                except Exception:
                    pass
            if 'parent_remarks' not in outpass_cols:
                try:
                    cur.execute("ALTER TABLE outpasses ADD COLUMN parent_remarks TEXT")
                except Exception:
                    pass
            if 'parent_action_at' not in outpass_cols:
                try:
                    cur.execute("ALTER TABLE outpasses ADD COLUMN parent_action_at TIMESTAMP")
                except Exception:
                    pass
            conn.commit()
        conn.close()
    except Exception as e:
        print("Notice: Database verification check:", e)


# Run verification on import
ensure_db_ready()


def get_db():
    """Get or create database connection for the current request context."""
    ensure_db_ready()
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db


def close_connection(exception=None):
    """Closes database connection at request end."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Execute a query and fetch results."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def modify_db(query, args=()):
    """Execute INSERT/UPDATE/DELETE query and commit."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id


def init_db():
    """Initialize database from schema.sql."""
    conn = sqlite3.connect(DATABASE)
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DATABASE}.")


def upgrade_db():
    """Ensure any newly added columns and tables exist in an existing database."""
    ensure_db_ready()
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_script = f.read()
    conn.executescript(schema_script)

    cur.execute("PRAGMA table_info(outpasses)")
    columns = [row[1] for row in cur.fetchall()]
    if 'parent_approval' not in columns:
        try:
            cur.execute("ALTER TABLE outpasses ADD COLUMN parent_approval TEXT DEFAULT 'Pending'")
        except Exception:
            pass
    if 'parent_remarks' not in columns:
        try:
            cur.execute("ALTER TABLE outpasses ADD COLUMN parent_remarks TEXT")
        except Exception:
            pass
    if 'parent_action_at' not in columns:
        try:
            cur.execute("ALTER TABLE outpasses ADD COLUMN parent_action_at TIMESTAMP")
        except Exception:
            pass

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
