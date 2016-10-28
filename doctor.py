import sqlite3
import time

global HOME
HOME = ".home"

global conn
global cursor
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

class Doctor:
	
	def __init__(this, n, sid):
		this.staff_id  = sid
		this.staff_name = n
	
	# Main doctor menu
	def doctorMenu(this):
		print("\nWelcome Doctor %s to the doctor department. Please type .home at any point to return to this main screen." %(this.staff_name))

		# Present doctor with their options
		print("\nWhat would you like to do?")
		while True:
			print("1. Search patient records \n2. Edit open chart \n3. Log out")
			sel = raw_input(">> ")
			if sel=='3':
				conn.close()
				return None
			elif sel=='1':
				return this.searchPatientRecords()
			elif sel=='2':
				return this.editOpenChart()
			else: 
				print("Please make a valid selection.\nWhat would you like to do?")

	# Option functions
	def editOpenChart(this):
		# Get the user to select an open chart
		chart = this.getOpenChart()
		if chart==-1: return None
		elif chart==-2: return this.doctorMenu()

		# Add a line for the chart
		return this.addLine(chart[1], chart[0])

	def searchPatientRecords(this):
		# Get the desired patient
		global patient
		global chartList
		patient, chartList = this.getPatientData()
		if patient==-1: return this.doctorMenu()

		# Display the chartList
		this.displayCharts(chartList)

		# Allow user to select a chart
		chart = this.getChart(chartList)
		if chart==-1: return this.displayRecords(patient, chartList)

		# Get and display chart data
		options = this.prepChart(chart)
		lineList = this.getLineList(patient[0], chart[0])
		lineList = sorted(lineList, key = lambda x: x[4])
		chartData = this.getChartString(lineList)
		print(chartData)

		# Handle users next input
		return this.chartMenu(chart, options)


	''' User Input Functions '''
	# For searching patient records
	def getPatientData(this):
		# Make sure we get valid data
		while True:
			print("\nPlease input a health care number: ")
			sel = raw_input(">> ").lower()
			if sel==HOME: return -1, -1

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
	def getChart( chartList):
		# Get valid input
		while True:
			print("\nPlease enter a chart id:")
			sel = raw_input(">> ").lower()
			
			if sel==HOME:
				return -1

			# Check if chart was in chartList
			for chart in chartList:
				if sel==chart[0]:
					return chart

			print("You entered an invalid chart id.")

	# For selecting a specific open chart
	def getOpenChart(this):
		# Get valid input
		while True:
			print("\nPlease enter an open chart id:")
			sel = raw_input(">> ").lower()

			if sel==HOME:
				return -1

			# Perform query
			sql = '''SELECT * FROM charts WHERE chart_id=? AND ddate IS NULL'''
			params = (sel, )
			selChart = cursor.execute(sql, params).fetchall()

			# Check if there was a chart
			if len(selChart)>0:
				return selChart[0]
			print("You entered an invalid chart id.")


	''' Display Functions '''
	# Handles user picking another chart
	def displayRecords(this, patient, chartList):
		# Display the chartList
		displayCharts(chartList)

		# Allow user to select a chart
		chart = getChart(chartList)
		if chart==-1: return this.doctorMenu()

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
		
		# Build header strings / options list
		if isClosed==None:
			barrier = '\n------------------------------------------'
			chartStr = " CHART ID | HCNO     | Admission Date" + '\n ' + selChart[0].ljust(8) + ' | ' + str(selChart[1]).ljust(8) + ' | ' + selChart[2].ljust(19) + barrier + next
			options.append('1. Add a line')
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


	''' Medication Check Functions '''
	def amountCheck (this, hcno, amount, drug_name):
		# Get patient age group
		sql = '''SELECT age_group FROM patients WHERE hcno=?'''
		params = (hcno, )
		age_group = str(cursor.execute(sql, params).fetchone()[0])

		# Get drug dosage data
		sql = '''SELECT sug_amount FROM dosage WHERE age_group=? AND drug_name=?'''
		params = (age_group, drug_name)
		sug_amount = int(cursor.execute(sql, params).fetchone()[0])

		# Handle check cases
		if amount > sug_amount:
			while True:
				print("\nYou have entered an amount greater than the suggested amount of " + str(sug_amount) + ".")
				print("Would you like to change the amount, continue or cancel?\n(Change = C, Continue = Y, Cancel = N)")
				choice = raw_input(">> ").lower()
				if choice==HOME:
					return 0
				elif choice=='c':
					print("Please select the new amount: ")
					return this.amountCheck(hcno, int(raw_input(">> "), drug_name))
				elif choice=='y':
					return True
				elif choice=='n':
					return False
				print("Please make a valid choice.")
		return True

	def allergyCheck( hcno, drug_name):
		sql = '''SELECT drug_name FROM reportedallergies WHERE hcno=?'''
		params = (hcno, )
		allergicList = cursor.execute(sql, params).fetchall()
		drugList = list()
		for al in allergicList:
			drugList.append(str(al[0]))
		# Check if patient is allergic to drug
		if drug_name in drugList:
			# Get valid input
			while True:
				print("You have entered a drug this patient is allergic to: " + drug_name)
				print("Would you like to proceed? (Y/n)")
				sel = raw_input(">> ").lower()
				if sel==HOME:
					return 0
				elif sel=='y':
					return True
				elif sel=='n':
					return False
				print("Please enter a valid response.")
		# Check if patient may be allergic to drug
		else:
			causedInferred = list()
			for drug in drugList:
				sql = '''SELECT * FROM inferredallergies WHERE alg=?'''
				params = (drug, )
				if len(cursor.execute(sql, params).fetchall())>0:
					causedInferred.append(drug)

			# No inferred allergies
			if len(causedInferred)==0:
				return True
			else:
				# Loop until we get a proper response from user
				while True:
					print("\nDue to the patients reported allergies of: ")
					for d in causedInferred: print(d)
					print("They may be allergic to " + drug_name + ".")
					print("Would you like to proceed? (Y/n)")
					sel = raw_input(">> ").lower()
					if sel==HOME:
						return 0
					elif sel=='y':
						return True
					elif sel=='n':
						return False
					print("Please make a valid selection.")


	''' Chart Edit Functions '''

	def addSymptom (this, hcno, chart_id):
		# Get the symptom
		print("\nPlease input the symptom:")
		symptom = raw_input(">> ").lower()
		if symptom==HOME:
			print("Line not added")
			return this.doctorMenu()

		# Add the symptom
		sql = '''INSERT INTO symptoms VALUES (?, ?, ?, ?, ?)'''
		params = (hcno, chart_id, this.staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), symptom)
		cursor.execute(sql, params)
		conn.commit()
		return this.lineMenu(hcno, chart_id)

	def addDiagnosis (this, hcno, chart_id):
		# Get diagnosis info
		print("\nPlease input the diagnosis")
		diagnosis = raw_input(">> ").lower()
		if diagnosis==HOME:
			print("Line not added.")
			return this.doctorMenu()

		# Add the diagnosis
		sql = '''INSERT INTO diagnoses VALUES (?, ?, ?, ?, ?)'''
		params = (hcno, chart_id, this.staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), diagnosis)
		cursor.execute(sql, params)
		conn.commit()
		return this.lineMenu(hcno, chart_id)

	def addMedication ( hcno, chart_id):
		# Get medication info
		print("\nPlease enter the medication start date: ")
		start = raw_input(">> ")
		print("Please enter the medication end date: ")
		end = raw_input(">> ")
		print("Please enter the daily amount: ")
		amount = int(raw_input(">> "))
		print("Please enter the drug name: ")
		drug_name = raw_input(">> ").lower()
		
		# If both tests pass we can add the medication
		test1 = this.amountCheck(hcno, amount, drug_name)
		test2 = this.allergyCheck(hcno, drug_name)
		if  test1 and test2:
			sql = '''INSERT INTO medications VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
			params = (hcno, chart_id, this.staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), start, end, amount, drug_name)
			cursor.execute(sql, params)
			conn.commit()
		else: print("Line was not added.")

		# Return to home
		if test1==0 or test2 ==0:
			return this.doctorMenu()

		return this.lineMenu(hcno, chart_id)

	def addLine (this, hcno, chart_id):
		# Loop continuously until we receive proper input
		while True:
			print("\nWhat kind of line would you like to enter?")
			print("S = Symptom \nD = Diagnosis \nM = Medication")
			sel = raw_input(">> ").lower()
			if sel==HOME:
				return this.doctorMenu()
			elif sel=='s':
				return this.addSymptom(hcno, chart_id)
			elif sel=='d':
				return this.addDiagnosis(hcno, chart_id)
			elif sel=='m':
				return this.addMedication(hcno, chart_id)
			print("Please make a valid selection.")


	''' Other Menu functions '''

	# Menu after adding line
	def lineMenu (this, hcno, chart_id):
		while True:
			print("\nWhat would you like to do?")
			print("1. Add another line \n2. Return to home")
			sel = raw_input(">> ").lower()
			if sel==HOME or sel=='2':
				return this.doctorMenu()
			elif sel=='1':
				return this.addLine(hcno, chart_id)

	# Menu after chart selection
	def chartMenu(this, chart, options):
		while True:
			# Present user with options
			print("\nWhat would you like to do?")
			for op in options:
				print op

			sel = raw_input(">> ").lower()
			
			if sel==HOME:
				return this.doctorMenu()

			# Handle closed chart input
			if len(options)==2:
				if sel=='1':
					return this.searchPatientRecords()
				elif sel=='2':
					return this.doctorMenu()
				print("Please make a valid selection.")
			# Handle open chart input
			else:
				if sel=='1':
					return this.addLine(patient[0], chart[0])
				elif sel=='2':
					return this.searchPatientRecords()
				elif sel=='3':
					return this.doctorMenu()

			print("Please make a valid selection.")
