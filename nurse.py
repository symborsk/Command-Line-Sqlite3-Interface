import sqlite3
import random
from string import ascii_uppercase, digits, ascii_lowercase

#main function call 
def InitializeNurseMenu(name, s_id):
	global staff_name
	global staff_id
	global conn
	global cursor

	staff_name = name
	staff_id = s_id
	conn = sqlite3.connect('hospital.db')
	cursor = conn.cursor()

	NurseMenu()

def NurseMenu():
	print("Welcome Nurse %s to the nursing department. Please type .home at any point to return to this main screen." %(staff_name))
	
	waiting_selection = True
	while waiting_selection:
		sel = raw_input("\nWhat would you like to do?\n1. Create Chart\n2. Close Chart\n3. List Charts for patient\n4. Add Symptom to Chart\n5. Logout\n")

		if sel == "1": 
			CreateChartPreCheck()
		elif sel == "2":
			CloseChart()
		elif sel == "3":
			ListChartsPreCheck()
		elif sel == "4":
			AddSymptonPreCheck()
		elif sel == "5":
			conn.close()	
			return
		else:
			print("Invalid selection try again")

def CreateChartPreCheck():
	health_care_no = raw_input("\nWhat is the patient health care no: ")
	if(health_care_no == ".home"):
		return

	# find all of the open tables of th
	cursor.execute('SELECT p.name, c.chart_id FROM charts c, patients p WHERE ddate IS NULL and c.hcno = p.hcno and c.hcno = ?', (health_care_no, ))
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
		cursor.execute('UPDATE charts set ddate = date(?) where chart_id = ?', params)
		conn.commit()

	CreateChart(health_care_no)

def CreateChart(healthNo):
	chartId = GenerateRandomChartId()
	cursor.execute('SELECT * from patients where hcno = ?', (healthNo, ))

	res = cursor.fetchall()
	if(len(res) == 0):
		print("\nPatient is not in the system adding him now: ")
		
		name = raw_input("\nplease enter patients name: ")
		if(name == ".home"):
			return
		
		age_group = raw_input("\nplease enter patients age group: ")
		if(name == ".home"):
			return
		
		address = raw_input("\nplease enter patient's address: ")
		if(name == ".home"):
			return
		
		phone_number = raw_input("\nplease enter patient's phone number(1112223333): ")
		while(len(phone_number) != 10 or not phone_number.isdigit()):
			if(phone_number == ".home"):
				return
			print("incorrect phone number format please re enter")
			phone_number = raw_input("\nplease enter patient's phone number(1112223333): ")
		
		emg_number = raw_input("\nplease enter patient's  emergency phone number((1112223333): ")
		while(len(emg_number) != 10 or not emg_phone_number.isdigit()):
			if(emg_number == ".home"):
				return
			print("incorrect phone number format please re enter")
			emg_number = raw_input("\n please enter patient's phone number(1112223333): ")
		
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

def CloseChartPreCheck():
	health_care_no = raw_input("\nWhat is the patient health care no: ");
	if(health_care_no == ".home"):
		return

	# find all of the open tables of th
	cursor.execute('SELECT p.name, c.chart_id FROM charts c, patients p WHERE ddate IS NULL and c.hcno = p.hcno and c.hcno = ?', (health_care_no, ))
	res = cursor.fetchall()
	
	# this means that  there is already an open table for that patient
	if len(res) == 1:
		params = ('now', res[0][1])
		cursor.execute('UPDATE charts set ddate = date(?) where chart_id = ?', params)
		conn.commit()
		waiting_selection = False
		print("\nChart closed.")
	else:
		print("Patient with that health care number does not have any open charts.")

def GenerateRandomChartId():

	while True:
		random_key = "".join(random.choice(ascii_uppercase + ascii_lowercase + digits ) for i in range(4))
		cursor.execute('SELECT * from charts where chart_id = ?', (random_key,))
		if(len(cursor.fetchall()) == 0):
			return random_key
