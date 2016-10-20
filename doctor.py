import sqlite3


waiting0 = True

while waiting0:
	# Present the user with their options
	name = "Brett" # NAME PASSED FROM LOGIN HERE
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

			# Connect to the database
			conn = sqlite3.connect('hospital.db')
			cursor = conn.cursor()
			
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
				num = raw_input(">> ")
				if num=="<":
					waiting1 = True
					break;
				for chart in chartList:
					if chart[0]==num:
						viewID = chart[0]
						selChart = chart
						waiting2 = False
				if waiting2: print("Please select a proper chart number.")


			# Display the medical information for the selected chart
			sql = '''SELECT *
FROM {}
WHERE hcno=?
AND chart_id=?
ORDER BY ? DESC'''
			# Create symptom list
			cursor.execute(sql.format('symptoms'), (hcno, num, 'obs_date'))
			sList = cursor.fetchall()
			symList = tuple()
			for sym in sList:
				symList += ((' S ',) + sym, )

			# Create diagnoses list
			cursor.execute(sql.format('diagnoses'), (hcno, num, 'ddate'))
			dList = cursor.fetchall()
			diaList = tuple()
			for dia in dList:
				diaList += ((' D ', ) + dia, )

			# Create medications list
			cursor.execute(sql.format('medications'), (hcno, num, 'mdate'))
			mList = cursor.fetchall()
			medList = tuple()
			for med in mList:
				medList += ((' M ', ) + med, )

			''' Sorting all entries by their entry date. Adapted from
			http://stackoverflow.com/questions/20183069/how-to-sort-multidimensional-array-by-column
			on Oct 19 2016'''
			lineList = symList + diaList + medList
			lineList = sorted(lineList, key = lambda x: x[4])
			for line in lineList:
				# Create and print line string
				string = '\n' + line[0]
				for element in line[1:]:
					# Format the element to a uniform length
					element = str(element)
					if len(element)>8 and len(element)<12:
						element = element.ljust(12)
					elif len(element)>6 and len(element)<10:
						element = element.ljust(10)
					else:
						element = element.ljust(6)
					string += '| ' + element
				print(string+'\n')

			# Get user options
			options = list()
			if (selChart[2] == None):
				options.append('1. Add a symptom')
				options.append('2. Add a diagnoses')
				options.append('3. Add a medication')
				options.append('4. Search for another chart')
				options.append('5. Return to home')
			else:
				options.append('1. Search for another chart')
				options.append('2. Return to home')

			# Handle user input
			waiting3 = True
			while waiting3:
				print("Please select an option")
				for op in options:
					print(op)
				sel = raw_input(">> ")

				# Handle input cases
				if len(options)==2:
					if sel=='1':
						waiting1 = True
						waiting3 = False
					elif sel=='2':
						waiting3 = False
					else:
						print("Please select a proper option.")
				else:
					if sel=='1':
						print("TODO// HANDLE ADD SYMPTOM")
					elif sel=='2':
						print ("TODO// HANDLE ADD DIAGNOSES")
					elif sel=='3':
						print ("TODO// HANDLE ADD MEDICATION")
					elif sel=='4':
						waiting1 = True
						waiting3 = False
					elif sel=='5':
						waiting3 = False
					else:
						print("Please select a proper option.")


conn.close()