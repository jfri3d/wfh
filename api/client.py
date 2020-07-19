import logging
import sqlite3
from datetime import datetime

from model import Actions

DB_PATH = "actions.sqlite"
TABLE_NAME = "actions"


class DBClient:
    def __init__(self, db_path=DB_PATH, table_name=TABLE_NAME):
        self.db_path = db_path
        self.table_name = table_name

        self.client = self._connect()
        self._create_table() if not self._check_table() else None

    def _connect(self):
        logging.info(f"[client] connecting -> {self.db_path}")
        return sqlite3.connect(self.db_path)

    def _check_table(self):
        logging.info(f"[client] checking table -> {self.table_name}")
        command = f"SELECT 1 FROM sqlite_master WHERE type='table' and name='{TABLE_NAME}'"
        return bool(self.client.execute(command).fetchone())

    def _create_table(self):
        logging.info(f"[client] creating table -> {self.table_name}")
        cur = self.client.cursor()

        command = f"""
            CREATE TABLE {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                d DATE DEFAULT (datetime('now','localtime')),
                action str NOT NULL)"""

        cur.execute(command)
        self.client.commit()

    def insert_action(self, action: Actions):
        logging.info(f"[client] insert action -> {action.name}")
        self.client = self._connect()
        cur = self.client.cursor()
        command = f"INSERT INTO {self.table_name} (action) VALUES(?)"
        cur.execute(command, (action.name,))
        self.client.commit()

    def get_actions(self, action: Actions, limit_today=False):
        logging.info(f"[client] get action -> {action.name}")
        self.client = self._connect()
        cur = self.client.cursor()
        command = f"SELECT datetime(d, 'localtime'), action FROM {TABLE_NAME} WHERE action = ?"
        values = (action.name,)
        if limit_today:
            logging.info(f"[client] limit query to today")
            command += " AND date(d, 'localtime') = ?"
            values += (datetime.now().strftime('%Y-%m-%d'),)
        result = cur.execute(command, values).fetchall()

        return {"action": action.name, "dates": [v[0] for v in result]}
