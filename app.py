import sqlite3
import psycopg2 
import os

import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp

# Connect to our database
DB_CONFIG = os.getenv("DB_TYPE")
if DB_CONFIG == 'PG':
    PG_USER = os.getenv("PG_USER")
    con = psycopg2.connect(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/todoapp?connect_timeout=10&application_name=todoapp")
else:
    con = sqlite3.connect("reimburse_app.sqlite", isolation_level=None)
cur = con.cursor()

# Create the table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        name TEXT,
        item TEXT,
        price FLOAT,
        is_paid BOOLEAN
    )
    """
)

# Define our Form
class Task(BaseModel):
    name: str
    item: str
    price: float
    is_paid: bool

# This function will be called when the check mark is toggled, this is called a callback function
def toggle_is_paid(is_paid, row):
    cur.execute(
        """
        UPDATE tasks SET is_paid = ? WHERE id = ?
        """,
        (is_paid, row[0]),
    )
# delete task
def delete_task(task_id):
    cur.execute(
        """
        DELETE FROM tasks WHERE id = ?
        """,
        (task_id,),
    )


def main():
    st.title("Reimbursement App")

    # Search and filter functionality
    search_query = st.text_input('Search Transactions')
    filter_status = st.selectbox('Filter by status', options=["All", "Paid", "Not Paid"])

    # Create a Form using the streamlit-pydantic package, just pass it the Task Class
    data = sp.pydantic_form(key="task_form", model=Task)
    if data:
        cur.execute(
            """
            INSERT INTO tasks (name, item, price, is_paid) VALUES (?, ?, ?, ?)
            """,
            (data.name, data.item, data.price, data.is_paid),
        )

    query = "SELECT * FROM tasks"
    if search_query:
        query += f" WHERE name LIKE '%{search_query}%'"
    if filter_status == "Paid":
        query += " AND is_paid = 1" if "WHERE" in query else " WHERE is_paid = 1"
    elif filter_status == "Not Paid":
        query += " AND is_paid = 0" if "WHERE" in query else " WHERE is_paid = 0"
    
    data = cur.execute(query).fetchall()

    cols = st.columns(5)
    cols[0].write("Paid?")
    cols[1].write("Name")
    cols[2].write("Item")
    cols[3].write("Price")
    cols[4].write("Delete")

    for row in data:
            # Use `f"done-{row[0]}"` for the checkbox key
        done_label = "Yes" if row[4] else "Not Yet"
        cols[0].checkbox(done_label, row[4], key=f"done-{row[0]}", on_change=toggle_is_paid, args=(not row[4], row))
        cols[1].write(row[1])
        cols[2].write(row[2])
        cols[3].write(row[3])
        # Use `f"delete-{row[0]}"` for the delete button key
        if cols[4].button("Delete", key=f"delete-{row[0]}"):
            delete_task(row[0])
            st.experimental_rerun()

main()