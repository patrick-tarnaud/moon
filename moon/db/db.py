import sqlite3
from typing import Optional


class ConnectionDB:
    db: str = ''
    conn: Optional[sqlite3.Connection] = None
    cur: Optional[sqlite3.Cursor] = None

    @staticmethod
    def set_db(db: str):
        ConnectionDB.db = db

    @staticmethod
    def get_connection() -> sqlite3.Connection:
        if ConnectionDB.conn is None:
            ConnectionDB.conn = sqlite3.connect(ConnectionDB.db)
            ConnectionDB.cur = ConnectionDB.conn.cursor()
        return ConnectionDB.conn

    @staticmethod
    def get_cursor() -> sqlite3.Cursor:
        if ConnectionDB.cur is None:
            ConnectionDB.get_connection()
        return ConnectionDB.cur # type: ignore

    @staticmethod
    def commit():
        ConnectionDB.conn.commit()

    @staticmethod
    def close():
        ConnectionDB.conn.close()
