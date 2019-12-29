import os.path
import json
import pytesseract
import re
import cv2
import imutils
import difflib
from flask import jsonify
import csv
from PIL import Image

def aadharocr(imageCopy, resized):

	print('In Aadhar code')
	greyRes = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
	greyCopy = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2GRAY)
	resizedCopy = imutils.resize(greyCopy, height=550)

	cv2.imwrite("temp.png", greyRes)
	cv2.imwrite("temp1.png", greyCopy)

	text = pytesseract.image_to_string(Image.open('temp.png'))
	textOri = pytesseract.image_to_string(Image.open('temp1.png'))

	# Initializing data variable
	gender = None
	yearline = []
	genline = []
	nameline = []
	text1 = []

	lines= ""
	for item in text:
		lines = lines + item
	#print('LINES',lines)


	# Searching for Year of Birth [Just need for text1 and wordlist]
	for wordlist in lines.split('\n'):
		xx = wordlist.split()
		if ([w for w in xx if re.search('(Year|Birth|irth|YoB|YOB:|DOB:|DOB)$', w)]):
			yearline = wordlist
			break
		else:
			text1.append(wordlist)
	try:
		text2 = text.split(yearline,1)[1]
	except:
		pass

	# Date of Birth
	try:
		dateObj = re.search('\d{1,2}[-/]\d{1,2}[-/]\d{4}', lines, re.M|re.I)
		date = dateObj.group()

	except:
		print('Date of Birth not found')
		date = ""

	# Gender

	try:
		for wordlist in lines.split('\n'):
			xx = wordlist.split()
			if ([w for w in xx if re.search('(Female|Male|emale|male|ale|FEMALE|MALE|EMALE)$', w)]):
				genline = wordlist
				break

		if 'FEMALE' in genline:
			gender = "Female"
		elif 'Female' in genline:
			gender = "Female"
		elif 'MALE' in genline:
			gender = "Male"
		elif 'Male' in genline:
			gender = "Male"

	except:
		print('Gender not found')
		gender = ''
		pass

	# Name

	try:

		newName = max(text1, key=len)
		newName = re.sub('[^A-Za-z ]+',"", newName)
		newName = re.sub('^\s+|\s+\Z', "", newName)

	except:
		print('Name not found')
		tempName = ""

	# Reading Database
	with open('namedb.csv', 'rt', encoding = 'utf8') as f:
		reader = csv.reader(f)
		newlist = list(reader)
	newlist = sum(newlist, [])

	# Searching for Name and finding closest name in database
	try:

		text1 = filter(None, text1)
		for x in text1:
			for y in x.split():
				if(difflib.get_close_matches(y.upper(), newlist)):
					nameline.append(x)
					break
		name = ''.join(str(e) for e in nameline)
	except:

		pass


	# Mobile Number
	try:

		mobileObj = re.search('[0-9]{10}', lines, re.M | re.I)
		mobile = mobileObj.group()
		mobile = re.sub('^\s+|\s+\Z', "", mobile)

	except:

		print('Mobile number not found')
		mobile = ""


	# Aadhar Number
	try:

		uidObj = re.search('[0-9]{4}\s[0-9]{4}\s[0-9]{4}', lines, re.M|re.I)
		uid = uidObj.group()
		uid = re.sub('^\s+|\s+\Z', "", uid)

	except:

		try:
			uidObj = re.search('[0-9]{4}\s[0-9]{4}\s[0-9]{4}', textOri, re.M | re.I)
			uid = uidObj.group()
			uid = re.sub('^\s+|\s+\Z', "", uid)
			print('Aadhar Number', uid)

		except:

			print('Aadhar number not found')
			uid = ""

	# Making tuples of data
	data = {}
	data['name'] = newName
	data['gender'] = gender
	data['birthYear'] = date
	data['mobileNumber'] = mobile
	data['aadharNo'] = uid

	# Writing data into JSON
	with open('raghav.json', 'w') as fp:
		json.dump(data, fp)

	# Removing dummy files
	os.remove('temp.png')

	# Reading data back JSON
	with open('raghav.json', 'r') as f:
		ndata = json.load(f)

	print("+++++++++++++++++++++++++++++++")
	print(ndata['name'])
	print("-------------------------------")
	print(ndata['birthYear'])
	print("-------------------------------")
	print(ndata['gender'])
	print("-------------------------------")
	print(ndata['mobileNumber'])
	print("-------------------------------")
	print(ndata['aadharNo'])
	print("-------------------------------")

	return jsonify(ndata)
