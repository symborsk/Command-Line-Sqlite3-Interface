import sqlite3
import time
from datetime import datetime

global HOME
HOME = ".home"

global conn
global cursor
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

class Admin:
	def __init__(this, name, s_id):
		this.staff_name = name
		this.staff_id = s_id
	
	#Main menu of the admin class
	def AdminMenu(this):

		print("\nWelcome admin {} to the admin department. Please type .home at any point to return to this main screen".format(this.staff_name))
		while True:
			sel = raw_input("\nWhat would you like to do?\n1. Create Report for doctors and drugs prescribed\n2. Drug Category Stats\n3. List possible medications for some diagnosis\n4. List possible diagnosis for some drug\n5. Logout\n>> ")
			if sel == "1": 
				this.CreateReport()
			elif sel == "2":
				this.DrugStats()
			elif sel == "3":
				this.ListMeds()
			elif sel == "4":
				this.ListDiagnoses()
			elif sel == "5":
				conn.close()	
				return
			else:
				print("Invalid selection try again")

	""" 1. Create a report, that lists, for each doctor, the name and the total amount of each drug that the doctor prescribed in a specified period of time. 
	(Drugs that he did not prescribe in that period of time should not be listed.)
	"""
	def CreateReport(this):
		
		print("\nPlease enter the start date of your period in the format YYYY-MM-DD HH:MM:SS")
		start = raw_input(">> ").lower()

		if start == HOME: 
			return 
		
		if len(start) != 19:
			print("\nWrong length (YYYY-MM-DD HH:MM:SS)")
			this.CreateReport()
			return
		if (start[4] != "-" or start[7] != "-" or start[13] != ":" or start[16] != ":"):
			print("\nWrong format - not datetime format (YYYY-MM-DD HH:MM:SS)")
			this.CreateReport()
			return
		
		print("\nPlease enter the end date of your period in the format YYYY-MM-DD HH:MM:SS")
		end = raw_input(">> ").lower()
		
		if end==HOME: 
			return
		
		if len(end) != 19:
			print("\nWrong length (YYYY-MM-DD HH:MM:SS)")
			this.CreateReport()
			return
		
		if (end[4] != "-" or end[7] != "-" or end[13] != ":" or end[16] != ":"):
			print("\nWrong format - not datetime format (YYYY-MM-DD HH:MM:SS)")
			this.CreateReport()
			return
		
		#Check to aid the user so they cannot check 
		if start >= end:
			print("\nThe start date is before end date please re-enter")
			this.CreateReport()
			return
		
		else:
			print("Results:\n")
			sql = '''SELECT * FROM staff WHERE role == "d"'''
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
				
				#print out all our results as drugname : amount
				for row1 in numpresc:
					drugname = row1[1]
					damt = row1[2]
					if damt != 0:
						print(str(drugname) + " : " + str(damt))

			while True:
				user = raw_input("Would you like generate another report?(y/n)\n>> ").lower();
				if(user == "y"):
					this.CreateReport()
					return
				elif(user == "n"  or user == HOME):
					return
				else:
					print("Invalid selection")

	"""2. 
	For each category of drugs, list the total amount prescribed for each drug in that category in a specified period of time. 
	The report should also contain a total for each category.
	"""
	def DrugStats(this):
		print("\nPlease enter the start date of your period in the format YYYY-MM-DD HH:MM:SS")
		start = raw_input(">> ").lower()
		
		#Each user entry requires we check to ensure they dont want to return to main menu
		if start == HOME: 
			return
		
		# Do a couple pre checks so the date they enter does not crash database 
		if len(start) != 19:
			print("\nWrong length (YYYY-MM-DD HH:MM:SS)")
			this.DrugStats()
			return

		if (start[4] != "-" or start[7] != "-" or start[13] != ":" or start[16] != ":"):
			print("\nWrong format - not datetime format (YYYY-MM-DD HH:MM:SS)")
			this.DrugStats()
			return
		
		print("\nPlease enter the end date of your period in the format YYYY-MM-DD HH:MM:SS")
		end = raw_input(">> ").lower()
		
		#Each user entry requires we check to ensure they dont want to return to main menu
		if end==HOME: 
			return
		
		# Do a couple pre checks so the date they enter does not crash database 
		if len(end) != 19:
			print("\nWrong length (YYYY-MM-DD HH:MM:SS)")
			this.DrugStats()
			return
		
		if (end[4] != "-" or end[7] != "-" or end[13] != ":" or end[16] != ":"):
			print("\nWrong format - not datetime format (YYYY-MM-DD HH:MM:SS)")
			this.DrugStats()
			return
		
		if start >= end:
			print("\nThe start date is after the end date, please re-enter")
			this.DrugStats()
			return

		else:
			print("Results: \n")
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
			
			while True:
				user = raw_input("Would you like generate another report?(y/n)\n>> ").lower();
				if(user == "y"):
					this.DrugStats()
					return
				elif(user == "n"  or user == HOME):
					return
				else:
					print("Invalid selection")

	def ListMeds(this):
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
		drug = cursor.fetchall()
		print("Drugs that have been prescribed for diagnosis {} (ordered by most to least prescribed): ".format(diag))
		for result in drug:
			print(result[0])
		if(len(drug) == 0):
			print("No drugs prescribed for that diagnosis")

		while True:
			user = raw_input("Would you like to enter search another diagnosis?(y/n)\n>> ");
			if(user.lower() == "y"):
				this.ListMeds()
				return;
			elif(user.lower() == "n"  or user.lower() == HOME):
				return
			else:
				print("Invalid selection")

	def ListDiagnoses(this):
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
		diag = cursor.fetchall()
		print("Diagnoses that have been precribed {} (ordered by largest average amount prescribed per diagnoses): ".format(drug))
		for result in diag:
			print(result[0])

		if(len(temp) == 0):
			print("No diagnoses for that specific drug.")

		while True:
			user = raw_input("Would you like to enter search another medication?(y/n)\n>> ").lower();
			if(user == "y"):
				this.ListDiagnoses()
				return
			elif(user == "n"  or user == HOME):
				return
			else:
				print("Invalid selection")