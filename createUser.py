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
print("Please enter your name")
name = str(raw_input(">>"))
while waiting1:
	print("Please enter your role (Doctor:D Nurse:N Administrator:A)")
	role = str(raw_input(">>"))
	# Check role value
	if role.lower() == "d" or role.lower() == "n" or role.lower() == "a":
		waiting1= False
	else:
		print("Please enter a proper role.")

while waiting2: 
	print("Please enter a username: ")
	username = str(raw_input(">>"))
	print("Please enter a password")
	password = str(getpass.getpass(">>"))

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
