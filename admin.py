import sqlite3
import time
from datetime import datetime

global HOME
HOME = ".home"

global conn
global cursor
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

#main function call 
def AdminMenu(name, s_id):
	global staff_name
	global staff_id
	
	staff_name = name
	staff_id = s_id
	print("\nWelcome admin {} type .home at any point to return to this main screen".format(staff_name))
	select = True
	while select:
		sel = raw_input("\nWhat would you like to do?\n1. Create Report\n2. Drug Category Stats\n3. List possible medications for some diagnosis\n4. List possible diagnosis for some drug\n5. Logout\n")
		if sel == "1": 
			# CreateReport()
			return
		elif sel == "2":
			# DrugStats()
			return
		elif sel == "3":
			ListMeds()
		elif sel == "4":
			ListDiagnoses()
		elif sel == "5":
			conn.close()	
			return
		else:
			print("Invalid selection try again")

# """ 1. Create a report, that lists, for each doctor, the name and the total amount of each drug that the doctor prescribed in a specified period of time. 
# (Drugs that he did not prescribe in that period of time should not be listed.)
# """
# def CreateReport():

# def DrugStats():
# 	#TODO

def ListMeds():

	diag = raw_input("Please enter diagnosis you wish to search: ")
	if diag == HOME: 
		return 
	#run a query for each medication and add it with repeats
	query = '''SELECT drug_name, COUNT(*) as med_count from medications, diagnoses where medications.chart_id = diagnoses.chart_id 
																		           and diagnosis = ? 
																		           and diagnoses.ddate <= medications.mdate
																		           GROUP BY drug_name 
																		           ORDER BY med_count DESC '''
	cursor.execute(query, (diag, ))
	temp = cursor.fetchall()
	print("Drugs that have been prescribed for diagnosis {} (ordered by most to least prescribed): ".format(diag))
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