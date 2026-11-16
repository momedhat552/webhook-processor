from fastapi import FastAPI
import asyncio
import sqlite3
from pydantic import BaseModel
import os

DB_PATH = os.getenv("DB_PATH","alerts.db")
app = FastAPI()

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
        event_id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL
        
        ) 
        
        
        """
    )
    conn.commit()
    conn.close()


init_db()





class Alert(BaseModel):
    event_id: str
    source: str
    message: str
    timestamp: str

@app.post("/webhook")
async def receive_webhook(alert:Alert):
    await asyncio.sleep(3)
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO alerts (event_id, source, message, timestamp) VALUES (?, ?, ?, ?)",

        (alert.event_id, alert.source, alert.message, alert.timestamp),
    )
    conn.commit()
    conn.close()
    return {"status": "processed", "event_id": alert.event_id}

@app.get("/alerts")
def get_alerts():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM alerts").fetchall()
    conn.close()
    return [dict(row) for row in rows]