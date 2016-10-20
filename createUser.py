import sqlite3
import hashlib

# Looping variables
waiting1 = True
waiting2 = True

print("\nWelcome to the Hospital User Creation Service.")
print("Please enter \".quit\" at any time to exit.")

# Get user credentials
name = str(raw_input("\nPlease enter your name: "))
while waiting1:
	role = str(raw_input("Please enter your role: "))

	# Check role value
	if role == "D" or role == "N" or role == "A":
		waiting1= False
	else:
		print("Please enter a proper role.")

while waiting2: 
	username = str(raw_input("Please enter a username: "))
	password = str(raw_input("Please enter a password: "))

	# Check to make sure there are no users with this log in 
	conn = sqlite3.connect('hospital.db')
	cursor = conn.cursor()

	params = (username, )
	cursor.execute('SELECT * FROM staff WHERE login=?', params)

	# If there were no results we can add this user
	if len(cursor.fetchall()) == 0:
		# Create password hash
		passHash = hashlib.sha224(password).hexdigest()

		# Create the query to store this users data
		sql = '''INSERT INTO staff(role, name, login, password)
				 VALUES (?, ?, ?, ?)'''
		params = (role, name, username, str(passHash))
		cursor.execute(sql, params)
		conn.commit()
		waiting2 = False

	# Another user already has that username
	else: 
		print("Username already exists! Please try again.")
conn.close()