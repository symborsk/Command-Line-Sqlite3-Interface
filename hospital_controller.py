import sqlite3
import hashlib
import random
import getpass
from doctor import doctorMenu
from nurse import InitializeNurseMenu
from string import ascii_uppercase, digits, ascii_lowercase

def Login():
	global staff_role
	global staff_id
	global staff_name

	conn = sqlite3.connect('hospital.db')
	cursor = conn.cursor()
	
	waiting = True
	while waiting:
		# Get the user credentials
		print("\nWelcome to the Hospital Record Service.")
		print("Please log in below. (Note: Passwords are case sensitive!)")
		username = raw_input("\nUsername: ")
		password = getpass.getpass("Password: ")
		passHash = hashlib.sha224(password).hexdigest()

		sql = """SELECT staff_id, name, role
					FROM staff
					WHERE login=?
					AND password=?"""
		params = (username, str(passHash))
		cursor.execute(sql, params)
		results = cursor.fetchall();

		if len(results)==1:
			# Get the users attributes
			user = results[0]
			staff_id = user[0]
			staff_name = user[1]
			staff_role = user[2]

			#Set up our global staff information
			waiting = False
			conn.close()
			ForwardMenu()
		else:
			waiting = True
			while waiting:
				userInput  = raw_input("There was an error logging in. Would you like to try again?(y/n)")
				if( userInput.lower() == "y"):
					waiting = False;
				elif( userInput.lower() == "n"):
					print("Exiting program. Goodbye.")
					conn.close()
					return
				else:
					("Please enter a valid input")

def ForwardMenu():

	if( staff_role == "D"):
		#TODO: Doctors menu call
		print("\nWelcome Dr. %s. \nRouting to the doctor menu..." % (staff_name))
		doctorMenu(staff_id, staff_name)
	elif(staff_role =="N"):
		InitializeNurseMenu(staff_name, staff_id)
	elif(staff_role == "A"):
		#Todo: Admin Staff
		print("\nWelcome Admin Staff %s. \nRouting to the admin menu..." % (staff_name))
	else:
		print("\nSomething went wrong please re-login")
	Login()

Login()



