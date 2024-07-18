import sqlite3
from typing import List, Dict
import json
import csv
import io
from datetime import datetime

DB_NAME = "files.db"


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        summary TEXT,
        file_type TEXT,
        path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS file_tags (
        file_id INTEGER,
        tag_id INTEGER,
        FOREIGN KEY (file_id) REFERENCES files(id),
        FOREIGN KEY (tag_id) REFERENCES tags(id),
        PRIMARY KEY (file_id, tag_id)
    )
    """
    )

    conn.commit()
    conn.close()


def add_file_to_db(file_meta: Dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO files (title, summary, file_type, path)
        VALUES (?, ?, ?, ?)
    """,
        (
            file_meta["title"],
            file_meta["summary"],
            file_meta["file_type"],
            file_meta["path"],
        ),
    )

    file_id = cursor.lastrowid

    for tag in file_meta["tags"]:
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
        tag_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id)
        )

    conn.commit()
    conn.close()


def find_files_by_tag(tag: str) -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT files.id, files.title, files.summary, files.file_type, files.path, files.created_at
    FROM files
    JOIN file_tags ON files.id = file_tags.file_id
    JOIN tags ON file_tags.tag_id = tags.id
    WHERE tags.name = ?
    """,
        (tag,),
    )

    rows = cursor.fetchall()

    files = []
    for row in rows:
        file = {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "file_type": row[3],
            "path": row[4],
            "created_at": row[5],
        }
        files.append(file)

    conn.close()
    return files


def get_all_tags() -> List[str]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT tags.name
    FROM tags
    """
    )

    rows = [i[0] for i in cursor.fetchall()]

    return rows


def search_files(keywords: str) -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    search_terms = f"%{keywords}%"
    cursor.execute(
        """
        SELECT id, title, summary, file_type, path, created_at
        FROM files
        WHERE title LIKE ? OR summary LIKE ?
    """,
        (search_terms, search_terms),
    )
    rows = cursor.fetchall()
    files = [
        {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "file_type": row[3],
            "path": row[4],
            "created_at": row[5],
        }
        for row in rows
    ]
    conn.close()
    return files


def filter_by_tags(tags: List[str]) -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in tags)
    cursor.execute(
        f"""
        SELECT DISTINCT f.id, f.title, f.summary, f.file_type, f.path, f.created_at
        FROM files f
        JOIN file_tags ft ON f.id = ft.file_id
        JOIN tags t ON ft.tag_id = t.id
        WHERE t.name IN ({placeholders})
    """,
        tags,
    )
    rows = cursor.fetchall()
    files = [
        {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "file_type": row[3],
            "path": row[4],
            "created_at": row[5],
        }
        for row in rows
    ]
    conn.close()
    return files


def get_stats(stat_type: str | None = None) -> Dict:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if stat_type == "file_type":
        cursor.execute("SELECT file_type, COUNT(*) FROM files GROUP BY file_type")
    elif stat_type == "tag":
        cursor.execute(
            """
            SELECT t.name, COUNT(DISTINCT ft.file_id)
            FROM tags t
            JOIN file_tags ft ON t.id = ft.tag_id
            GROUP BY t.name
        """
        )
    else:
        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tags")
        tag_count = cursor.fetchone()[0]
        conn.close()
        return {"total_files": file_count, "total_tags": tag_count}

    results = dict(cursor.fetchall())
    conn.close()
    return results


def add_tag(file_id: int, tag: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
    tag_id = cursor.fetchone()[0]
    cursor.execute(
        "INSERT OR IGNORE INTO file_tags (file_id, tag_id) VALUES (?, ?)",
        (file_id, tag_id),
    )
    conn.commit()
    conn.close()


def rename_tag(old_name: str, new_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tags SET name = ? WHERE name = ?", (new_name, old_name))
    conn.commit()
    conn.close()


def export_db(file):
    conn = sqlite3.connect(DB_NAME)
    for line in conn.iterdump():
        file.write(f"{line}\n")
    conn.close()


def import_db(file):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.executescript(file.read())
    conn.commit()
    conn.close()


def get_file_by_id(file_id: int) -> Dict | None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, summary, file_type, path, created_at FROM files WHERE id = ?",
        (file_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "file_type": row[3],
            "path": row[4],
            "created_at": row[5],
        }
    return None


def update_file_tags(file_id: int, tags: List[str]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM file_tags WHERE file_id = ?", (file_id,))
    for tag in tags:
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
        tag_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id)
        )
    conn.commit()
    conn.close()


def list_files(date_after: str | None = None) -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = "SELECT id, title, summary, file_type, path, created_at FROM files"
    params = ()
    if date_after:
        query += " WHERE created_at > ?"
        params = (date_after,)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    files = [
        {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "file_type": row[3],
            "path": row[4],
            "created_at": row[5],
        }
        for row in rows
    ]
    conn.close()
    return files


def get_tags_for_file(file_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT tags.name
        FROM tags
        JOIN file_tags ON tags.id = file_tags.tag_id
        WHERE file_tags.file_id = ?
    """,
        (file_id,),
    )
    tags = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tags
