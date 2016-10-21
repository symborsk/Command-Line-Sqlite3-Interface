import sqlite3
import time
import getpass

# Returns true if amount check passes, false if it fails
def amountCheck ( hcno, amount, drug_name):
	sql = '''SELECT age_group FROM patients WHERE hcno=?'''
	params = (hcno, )
	age_group = str(cursor.execute(sql, params).fetchone()[0])

	sql = '''SELECT sug_amount FROM dosage WHERE age_group=? AND drug_name=?'''
	params = (age_group, drug_name)
	sug_amount = int(cursor.execute(sql, params).fetchone()[0])
	if amount > sug_amount:
		while True:
			print("You have entered an amount greater than the suggested amount of " + str(sug_amount) + ".")
			print("Would you like to continue? (Y/n)")
			choice = raw_input(">> ")
			if choice.lower()=='y':
				return True
			elif choice.lower()=='n':
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
		while True:
			print("You have entered a drug this patient is allergic to: " + drug_name)
			print("Would you like to proceed? (Y/n)")
			sel = raw_input(">> ")
			if sel.lower()=='y':
				return True
			elif sel.lower()=='n':
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

		if len(causedInferred)==0:
			return True
		else:
			while True:
				print("\nDue to the patients reported allergies of: ")
				for d in causedInferred: print(d)
				print("They may be allergic to " + drug_name + ".")
				print("Would you like to proceed? (Y/n)")
				sel = raw_input(">> ").lower()
				if sel=='y':
					return True
				elif sel=='n':
					return False
				print("Please make a valid selection.")

def addSymptom ( hcno, chart_id):
	print("\nPlease input the symptom:")
	symptom = raw_input(">> ")
	sql = '''INSERT INTO symptoms VALUES (?, ?, ?, ?, ?)'''
	params = (hcno, chart_id, staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), symptom)
	cursor.execute(sql, params)
	conn.commit()

def addDiagnosis ( hcno, chart_id):
	print("\nPlease input the diagnosis")
	diagnosis = raw_input(">> ")
	sql = '''INSERT INTO diagnoses VALUES (?, ?, ?, ?, ?)'''
	params = (hcno, chart_id, staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), diagnosis)
	cursor.execute(sql, params)
	conn.commit()

def addMedication ( hcno, chart_id):
	print("\nPlease enter the medication start date: ")
	start = raw_input(">> ")
	print("Please enter the medication end date: ")
	end = raw_input(">> ")
	print("Please enter the daily amount: ")
	amount = int(raw_input(">> "))
	print("Please enter the drug name: ")
	drug_name = raw_input(">> ")
	
	# If both tests pass we can add the medication
	if amountCheck(hcno, amount, drug_name) and allergyCheck(hcno, drug_name):
		sql = '''INSERT INTO medications VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
		params = (hcno, chart_id, staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), start, end, amount, drug_name)
		cursor.execute(sql, params)
		conn.commit()

def addLine( hcno, chart_id):
	while True:
		print("\nWhat kind of line would you like to enter?")
		print("S = Symptom \nD = Diagnosis \nM = Medication")
		sel = raw_input(">> ").lower()
		if sel=='s':
			addSymptom(hcno, chart_id)
			waiting6 = False
			break
		elif sel=='d':
			addDiagnosis(hcno, chart_id)
			waiting6 = False
			break
		elif sel=='m':
			addMedication(hcno, chart_id)
			waiting6 = False
			break
		elif sel=='<':
			waiting6 = False
			break
		print("Please make a valid selection.")

def getChartList():
	while True:
		# Get HCNO
		print("\nPlease enter the desired patient health care number: ")
		hcno = raw_input(">> ")
				
		# Check for return key
		if hcno=="<":
			return None
		hcno = int(hcno)

		# Execute the query
		sql = '''SELECT * FROM charts WHERE hcno=? ORDER BY adate DESC'''
		params = (hcno, )
		cursor.execute(sql, params)

		# Display the resultsc
		chartList = cursor.fetchall()
		if len(chartList)>0:
			return chartList
		print("Could not find records for that patient. Please try again.")

def displayCharts( chartList):
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

def displayChartHeader(selChart):
	# Get parameters based on open/closed chart
	isClosed = selChart[3]
	options = list()
	if isClosed==None:
		barrier = '\n--------------------------------------'
		chartStr = " CHART ID | HCNO     | Admission Date" + '\n ' + selChart[0].ljust(8) + ' | ' + str(selChart[1]).ljust(8) + ' | ' + selChart[2].ljust(19) + barrier 
		options.append('1. Add a line')
		options.append('2. Search for another chart')
		options.append('3. Return to home')
	else:
		barrier = '\n----------------------------------------------------------'
		chartStr = " CHART ID | HCNO     | Admission Date      | Departure Date\n " + selChart[0].ljust(8) + ' | ' + str(selChart[1]).ljust(8) + ' | ' + selChart[2].ljust(19) + ' | ' + selChart[3].ljust(19)+ barrier
		options.append('1. Search for another chart')
		options.append('2. Return to home')
	print(chartStr)
	return options

def handleChartInput( options):
	# Handle user input
	while True:
		print("\nPlease select an option")
		for op in options:
			print(op)
		sel = raw_input(">> ")

		# Handle chart dependant cases
		if len(options)==2:
			# Search pressed
			if sel=='1':
				return True
			# Return pressed
			elif sel=='2':
				return False
			else:
				print("Please select a proper option.")

		else:
			# Add Line pressed
			if sel=='1':
				addLine(selChart[1], selChart[0])

				# Handle next input
				while True:
					print("\nWhat would you like to do?\n1. Add another line \n2. Search for another chart \n3. Return to home")
					sel = raw_input(">> ")
					if sel=='1':
						break
					elif sel=='2':
						return True
					elif sel=='3':
						return False
					print("Please make a valid selection.")

			# Search pressed
			elif sel=='2':
				return True
			# Return pressed
			elif sel=='3':
				return False
			else: print("Please select a proper option.")

def getOpenChart():
	while True:
		print("\nPlease enter an open chart id:")
		sel = raw_input(">> ")

		if sel=="<": return None

		sql = '''SELECT * FROM charts WHERE chart_id=? AND ddate IS NULL'''
		params = (sel, )
		selChart = cursor.execute(sql, params).fetchall()

		if len(selChart)>0:
			return selChart[0]
		print("You entered an invalid chart id.")

def getChart( chartList):
	while True:
		print("\nPlease enter a chart id:")
		sel = raw_input(">> ")
		
		if sel=="<":
			return None

		for chart in chartList:
			if sel in chart:
				return chart

		print("You entered an invalid chart id.")

def getLineString( lineList):
	lineString = str()
	for line in lineList:
		# Create and print line string
		string = line[0]
		for element in line[1:]:
			# Format the element to a uniform length
			element = str(element)
			if len(element)>16:
				element = element.ljust(20)
			elif len(element)>12:
				element = element.ljust(16)
			elif len(element)>8:
				element = element.ljust(12)
			elif len(element)>4:
				element = element.ljust(8)
			else:
				element = element.ljust(4)
			string += '| ' + element
		lineString += string + '\n'

	return lineString

def getLineList( hcno, chart_id):
	# Create sql query
	sql = '''SELECT * FROM {} WHERE hcno=? AND chart_id=? ORDER BY ? DESC'''

	# Create symptom list
	cursor.execute(sql.format('symptoms'), (hcno, chart_id, 'obs_date'))
	sList = cursor.fetchall()
	symList = tuple()
	for sym in sList:
		symList += ((' S ',) + sym, )

	# Create diagnoses list
	cursor.execute(sql.format('diagnoses'), (hcno, chart_id, 'ddate'))
	dList = cursor.fetchall()
	diaList = tuple()
	for dia in dList:
		diaList += ((' D ', ) + dia, )

	# Create medications list
	cursor.execute(sql.format('medications'), (hcno, chart_id, 'mdate'))
	mList = cursor.fetchall()
	medList = tuple()
	for med in mList:
		medList += ((' M ', ) + med, )

	lineList = symList + diaList + medList
	return lineList

# Connect to the database
global conn
global cursor
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()
waiting = True

# Global vars from login
global name
global staff_id

while waiting:
	# Present the user with their options
	name = "Brett" # NAME PASSED FROM LOGIN HERE
	staff_id = 1
	print "\nWelcome,", name, "\nPlease select one of the following: \n1. Search patient records\n2. Edit chart\n3. Log out"

	# Prompt the user for input
	choice = raw_input(">> ")

	# Case 1: Search for patient records
	if choice=='1':
		waiting1=True
		while waiting1:
			# Get chart list for a selected patient
			chartList = getChartList()
			if chartList==None:
				break

			# Allow the user to select a chart
			global selChart
			displayCharts(chartList)
			selChart = getChart(chartList)
			if selChart==None:
				break

			# Display valid chart header and get options
			options = displayChartHeader(selChart)

			''' Sorting all entries by their entry date. Adapted from
			http://stackoverflow.com/questions/20183069/how-to-sort-multidimensional-array-by-column
			on Oct 19 2016'''
			lineList = getLineList(selChart[1], selChart[0])
			lineList = sorted(lineList, key = lambda x: x[4])
			lineString = getLineString(lineList)
			print(lineString)
				
			# Handle users next input
			waiting1 = handleChartInput(options)

	# Case 2: Edit open chart
	elif choice=='2':
		sel = 2
		while sel<3:
			# Get a proper chart from the user
			if sel==2: selChart = getOpenChart()
			if selChart==None:
				break

			# Add line
			addLine(selChart[1], selChart[0])

			# Handle next input
			while True:
				print("\nWhat would you like to do?\n1. Add another line \n2. Edit another chart \n3. Return to home")
				sel = raw_input(">> ")
				if sel=='1':
					break
				elif sel=='2':
					break
				elif sel=='3':
					waiting0 = False
					break
				print("Please make a valid selection.")

	# Case 3: Log out
	elif choice=='3':
		break
	else:
		print("Please make a valid selection")


conn.close()
quit()