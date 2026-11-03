import sqlite3
from pathlib import Path

DB_FILE = str(Path(__file__).resolve().with_name("subscriptions.db"))


def get_channels():
    con = sqlite3.connect(DB_FILE)
    rows = con.execute(
        "SELECT id, channel, link, enabled FROM channels ORDER BY id"
    ).fetchall()
    con.close()
    return rows


def add_channel(channel, link):
    con = sqlite3.connect(DB_FILE)
    con.execute(
        "INSERT OR IGNORE INTO channels (channel, link, enabled) VALUES (?, ?, 1)",
        (channel, link)
    )
    con.commit()
    con.close()


def toggle_channel(channel_id):
    con = sqlite3.connect(DB_FILE)
    con.execute(
        "UPDATE channels SET enabled = CASE enabled WHEN 1 THEN 0 ELSE 1 END WHERE id = ?",
        (channel_id,)
    )
    con.commit()
    con.close()


def delete_channel(channel_id):
    con = sqlite3.connect(DB_FILE)
    con.execute(
        "DELETE FROM channels WHERE id = ?",
        (channel_id,)
    )
    con.commit()
    con.close()
