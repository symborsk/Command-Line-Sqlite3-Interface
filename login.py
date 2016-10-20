import sqlite3
import hashlib

waiting = True

while waiting:
	# Get the user credentials
	print("\nWelcome to the Hospital Record Service.")
	print("Please log in below. (Note: Passwords are case sensitive!)")
	username = raw_input("\nUsername: ")
	password = raw_input("Password: ")
	passHash = hashlib.md5(password).hexdigest()

	# Connect to the database
	conn = sqlite3.connect('hospital.db')

	# Build/execute the log in query
	cursor = conn.cursor()
	sql = """SELECT staff_id, name, role
				FROM staff
				WHERE login=?
				AND password=?"""
	params = (username, str(passHash))
	cursor.execute(sql, params)

	if len(cursor.fetchall())==1:
		# Get the users attributes
		user = cursor.fetchone()
		waiting = False
	else:
		print("There was an error logging in. Please try again.")
conn.close()