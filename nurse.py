import sqlite3

#main function call end
def initialize():
	print("Welcome to the nursing department")
	while waiting_selection:
		sel = raw_input("\nWhat would you like to do? (Create Chart : CO, Close Chart : CC ): ")

		if sel == "CO": 
			CreateChart()
		else:
			print("Invalid selection try again")

def CreateChart():

	health_care_no = raw_input("\nCreating chart... what is the patient health care no: ");

	#connect to the database
	conn = sqlite3.connect('hospital.db')
	cursor = conn.cursor()

	# find all of the open tables of th
	cursor.execute('SELECT p.name as a, c.chart_id as b FROM charts c, patients p WHERE edate IS NULL and c.hcno = p.hcno and c.hcno = ?' , health_care_no);
	res = cursor.fetchall()

	# this means that  there is already an open table for that patient
	if len(res) != 0:
		
		waiting_selection = True
		while waiting_selection:
			string = ("\nTable open already for patient {} would you like to close it Y/N: ").format( res[0][1])
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

		#TODO: add option to create a charte

waiting_selection = True
initialize()


