import sqlite3
import random
from string import ascii_uppercase, digits, ascii_lowercase

#main function call end
def initialize():
	print("Welcome to the nursing department")
	waiting_selection = True
	while waiting_selection:
		sel = raw_input("\nWhat would you like to do?\n1. Create Chart\n2. Close Chart\n")

		if sel == "1": 
			CreateChartPreCheck()
			waiting_selection = False
		elif sel == "2":
			CloseChartPreCheck()
		elif sel == "quit":
			return
		else:
			print("Invalid selection try again")

def CreateChartPreCheck():

	health_care_no = raw_input("\nWhat is the patient health care no: ");
	# find all of the open tables of th
	cursor.execute('SELECT p.name, c.chart_id FROM charts c, patients p WHERE edate IS NULL and c.hcno = p.hcno and c.hcno = ?', (health_care_no, ))
	res = cursor.fetchall()
	# this means that  there is already an open table for that patient
	if len(res) == 1:
		
		waiting_selection = True
		while waiting_selection:
			string = ("\nTable open already for patient {} with health care no {} would you like to close it Y/N: ").format( res[0][0], health_care_no)
			sel = raw_input(string)
			
			if sel.lower() =="n":
				print("cancelling chart creation\n")
				initialize()
			elif sel.lower() == "y":
				waiting_selection = False
			else:
				print("Invalid selection try again")

		
		params = ('now', res[0][1])
		cursor.execute('UPDATE charts set edate = date(?) where chart_id = ?', params)
		conn.commit()

	CreateTable(health_care_no)

def CreateTable(healthNo):
	chartId = GenerateRandomChartId()
	cursor.execute('SELECT * from patients where hcno = ?', (healthNo, ))

	res = cursor.fetchall()
	if(len(res) == 0):
		print("\nPatient is not in the system adding him now: ")
		name = raw_input("\nplease enter patients name: ")
		age_group = raw_input("\nplease enter patients age group: ")
		address = raw_input("\nplease enter patient's address: ")
		phone_number = raw_input("\nplease enter patient's phone number(XXXYYYZZZZ): ")
		while(len(phone_number) != 10):
			print("incorrect phone number format please re enter")
			phone_number = raw_input("\nplease enter patient's phone number(XXXYYYZZZZ): ")
		emg_number = raw_input("\nplease enter patient's  emergency phone number((XXXYYYZZZZ): ")
		while(len(emg_number) != 10):
			print("incorrect phone number format please re enter")
			emg_number = raw_input("\n please enter patient's phone number(XXXYYYZZZZ): ")
		params = (healthNo, name, age_group, address, phone_number, emg_number)
		cursor.execute('INSERT into patients(hcno, name, age_group, address, phone, emg_phone) VALUES(?,?,?,?,?,?)', params)

	#create table
	params = (chartId, healthNo, 'now')
	InsertChartTableIntoDB(params)

def InsertChartTableIntoDB(params):
		cursor.execute('INSERT into charts(chart_id, hcno, adate) VALUES( ?, ?, date(?))', params)
		conn.commit()
		string = ("\nChart {} created for patient with hcno {}").format(params[0], params[1])
		print(string)

def GenerateRandomChartId():

	while True:
		random_key = "".join(random.choice(ascii_uppercase + ascii_lowercase + digits ) for i in range(4))
		cursor.execute('SELECT * from charts where chart_id = ?', (random_key,))
		if(len(cursor.fetchall()) == 0):
			return random_key

def CloseChart():
	
	health_care_no = raw_input("\nWhat is the patient health care no: ");
	# find all of the open tables of th
	cursor.execute('SELECT p.name, c.chart_id FROM charts c, patients p WHERE edate IS NULL and c.hcno = p.hcno and c.hcno = ?', (health_care_no, ))
	res = cursor.fetchall()
	# this means that  there is already an open table for that patient
	if len(res) == 1:
		params = ('now', res[0][1])
		cursor.execute('UPDATE charts set edate = date(?) where chart_id = ?', params)
		conn.commit()
		waiting_selection = False
		print("\nChart closed.")
	else:
		print("Patient with that health care number does not have any open charts.")

	initialize()

#main program
global waiting_selection
#connect to the database
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()
initialize()

conn.close()


