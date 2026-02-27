"""
Migration script: Add materiality fields to article table and seed new topics.

Run this script once to update the database schema:
    python migrate_materiality.py

This script is idempotent — safe to run multiple times.
"""
import sqlite3
import os
import sys


def get_db_path():
    """Resolve the database path from config or default."""
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///trading_app.db')
    if db_url.startswith('sqlite:///'):
        path = db_url.replace('sqlite:///', '')
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(__file__), path)
        return path
    print(f"Non-SQLite database detected ({db_url}). Adjust this script for your DB.")
    sys.exit(1)


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def migrate(db_path):
    print(f"Migrating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Add materiality_score column
    if not column_exists(cursor, 'article', 'materiality_score'):
        cursor.execute("ALTER TABLE article ADD COLUMN materiality_score FLOAT")
        print("  Added column: article.materiality_score")
    else:
        print("  Column article.materiality_score already exists, skipping")

    # 2. Add is_material column with default TRUE
    if not column_exists(cursor, 'article', 'is_material'):
        cursor.execute("ALTER TABLE article ADD COLUMN is_material BOOLEAN DEFAULT 1")
        print("  Added column: article.is_material (default=TRUE)")
    else:
        print("  Column article.is_material already exists, skipping")

    # 3. Seed new topic categories
    new_topics = [
        "M&A", "Spin-offs", "Buybacks", "Guidance", "Leadership",
        "Approvals", "Activism", "Earnings", "Offerings", "Partnerships",
        "Litigation", "Restructuring", "Contracts", "Clinical Trials", "General",
    ]

    for topic_name in new_topics:
        cursor.execute("SELECT id FROM topic WHERE name = ?", (topic_name,))
        if not cursor.fetchone():
            import uuid
            cursor.execute(
                "INSERT INTO topic (id, name) VALUES (?, ?)",
                (str(uuid.uuid4()), topic_name)
            )
            print(f"  Seeded topic: {topic_name}")

    # 4. Rename "Spin offs" -> "Spin-offs" (preserve existing relationships)
    cursor.execute("SELECT id FROM topic WHERE name = 'Spin offs'")
    old_topic = cursor.fetchone()
    if old_topic:
        cursor.execute("SELECT id FROM topic WHERE name = 'Spin-offs'")
        new_topic = cursor.fetchone()
        if new_topic:
            # Both exist — migrate article associations from old to new, then delete old
            old_id = old_topic[0]
            new_id = new_topic[0]
            cursor.execute(
                "UPDATE OR IGNORE article_topic SET topic_id = ? WHERE topic_id = ?",
                (new_id, old_id)
            )
            cursor.execute("DELETE FROM article_topic WHERE topic_id = ?", (old_id,))
            cursor.execute("DELETE FROM topic WHERE id = ?", (old_id,))
            print("  Migrated 'Spin offs' associations to 'Spin-offs' and removed old topic")
        else:
            # Only old exists — just rename it
            cursor.execute(
                "UPDATE topic SET name = 'Spin-offs' WHERE name = 'Spin offs'"
            )
            print("  Renamed topic: 'Spin offs' -> 'Spin-offs'")

    conn.commit()
    conn.close()
    print("Migration complete!")


if __name__ == '__main__':
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Run the app first to create it.")
        sys.exit(1)
    migrate(db_path)
