import sqlite3
connect = sqlite3.connect('database.db')
print(connect.execute('''SELECT * FROM TWEETS LIMIT 5''').fetchall())
print(connect.execute('''SELECT * FROM EMOTIONS LIMIT 5''').fetchall())
print(connect.execute('''SELECT * FROM USERS''').fetchall())