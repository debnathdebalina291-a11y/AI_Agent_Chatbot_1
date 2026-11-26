import sqlite3

DB_PATH = "conversations.db"


# 1. Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# 2. Create conversations table
def create_conversations_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("Conversations table created successfully!")
    conn.close()


# 3. Insert a chat exchange into conversations table
def save_conversation(user_message, ai_response):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO conversations (user_message, ai_response)
        VALUES (?, ?)
        """,
        (user_message, ai_response),
    )
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()
    return conversation_id


# 4. Retrieve all previous conversations
def get_all_conversations(limit=100):

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, user_message, ai_response, created_at
            FROM conversations
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        conversations = cursor.fetchall()

        return [dict(row) for row in conversations]

    finally:
        conn.close()


# 5. Retrieve a particular conversation using its ID
def get_conversation_by_id(conversation_id):

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, user_message, ai_response, created_at
            FROM conversations
            WHERE id = ?
        """, (conversation_id,))

        conversation = cursor.fetchone()

        return dict(conversation) if conversation else None

    finally:
        conn.close()


# 6. Retrieve recent conversations for chat history
def get_conversations(limit=50):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_message, ai_response, created_at
            FROM conversations
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# 7. Verify database tables
def check_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """)
    tables = cursor.fetchall()
    print("\nAvailable database tables:")
    for table in tables:
        print(table["name"])
    conn.close()


# 8. Execute database functions
if __name__ == "__main__":
    create_conversations_table()
    check_database()
    print("\nSQLite database configured successfully!")