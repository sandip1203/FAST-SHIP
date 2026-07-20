import sqlite3
from typing import Any

from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate  # type: ignore


class Database:
    def connect_to_db(self):
        # Make connection with database
        self.conn = sqlite3.connect("sqlite.db", check_same_thread=False)
        # Get cursor to execute queries and fetch data
        self.cur = self.conn.cursor()
        print("connected to sqlite.db ...")
        self.create_table()


    def create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS shipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                weight REAL,
                status TEXT,
                destination INTEGER
            )
        """)

    def create(self, shipment: ShipmentCreate) -> int:
        self.cur.execute("""
            INSERT INTO shipment (content, weight, status, destination)
            VALUES (:content, :weight, :status, :destination)
        """, {
            **shipment.model_dump(),
            "status": "placed",
        })

        self.conn.commit()
        return self.cur.lastrowid

    def get(self, id: int) -> dict[str, Any] | None:
        self.cur.execute("""
            SELECT * FROM shipment WHERE id = ?
        """, (id,))
        row = self.cur.fetchone()

        return {
            "id": row[0],
            "content": row[1],
            "weight": row[2],
            "status": row[3],
            "destination": row[4],  # ✅ FIX
        } if row else None
    
    def update(self, id: int, shipment: ShipmentUpdate):
        data = shipment.model_dump(exclude_unset=True)

        if "status" in data:
            self.cur.execute("""
                UPDATE shipment SET status = :status
                WHERE id = :id
            """, {"id": id, "status": data["status"]})
            self.conn.commit()

        return self.get(id)
    
    def delete(self, id: int):
        self.cur.execute("""
            DELETE FROM shipment
            WHERE id = ?
        """, (id, ))
        self.conn.commit()

    def close(self):
        print("...connection closed")
        self.conn.close()
        
    def __enter__(self):
        print("enter the context")
        self.connect_to_db()
        self.create_table()
        return self
    
    def __exit__(self,*arg):
        print("exiting the context")
        self.close()

## usage 
with Database()  as db:
    print(db.get(2))