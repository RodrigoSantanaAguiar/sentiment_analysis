import sqlite3
import time
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def load_sql_query(filename):
    script_dir = os.path.dirname(__file__)
    filepath = os.path.join(script_dir, "sql_queries", filename)
    with open(filepath, "r") as query_file:
        return query_file.read()


def execute_query(query_filename):
    conn = None
    try:
        conn = sqlite3.connect("sentiment_data.db")
        cursor = conn.cursor()

        sql_query = load_sql_query(query_filename)
        cursor.execute(sql_query)
        conn.commit()
        logging.info("Query executed successfully!")

    except Exception as e:
        logging.error(e)
    finally:
        if conn:
            conn.close()

# Create aggregated table
execute_query("create_aggregated_table.sql")

while True:
    execute_query("aggregate_data.sql")
    time.sleep(60)
