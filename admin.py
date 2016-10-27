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
	while True:
		sel = raw_input("\nWhat would you like to do?\n1. Create Report\n2. Drug Category Stats\n3. List possible medications for some diagnosis\n4. List possible diagnosis for some drug\n5. Logout\n")
		if sel == "1": 
			CreateReport()
			return
		elif sel == "2":
			DrugStats()
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

""" 1. Create a report, that lists, for each doctor, the name and the total amount of each drug that the doctor prescribed in a specified period of time. 
(Drugs that he did not prescribe in that period of time should not be listed.)
"""
def CreateReport():
	
	print("\nPlease enter the start date of your period in the format, DATE - format YYYY-MM-DD HH:MM:SS")
	start = raw_input(">> ").lower()

	if start == HOME: 
		return 
	
	if len(start) < 17:
		print("\nwrong format - not long enough (YYYY-MM-DD HH:MM:SS)")
		CreateReport()
		return
	if (start[4] != "-" or start[7] != "-" or start[13] != ":" or start[16] != ":"):
		print("\nwrong format-not datetime format (YYYY-MM-DD HH:MM:SS)")
		CreateReport()
		return
	
	print("\nPlease enter the end date of your period in the format, DATE - format YYYY-MM-DD HH:MM:SS")
	end = raw_input(">> ").lower()
	
	if end==HOME: 
		return
	
	if len(end) < 17:
		print("\nwrong format - not long enough (YYYY-MM-DD HH:MM:SS)")
		CreateReport()
		return
	if (end[4] != "-" or end[7] != "-" or end[13] != ":" or end[16] != ":"):
		print("\nwrong format-not datetime format (YYYY-MM-DD HH:MM:SS)")
		CreateReport()
		return
	
	if start >= end:
		print("\nThe start date is greater than the end date, please re-enter")
		CreateReport()
		return
	
	else:
		sql = '''SELECT * FROM staff WHERE role == "D"'''
		cursor.execute(sql)
		docs = cursor.fetchall()
		for row in docs:
			staffid = row[0]
			docname = row[2]
			sql = '''SELECT mdate, drug_name, amount FROM medications WHERE staff_id = ? AND mdate > datetime(?) AND mdate < datetime(?)'''
			params = (staffid, start, end)
			cursor.execute(sql, params)
			numpresc = cursor.fetchall()
			if len(numpresc) > 0:
				print("\n" + str(row[2]) + ":")
			#print(len(numpresc))
			
			for row1 in numpresc:
				drugname = row1[1]
				damt = row1[2]
				if damt != 0:
					print(str(drugname) + " : " + str(damt))
		return

"""2. 
For each category of drugs, list the total amount prescribed for each drug in that category in a specified period of time. 
The report should also contain a total for each category.
"""
def DrugStats():
	print("\nDrug Stats")
	print("\nPlease enter the start date of your period in the format, DATE - format YYYY-MM-DD HH:MM:SS")
	start = raw_input(">> ").lower()
	
	if start == HOME: 
		return
	
	if len(start) < 17:
		print("\nWrong format - not long enough (YYYY-MM-DD HH:MM:SS)")
		DrugStats()
		return
	if (start[4] != "-" or start[7] != "-" or start[13] != ":" or start[16] != ":"):
		print("\nWrong format-not datetime format (YYYY-MM-DD HH:MM:SS)")
		DrugStats()
		return
	
	print("\nPlease enter the end date of your period in the format, DATE - format YYYY-MM-DD HH:MM:SS")
	end = raw_input(">> ").lower()
	
	if end==HOME: 
		return
	
	if len(end) < 17:
		print("\nWrong format - not long enough (YYYY-MM-DD HH:MM:SS)")
		DrugStats()
		return
	if (end[4] != "-" or end[7] != "-" or end[13] != ":" or end[16] != ":"):
		print("\nWrong format-not datetime format (YYYY-MM-DD HH:MM:SS)")
		DrugStats()
		return
	
	if start >= end:
		print("\nThe start date is greater than the end date, please re-enter")
		DrugStats()
		return
	
	else:
		sql = '''SELECT DISTINCT category FROM drugs'''
		cursor.execute(sql)
		categories = cursor.fetchall()
		#runs through all categories
		for row2 in categories:	
			catname = row2[0]
			
			#gets all prescribed drug names and amounts in certain category, within specified period, used to get total amount in each category
			sql = '''SELECT medications.drug_name, medications.amount FROM medications, drugs WHERE medications.mdate > datetime(?) AND medications.mdate < datetime(?) AND drugs.drug_name = medications.drug_name AND drugs.category = ?'''
			params = (start, end, catname, )
			cursor.execute(sql, params)
			drugz = cursor.fetchall()
			totamt = 0
			for amt in drugz:
				#print(amt[0])
				totamt = totamt + amt[1]
			print("Category: " + str(catname) + " -- Total amount: "+ str(totamt))

			sql = '''SELECT DISTINCT medications.drug_name FROM medications, drugs WHERE medications.mdate > datetime(?) AND medications.mdate < datetime(?) AND drugs.drug_name = medications.drug_name AND drugs.category = ?'''
			params = (start, end, catname, )
			cursor.execute(sql, params)
			drugzname = cursor.fetchall()
			for namez in drugzname:
				indamt = 0
				
				for namezz in drugz:
					if namezz[0] == namez[0]:
						indamt = indamt + int(namezz[1])
						#print(str(namezz[0] + str(namezz[1]) + "going through?"))
						
				print(str(namez[0]) + " : " + str(indamt))
		return

def ListMeds():

	diag = raw_input("Please enter diagnosis you wish to search: ").lower()
	if diag == HOME: 
		return 
		
	#run a query for each medication that counts and sorts times are prescribed
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
	if(len(temp) == 0):
		print("No drugs prescribed for that diagnosis")

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
	drug = raw_input("Please enter medication you wish to search: ").lower()
	if drug == HOME: 
		return 


	#run a query for each medication that calculates the average dose prescribed per diagnosis
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
		user = raw_input("Would you like to enter search another diagnosis(y/n)").lower();
		if(user. == "y"):
			ListMeds()
			return;
		elif(user == "n"  or user == HOME):
			return
		else:
			print("Invalid selection")