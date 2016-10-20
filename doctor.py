import sqlite3
import time

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





def addSymptom ( hcno, chart_id, symptom):
	sql = '''INSERT INTO symptoms VALUES (?, ?, ?, ?, ?)'''
	params = (hcno, chart_id, staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), symptom)
	cursor.execute(sql, params)
	conn.commit()

def addDiagnosis ( hcno, chart_id, diagnosis):
	sql = '''INSERT INTO diagnoses VALUES (?, ?, ?, ?, ?)'''
	params = (hcno, chart_id, staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), diagnosis)
	cursor.execute(sql, params)
	conn.commit()

def addMedication ( hcno, chart_id, start, end, amount, drug_name):
	# If both tests pass we can add the medication
	if amountCheck(hcno, amount, drug_name) and allergyCheck(hcno, drug_name):
		sql = '''INSERT INTO medications VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
		params = (hcno, chart_id, staff_id, time.strftime("%Y-%m-%d %H:%M:%S"), start, end, amount, drug_name)
		cursor.execute(sql, params)
		conn.commit()


# Connect to the database
global conn
global cursor
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()
waiting0 = True

# Global vars from login
global name
global staff_id

while waiting0:
	# Present the user with their options
	name = "Brett" # NAME PASSED FROM LOGIN HERE
	staff_id = 1
	print "\nWelcome,", name, '''\nPlease select one of the following: 
\n1. Search patient records
2. Edit chart
3. Change password
4. Log out'''

	# Prompt the user for input
	choice = raw_input(">> ")

	# Handle the users input
	waiting1 = True
	while waiting1:
		if choice=='1':
			waiting1 = False;

			# Determine which patient the user needs charts for
			print("\nPlease enter the desired patient health care number: ")
			hcno = int(raw_input(">> "))

			if hcno=="<":
				break
			
			# Execute the query
			sql = '''SELECT chart_id, adate, edate
FROM charts
WHERE hcno=?
ORDER BY adate DESC'''
			params = (hcno, )
			cursor.execute(sql, params)

			# Display the resultsc
			chartList = cursor.fetchall()

			# Show open charts
			print ("\nOpen Charts\nChart # | Admission Date")
			for chart in chartList:
				if chart[2] == None:
					string = chart[0].ljust(7) + ' | ' + chart[1].ljust(14)
					print(string)

			# Show closed charts
			print ("Closed Charts\nChart # | Admission Date | Departure Date")
			for chart in chartList:
				if chart[2] != None:
					string = chart[0].ljust(7) + ' | ' + chart[1].ljust(14) + ' | ' + chart[2]
					print(string)

			# Allow the user to select a chart
			waiting2 = True
			viewID = None
			global selChart
			while waiting2:
				print("\nSelect the chart number you want to view:")
				chart_id = raw_input(">> ")
				if chart_id=="<":
					waiting1 = True
					break;
				for chart in chartList:
					if chart[0]==chart_id:
						viewID = chart[0]
						selChart = chart
						waiting2 = False
						print("")
				if waiting2: print("Please select a proper chart number.")

			chartStr = " CHART ID | HCNO     | Admission Date" + '\n ' + selChart[0].ljust(8) + ' | ' + str(hcno).ljust(8) + ' | ' + selChart[1] 
			print(chartStr)

			# Display the medical information for the selected chart
			sql = '''SELECT *
FROM {}
WHERE hcno=?
AND chart_id=?
ORDER BY ? DESC'''
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

			''' Sorting all entries by their entry date. Adapted from
			http://stackoverflow.com/questions/20183069/how-to-sort-multidimensional-array-by-column
			on Oct 19 2016'''
			lineList = symList + diaList + medList
			lineList = sorted(lineList, key = lambda x: x[4])
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
			print(lineString)

			# Get user options
			options = list()
			if (selChart[2] == None):
				options.append('1. Add a symptom')
				options.append('2. Add a diagnosis')
				options.append('3. Add a medication')
				options.append('4. Search for another chart')
				options.append('5. Return to home')
			else:
				options.append('1. Search for another chart')
				options.append('2. Return to home')

			# Handle user input
			waiting3 = True
			while waiting3:
				print("\nPlease select an option")
				for op in options:
					print(op)
				sel = raw_input(">> ")

				# Handle input cases
				if len(options)==2:
					# Search pressed
					if sel=='1':
						waiting1 = True
						waiting3 = False
					# Return pressed
					elif sel=='2':
						waiting3 = False
					else:
						print("Please select a proper option.")
				else:
					# Symptom pressed
					if sel=='1':
						print("\nPlease input the symptom:")
						addSymptom(hcno, chart_id, raw_input(">> "))
					# Diagnosis pressed
					elif sel=='2':
						print("\nPlease input the diagnosis")
						addDiagnosis(hcno, chart_id, raw_input(">> "))
					# Medication pressed
					elif sel=='3':
						print("\nPlease enter the medication start date: ")
						start = raw_input(">> ")
						print("Please enter the medication end date: ")
						end = raw_input(">> ")
						print("Please enter the daily amount: ")
						amount = int(raw_input(">> "))
						print("Please enter the drug name: ")
						drug = raw_input(">> ")
						addMedication(hcno, chart_id, start, end, amount, drug) 
					# Search pressed
					elif sel=='4':
						waiting1 = True
						waiting3 = False
						break
					# Return pressed
					elif sel=='5':
						waiting3 = False
						break
					else:
						print("Please select a proper option.")


conn.close()