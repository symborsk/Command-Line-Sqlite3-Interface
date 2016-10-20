import sqlite3


waiting0 = True

while waiting0:
	# Present the user with their options
	name = "Brett"
	print "Welcome,", name, '''\nPlease select one of the following: 
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
			print("Please enter the desired patient health care number: ")
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
			print ("Open Charts\nChart # | Admission Date")
			for chart in chartList:
				if chart[2] == None:
					string = chart[0].ljust(7) + ' | ' + chart[1].ljust(14)
					print(string)

			# Show closed charts
			print ("\nClosed Charts\nChart # | Admission Date | Departure Date")
			for chart in chartList:
				if chart[2] != None:
					string = chart[0].ljust(7) + ' | ' + chart[1].ljust(14) + ' | ' + chart[2]
					print(string)

			# Allow the user to select a chart
			waiting2 = True
			viewID = None
			while waiting2:
				print("Select the chart number you want to view:")
				num = raw_input(">> ")
				if num=="<":
					waiting1 = True
					break;
				for chart in chartList:
					if chart[0]==num:
						waiting2 = False
						viewID = chart[0]
				print("Please select a proper chart number.")

conn.close()