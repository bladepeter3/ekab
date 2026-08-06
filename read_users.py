import sqlite3

# 1. Connect to the database file
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# 2. Execute a SQL command to grab everything from the 'users' table
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# 3. Print the results nicely
print("--- REGISTERED USERS ---")
for row in rows:
    # row is a tuple: (id, name, last_name, username, password, role)
    print(f"ID: {row[0]} | Name: {row[1]} {row[2]} | Username: {row[3]} | Password: {row[4]} | Role: {row[5]}")

# 4. Close the connection
conn.close()