import sqlite3
import random
import time
from string import ascii_uppercase, digits, ascii_lowercase

global HOME
HOME = ".home"

global conn
global cursor
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

class Nurse:

	def __init__(this, name, s_id):
		this.staff_name = name
		this.staff_id = s_id

	def InitializeNurseMenu(this):
		this.NurseMenu()

	#main function call 
	def NurseMenu(this):
		print("\nWelcome Nurse %s to the nursing department. Please type .home at any point to return to this main screen." %(this.staff_name))
		
		waiting_selection = True
		while waiting_selection:
			print("\nWhat would you like to do? \n1. Create Chart \n2. Close Chart \n3. List Charts for patient \n4. Add Symptom to Chart \n5. Logout")
			sel = raw_input(">> ")

			if sel == "1": 
				healthCareNo = this.GetHealthCareNumber()
				this.CreateChart(healthCareNo)
			elif sel == "2":
				this.CloseChart()
			elif sel == "3":
				this.searchPatientRecords()
			elif sel == "4":
				this.editOpenChart()
			elif sel == "5":
				conn.close()	
				return
			else:
				print("Invalid selection try again")

	# Option functions
	def searchPatientRecords(this):
		# Get the desired patient
		global patient
		global chartList
		patient, chartList = this.getPatientData()
		if patient==-1: return 

		# Display the chartList
		this.displayCharts(chartList)

		# Allow user to select a chart
		chart = this.getChart(chartList)
		if chart==-1: return 

		# Get and display chart data
		options = this.prepChart(chart)
		lineList = this.getLineList(patient[0], chart[0])
		lineList = sorted(lineList, key = lambda x: x[4])
		chartData = this.getChartString(lineList)
		print(chartData)

		# Handle users next input
		return this.chartMenu(chart, options)

	def editOpenChart(this):
		# Get the user to select an open chart
		chart = this.getOpenChart()
		if chart==-1: return 

		# Add a line for the chart
		return this.addSymptom(chart[1], chart[0])

	def getPatientData(this):
		# Make sure we get valid data
		while True:
			print("\nPlease input a health care number: ")
			sel = raw_input(">> ").lower()
			if sel == HOME:
				return -1, -1

			else:
				# Check if that patient exists
				sql = '''SELECT * FROM patients WHERE hcno=?'''
				params = (sel, )
				patient = cursor.execute(sql, params).fetchall()
				if len(patient)>0:

					# Check for patient charts
					sql = '''SELECT * FROM charts WHERE hcno=? ORDER BY adate DESC'''
					cursor.execute(sql, params)

					# Return charts if applicable
					chartList = cursor.fetchall()
					if len(chartList)>0:
						return patient[0], chartList
					print("Could not find medical records for that patient. Please try again.")

				else: print("No patient record found. Please try again.")

	# For selecting a specific patient chart
	def getChart(this, chartList):
		while True:
			print("\nPlease enter a chart id:")
			sel = raw_input(">> ")
			
			if sel==HOME:
				return -1

			for chart in chartList:
				if sel==chart[0]:
					return chart

			print("You entered an invalid chart id.")

	# For selecting a specific open chart
	def getOpenChart(this):
		while True:
			print("\nPlease enter an open chart id:")
			sel = raw_input(">> ")

			if sel==HOME:
				return -1

			sql = '''SELECT * FROM charts WHERE chart_id=? AND ddate IS NULL'''
			params = (sel, )
			selChart = cursor.execute(sql, params).fetchall()

			if len(selChart)>0:
				return selChart[0]
			print("You entered an invalid chart id.")

	# Handles user picking another chart
	def displayRecords(this, patient, chartList):
		# Display the chartList
		this.displayCharts(chartList)

		# Allow user to select a chart
		chart = this.getChart(chartList)
		if chart==-1: return 
		# Get and display chart data
		options = this.dislayChartHeader(chart)
		lineList = this.getLineList(patient[0], chart[0])
		lineList = sorted(lineList, key = lambda x: x[4])
		chartData = this.getChartString(lineList)
		print(chartData)

		# Handle users next input
		return this.chartMenu(chart, options)

	# Displays all charts in chartList
	def displayCharts(this, chartList):
		# Show open charts
		print ("\nOpen Charts\nChart # | Admission Date")
		for chart in chartList:
			if chart[3] == None:
				string = chart[0].ljust(7) + ' | ' + chart[2].ljust(14)
				print(string)

		# Show closed charts
		print ("\nClosed Charts\nChart # | Admission Date      | Departure Date")
		for chart in chartList:
			if chart[3] != None:
				string = chart[0].ljust(7) + ' | ' + chart[2].ljust(14) + ' | ' + chart[3]
				print(string)

	# Creates chart header string and user options tuple
	def prepChart(this, selChart):
		# Get parameters based on open/closed chart
		isClosed = selChart[3]
		options = list()
		next = '\n Type | StaffID | Date Added'
		if isClosed==None:
			barrier = '\n------------------------------------------'
			chartStr = " CHART ID | HCNO     | Admission Date" + '\n ' + selChart[0].ljust(8) + ' | ' + str(selChart[1]).ljust(8) + ' | ' + selChart[2].ljust(19) + barrier + next
			options.append('1. Add a symptom')
			options.append('2. Search for another chart')
			options.append('3. Return to home')
		else:
			barrier = '\n----------------------------------------------------------'
			chartStr = " CHART ID | HCNO     | Admission Date      | Departure Date\n " + selChart[0].ljust(8) + ' | ' + str(selChart[1]).ljust(8) + ' | ' + selChart[2].ljust(19) + ' | ' + selChart[3].ljust(19)+ barrier + next
			options.append('1. Search for another chart')
			options.append('2. Return to home')
		print(chartStr)
		return options

	# String of all chart data
	def getChartString(this, lineList):
		lineString = str()
		for line in lineList:
			# Create and print line string
			string = line[0]
			for element in line[3:]:
				# Format the element to a uniform length
				element = str(element)
				if len(element)>16:
					element = element.ljust(20)
				elif len(element)>12:
					element = element.ljust(16)
				elif len(element)>8:
					element = element.ljust(12)
				else:
					element = element.ljust(8)
				string += '| ' + element
			lineString += string + '\n'

		return lineString

	# Get list of all chart lines
	def getLineList(this, hcno, chart_id):
		# Create sql query
		sql = '''SELECT * FROM {} WHERE hcno=? AND chart_id=? ORDER BY ? DESC'''

		# Create symptom list
		cursor.execute(sql.format('symptoms'), (hcno, chart_id, 'obs_date'))
		sList = cursor.fetchall()
		symList = tuple()
		for sym in sList:
			symList += (('  S   ',) + sym, )

		# Create diagnoses list
		cursor.execute(sql.format('diagnoses'), (hcno, chart_id, 'ddate'))
		dList = cursor.fetchall()
		diaList = tuple()
		for dia in dList:
			diaList += (('  D   ', ) + dia, )

		# Create medications list
		cursor.execute(sql.format('medications'), (hcno, chart_id, 'mdate'))
		mList = cursor.fetchall()
		medList = tuple()
		for med in mList:
			medList += (('  M   ', ) + med, )

		lineList = symList + diaList + medList
		return lineList

	def addSymptom (this, hcno, chart_id):
		print("\nPlease input the symptom:")
		symptom = raw_input(">> ")
		if symptom==HOME:
			print("Line not added")
			return 
		sql = '''INSERT INTO symptoms VALUES (?, ?, ?, ?, ?)'''
		params = (hcno, chart_id, this.staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), symptom)
		cursor.execute(sql, params)
		conn.commit()
		return this.lineMenu(hcno, chart_id)

	# Menu after adding line
	def lineMenu (this, hcno, chart_id):
		while True:
			print("\nWhat would you like to do?")
			print("1. Add another symptom \n2. Return to home")
			sel = raw_input(">> ").lower()
			if sel==HOME or sel=='2':
				return 
			elif sel=='1':
				return this.addSymptom(hcno, chart_id)

	# Menu after chart selection
	def chartMenu(this, chart, options):
		while True:
			# Present user with options
			print("\nWhat would you like to do?")
			for op in options:
				print op

			sel = raw_input(">> ").lower()
			
			# Handle special keys
			if sel==HOME:
				return 

			# Handle closed chart input
			if len(options)==2:
				if sel=='1':
					return this.searchPatientRecords()
				elif sel=='2':
					return 
				print("Please make a valid selection.")
			# Handle open chart input
			else:
				if sel=='1':
					return this.addSymptom(patient[0], chart[0])
				elif sel=='2':
					return this.searchPatientRecords()
				elif sel=='3':
					return 

			print("Please make a valid selection.")

	# Find the user input and compare it to see if it has any open charts
	# If there is already an open table give the user the option to close it
	def GetHealthCareNumber(this):
		print("\nWhat is the patient health care no: ")
		health_care_no = raw_input(">> ")
		if(health_care_no ==  HOME):
			return

		# find all of the open tables of th
		cursor.execute('SELECT p.name, c.chart_id FROM charts c, patients p WHERE ddate IS NULL and c.hcno = p.hcno and c.hcno = ?', (health_care_no, ))
		res = cursor.fetchall()
		# this means that  there is already an open table for that patient
		if len(res) == 1:
			
			waiting_selection = True
			while waiting_selection:
				print(("\nTable open already for patient {} with health care no {} would you like to close it Y/N: ").format( res[0][0], health_care_no))
				sel = raw_input(">> ")
				
				if sel.lower() =="n":
					print("Cancelling chart creation\n")
					initialize()
				elif sel.lower() == "y":
					waiting_selection = False
				else:
					print("Invalid selection try again")

			
			params = ('now', res[0][1])
			cursor.execute('UPDATE charts set ddate = datetime(?) where chart_id = ?', params)
			conn.commit()

		return health_care_no

	#Create a new open chart for patient of health care no healthNo
	#If that patient doesnt exist create it first
	def CreateChart(this, healthNo):
		chartId = this.GenerateRandomChartId()
		cursor.execute('SELECT * from patients where hcno = ?', (healthNo, ))

		res = cursor.fetchall()
		if(len(res) == 0):
			this.CreatePatient(healthNo)
		
		#create table
		params = (chartId, healthNo, 'now')
		this.InsertChartTableIntoDB(params)

	#Create a patient with health care number healthNo
	def CreatePatient(this, healthNo):
			print("\nPatient is not in the system, adding him now...")
			
			print("What is the patient's name: ")
			name = raw_input(">> ")
			if(name == HOME):
				return
			
			print("Please enter the patient's age group: ")
			age_group = raw_input(">> ")
			if(name == HOME):
				return
			
			print("Please enter the patient's address")
			address = raw_input(">> ")
			if(name == HOME):
				return
			
			print("Please enter the patient's phone number (1112223333): ")
			phone_number = raw_input(">> ")
			while(len(phone_number) != 10 or not phone_number.isdigit()):
				if(phone_number == HOME):
					return
				print("Incorrect phone number format, please try again.")
				print("Please enter the patient's phone number (1112223333):")
				phone_number = raw_input(">> ")
			
			print("Please enter the patient's emergency contact number (1112223333):")
			emg_number = raw_input(">> ")
			while(len(emg_number) != 10 or not emg_number.isdigit()):
				if(emg_number == HOME):
					return
				print("Incorrect phone number format, please try again.\nPlease enter patient's emergency contact number(1112223333): ")
				emg_number = raw_input(">> ")
			
			params = (healthNo, name, age_group, address, phone_number, emg_number)
			cursor.execute('INSERT into patients(hcno, name, age_group, address, phone, emg_phone) VALUES(?,?,?,?,?,?)', params)
			conn.commit()

	#Insert tuple params in chart table in DB
	def InsertChartTableIntoDB(this, params):
			cursor.execute('INSERT into charts(chart_id, hcno, adate) VALUES( ?, ?, datetime(?))', params)
			conn.commit()
			string = ("\nChart {} created for patient with hcno {}").format(params[0], params[1])
			print(string)

	#Ask the user a for a health care no. and then close any open table with that value
	def CloseChart(this):
		print("\nPlease enter the patient's health care number: ")
		health_care_no = raw_input(">> ");
		if(health_care_no == ".home"):
			return

		# find all of the open tables of th
		cursor.execute('SELECT p.name, c.chart_id FROM charts c, patients p WHERE ddate IS NULL and c.hcno = p.hcno and c.hcno = ?', (health_care_no, ))
		res = cursor.fetchall()
		
		# this means that  there is already an open table for that patient
		if len(res) == 1:
			cursor.execute('UPDATE charts set ddate = datetime() where chart_id = ?', (res[0][1], ))
			conn.commit()
			waiting_selection = False
			print("\nChart closed.")
		else:
			print("Patient with that health care number does not have any open charts.")

	#Generate a random chart ID for primary key of chart
	def GenerateRandomChartId(this):

		while True:
			random_key = "".join(random.choice(ascii_uppercase + ascii_lowercase + digits ) for i in range(4))
			cursor.execute('SELECT * from charts where chart_id = ?', (random_key,))
			if(len(cursor.fetchall()) == 0):
				return random_key
