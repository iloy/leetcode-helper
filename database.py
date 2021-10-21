
import sqlite3

DATABASE_FILENAME = 'leetcode.sqlite3'

def vacuum() -> None:
    con = sqlite3.connect(DATABASE_FILENAME)
    try:
        con.execute("VACUUM")
    finally:
        con.close()

