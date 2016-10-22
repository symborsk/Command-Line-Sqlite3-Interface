import sqlite3
import hashlib
import getpass
import random
from string import ascii_uppercase, digits, ascii_lowercase




def GenerateRandomStaffId():
	while True:
		random_key = "".join(random.choice(ascii_uppercase + ascii_lowercase + digits ) for i in range(5))
		cursor.execute('SELECT * from staff where staff_id = ?', (random_key,))
		if(len(cursor.fetchall()) == 0):
			return random_key


waiting1 = True
waiting2 = True

conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

print("\nWelcome to the Hospital User Creation Service.")
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
	password = str(getpass.getpass("Please enter a password: ")) 
	
	params = (username, )
	cursor.execute('SELECT * FROM staff WHERE login=?', params)

	# If there were no results we can add this user
	if len(cursor.fetchall()) == 0:
		# Create password hash
		passHash = hashlib.sha224(password).hexdigest()

		StaffId = GenerateRandomStaffId()
		# Create the query to store this users data
		sql = '''INSERT INTO staff(staff_id, role, name, login, password)
				 VALUES (?, ?, ?, ?, ?)'''
		params = (StaffId, role, name, username, str(passHash))
		cursor.execute(sql, params)
		conn.commit()
		waiting2 = False

	# Another user already has that username
	else: 
		print("Username already exists! Please try again.")
conn.close()
