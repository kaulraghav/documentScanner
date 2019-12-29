import pytesseract
import re
import difflib
from flask import jsonify
from PIL import Image
import json
import os.path
import imutils
import csv
import cv2


def panocr(resized):
    #importing image
    #image = cv2.imread(".jpg")
    #grey = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    resized = imutils.resize(resized, height=500)

    #cv2.imshow('Resized', resized)
    #cv2.waitKey(0)

    newWidth = int(0.6*resized.shape[1])
    crop = resized[0: resized.shape[0], 0:newWidth]

    #cv2.imshow('crop', crop)
    #cv2.waitKey(0)

    cv2.imwrite("temp.png", crop)
    text = pytesseract.image_to_string(Image.open('temp.png'))
    #print(text)

    lines = text.split('\n')
    #print(lines)

    while ("" in lines):
        lines.remove("")
    while (" " in lines):
        lines.remove(" ")

    #print(lines)



    # Name

    taxSub = 'TAX'


    if re.search(taxSub, text):
        print('FOUND')

    try:
        taxLine = next((s for s in lines if taxSub in s), None)
        taxIndex = lines.index(taxLine)
        #print(taxIndex)
        nameIndex = taxIndex + 1
        #print(nameIndex)
        #print(lines[nameIndex])
        fnameIndex = nameIndex + 1

    except:
        pass

    try:
        newName = re.sub('[^A-Z ]+', "", lines[nameIndex])
        #print('Regex name', newName)
        newName = re.sub('^(\S*\s+\S+\S*\s\S*).*', "\\1", newName)
        #print('Regex Newnew name', newName)
    except:
        print('Name not found')
        newName = ''


    try:
        newFname = re.sub('[^A-Z ]+', "", lines[fnameIndex])
        newFname = re.sub('^(\S*\s+\S+\S*\s\S*).*', "\\1", newFname)
        # print('New Father name', newFname)
    except:
        print('Fathers Name not found')
        newFname = ''




    # PAN Number
    try:
        panObj = re.search('[A-Z]{5}\d{4}[A-Z]{1}', text, re.M | re.I)
        pan = panObj.group()
        #print('PAN NUMBER -', pan)

    except:
        print('PAN Number not found')
        pan = ''


    # Date of Birth
    try:
        dateObj = re.search('\d{2}[/]\d{2}[/]\d{4}', text, re.M | re.I)
        dob = dateObj.group()
        #print('DATE OF BIRTH -', dob)

    except:
        print('Date of birth not found')
        dob = ""




    #Alternate method (Working on Ganesh sir's laptop)
    '''
    # saving the new image
    cv2.imwrite("temp.png", resized)
    
    # performing charcter recognition
    text = pytesseract.image_to_string(Image.open('temp.png'))
    
    # Date of Birth
    try:
        dateObj = re.search('\d{2}[/]\d{2}[/]\d{4}', text, re.M | re.I)
        dob = dateObj.group()
        # print('Regex DOB', reDob)
    
    except:
        print('Date of birth not found')
        reDob = ""
    
    # PAN Number
    
    try:
        panObj = re.search('[A-Z]{5}\d{4}[A-Z]{1}', text, re.M | re.I)
        rePan = panObj.group()
        # print('Regex PAN', rePan)
    
    except:
        pass
    
    
    # Initializing data variable
    name = None
    fname = None
    dob = None
    pan = None
    nameline = []
    dobline = []
    panline = []
    text0 = []
    text1 = []
    text2 = []
    govRE_str = '(GOVERNMENT|OVERNMENT|VERNMENT|DEPARTMENT|EPARTMENT\
                  |PARTMENT|ARTMENT|INDIA|NDIA)$'
    numRE_str = '(Number|umber|Account|ccount|count|Permanent|\
                  ermanent|manent)$'
    
    # Searching for PAN
    lines = text.split('\n')
    for lin in lines:
        text = lin.strip()
        text = text.rstrip()
        text = text.lstrip()
        text1.append(text)
    
    text1 = filter(None, text1)
    t = []
    for item in text1:
        t.append(item)
    
    lineno = 0
    
    
    # -----------Read Database
    with open('namedb.csv', 'r') as f:
        reader = csv.reader(f)
        newlist = list(reader)
    newlist = sum(newlist, [])
    # print('newlist', newlist)
    
    # Searching for Name and finding closest name in database
    try:
        for x in text0:
            for y in x.split():
                if (difflib.get_close_matches(y, newlist)):
                    nameline.append(x)
                    break
    except Exception as ex:
        pass
    
    # print('nameline', nameline)
    
    try:
        name = nameline[0]
        print('NAME - ', name)
        fname = nameline[1]
        print('FATHER NAME - ', fname)
    except Exception as ex:
        pass
    
    
    newName = re.sub('[^A-Z ]+', "", name)
    # print('Regex name', newName)
    newName = re.sub('^(\S*\s+\S+\S*\s\S*).*', "\\1", newName)
    # print('Regex Newnew name', newName)
    newFname = re.sub('[^A-Z ]+', "", fname)
    newFname = re.sub('^(\S*\s+\S+\S*\s\S*).*', "\\1", newFname)
    # print('New Father name', newFname)
    
    try:
        dobline = [item for item in text0 if item not in nameline]
        # print dobline
        for y in dobline:
            l = y.split()
            l = [s1 for s1 in l if len(s1) > 3]
            l
        for x in dobline:
            z = x.split()
            z = [s1 for s1 in z if len(s1) > 3]
            for y in z:
                if dparser.parse(y, fuzzy=True):
                    dob = dparser.parse(y, fuzzy=True).year
                    panline = dobline[dobline.index(x) + 1:]
                    break
    except Exception as ex:
        pass
    '''


    # Making tuples of data
    data = {}
    data['typeOfDocument'] = 'PAN CARD'
    data['name'] = newName
    data['fatherName'] = newFname
    data['dateOfBirth'] = dob
    data['pan'] = pan

    # Writing data into JSON
    with open('raghav.json', 'w') as fp:
        json.dump(data, fp)

    # Removing dummy files
    os.remove('temp.png')

    # Reading data back JSON(give correct path where JSON is stored)
    with open('raghav.json', 'r') as f:
        ndata = json.load(f)
    print("+++++++++++++++++++++++++++++++")
    print(ndata['typeOfDocument'])
    print("-------------------------------")
    print(ndata['name'])
    print("-------------------------------")
    print(ndata['fatherName'])
    print("-------------------------------")
    print(ndata['dateOfBirth'])
    print("-------------------------------")
    print(ndata['pan'])
    print("-------------------------------")

    return jsonify(ndata)
