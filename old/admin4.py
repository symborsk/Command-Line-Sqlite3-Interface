import sqlite3
import time

conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()
global HOME
HOME = ".home"

# Make sure the user has selected a valid drug
def getDrug():
	while True:
		print("Please input a drug: ")
		sel = raw_input(">> ")

		sql = '''SELECT drug_name FROM drugs WHERE drug_name=?'''
		params = (sel, )

		drug = cursor.execute(sql, params).fetchall()

		if len(drug)>0:
			return drug[0]

		print("No drug with that name found. Please try again.")

# Get all diagnoses made before drug prescription
def getDiagnoses(drug_name):
	# Get all charts where drug prescribed
	sql = '''SELECT chart_id, mdate, amount FROM medications WHERE drug_name=?'''

	# Array of (chart_id, mdate) 
	chartInfo = cursor.execute(sql, drug_name).fetchall()
	if len(chartInfo)==0:
		return -1

	amounts = list(tuple())
	sql = '''SELECT diagnosis FROM diagnoses WHERE chart_id=? AND ddate<?'''

	# Get all diagnoses in chart_id with ddate < mdate
	for info in chartInfo:
		data = (info[0], info[1])
		tmp = cursor.execute(sql, data).fetchall()
		if len(tmp)>0:
			amounts.append((tmp[0][0], info[2]))


	if len(amounts)==0:
		return -2
	return amounts

def Admin4():

	drug = getDrug()

	# Handle diagnoses cases
	amounts = getDiagnoses(drug)
	if amounts==-1:
		print(drug[0] + " has not yet been prescribed.")
		return
	elif amounts==-2:
		print("No diagnoses have been made before a prescription of " + drug[0] + ".")
		return

	totals = dict()

	# Get total amounts for all diagnoses
	for a in amounts:
		# Add diagnosis if it isn't there
		if totals.has_key(a[0])==False:
			totals[a[0]]= (a[1], 1)
		else:
			curr = totals[a[0]]
			tmp = (curr[0] + a[1], curr[1] + 1)
			totals[a[0]] = tmp


	results = list()

	# Get averages
	for pair in totals.items():
		name = pair[0]
		totalAmount = pair[1][0]
		numPrescribed = pair[1][1]
		avg = (totalAmount*1.0)/(numPrescribed*1.0)
		results.append((name, avg))


	# Sort based on averages
	results = sorted(results, key = lambda x: x[1])

	# Print the results
	for r in results:
		print("Diagnosis: " + str(r[0]).ljust(16) + "Average: " + str(r[1]))

def ListDiagnoses():
	drug = raw_input("Please enter medication you wish to search: ")
	if drug == HOME: 
		return 
	#run a query for each medication and add it with repeats
	query = '''SELECT diagnosis, AVG(medications.amount) as average from medications, diagnoses where medications.chart_id = diagnoses.chart_id 
																		           and drug_name = ? 
																		           and diagnoses.ddate <= medications.mdate
																		           GROUP BY diagnosis 
																		           ORDER BY average DESC '''
	cursor.execute(query, (drug, ))
	temp = cursor.fetchall()
	print("Diagnoses that have been precribed {} (ordered by largest average amount prescribed per diagnoses): ".format(drug))
	for result in temp:
		print(result[0])

	while True:
		user = raw_input("Would you like to enter search another diagnosis(y/n)");
		if(user.lower() == "y"):
			ListMeds()
			return;
		elif(user.lower() == "n"  or user.lower() == HOME):
			return
		else:
			print("Invalid selection")


ListDiagnoses()