import sqlite3 

con = sqlite3.connect("db.sqlite")
con.cursor().execute("DROP TABLE 'allowed_time'")