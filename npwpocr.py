import cv2
import os.path
import re
import json
import imutils
import pytesseract
from flask import jsonify
from PIL import Image


def npwpocr(imageCopy):

    resized = imutils.resize(imageCopy, height=500)
    cv2.imwrite("temp.png", resized)

    #cv2.imshow('Resized', resized)
    #cv2.waitKey(0)

    # Distinguishing different coloured NPNWs

    text = pytesseract.image_to_string(Image.open('temp.png'))
    #print(text)

    whiteString = '(KEMENTERIAN|KEUANGAN|REPUBLIK|INDONESIA)'

    if re.search(whiteString, text):
        #print('White NPNW')
        pass
    else:
        #print('Yellow or undetected row NPWP')
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("temp.png", resized)
        text = pytesseract.image_to_string(Image.open('temp.png'))

    #cv2.imshow('Resized', resized)
    #cv2.waitKey(0)

    #print(text)

    lines = text.split('\n')
    #print(lines)

    while ("" in lines):
        lines.remove("")
    while (" " in lines):
        lines.remove(" ")

    #print(lines)



    # NPWP [Tax Identification Number]

    try:
        npwpObj = re.search('\d{2}[.|,]\d{3}[.|,]\d{3}[.|,]\d{1}[-|,]\d{3}[.|,]\d{3}', text, re.M | re.I)
        npwp = npwpObj.group()
        npwp = re.sub(',', ".", npwp)
        npwp = re.sub('^\s+|\s+\Z', "", npwp)

    except:
        #print('NPWP not found')
        npwp = ""


    #Name

    npwpSub = 'NPWP'
    try:
        npwpLine = next((s for s in lines if npwpSub in s), None)
        npwpIndex = lines.index(npwpLine)
        nameIndex = npwpIndex + 1

    except:
        pass

    try:
        name = lines[nameIndex]
        name = re.sub('[^A-Z ]+',"", name)
        name = re.sub('^\s+|\s+\Z', "", name)
        #print('NAME -', name)

    except:
        #print('Name not found')
        name = ''


    # NIK

    try:
        nikObj = re.search('(?<=NIK).*$', text, re.M | re.I)
        nik = nikObj.group()
        nikObj = re.search(r'\b\d?.*', nik)
        nik = nikObj.group()
        nik = re.sub('b', '6', nik)
        nik = re.sub('S', '5', nik)
        nik = re.sub('[?]', '7', nik)
        nik = re.sub('[^0-9]+', "", nik)
        nik = re.sub('^\s+|\s+\Z', "", nik)
        #print('NIK -', nik)
    except:
        try:
            nikObj = re.search('\d{16,17}', lines, re.M | re.I)
            nik = nikObj.group()
            #print('NIK -', nik)
        except:
            #print('NIK not found')
            nik = ''


    # Address Block

    try:
        nik
    except NameError:
        nik = ''

    try:
        # Test whether variable is defined to be None
        if nik is '':
            addObj = (re.compile('(?<=%s)(.*?)(?=TGL)'%name, re.I | re.DOTALL).search(text) or re.compile('(?<=%s)(.*?)(?=TERDAFTAR)'%name, re.I | re.DOTALL).search(text)  or re.compile('(?<=%s)(.*?)(?=TANNGAL)'%name, re.I | re.DOTALL).search(text) or re.compile('(?<=%s)(.*?)(?=KPP)'%name, re.I | re.DOTALL).search(text))
            add = addObj.group()

        else:
            addObj = (re.compile('(?<=%s)(.*?)(?=TGL)' %nik, re.I | re.DOTALL).search(text) or re.compile('(?<=%s)(.*?)(?=TERDAFTAR)' %nik, re.I | re.DOTALL).search(text) or re.compile('(?<=%s)(.*?)(?=TANNGAL)' %nik, re.I | re.DOTALL).search(text) or re.compile('(?<=%s)(.*?)(?=KPP)' %nik, re.I | re.DOTALL).search(text))
            add = addObj.group()

        add = re.sub('[^A-Z0-9. \n]+',"", add)
        add = re.sub('\n'," ", add)
        add = re.sub('TANGGAL',"", add)
        add = re.sub('^\s+|\s+\Z', "", add)
        #print(add)
    except:
        #print('Address Block not found')
        add = ""

    # Registration Date

    try:
        regObj = re.search('\d{2}[-]\d{2}[-]\d{4}', text, re.M|re.I)
        regD = regObj.group()
        #print('REGISTRATION DATE -',regD)

    except:
        #print('Registration Date not found')
        regD = ""


    # Tax Office

    try:
        taxObj = re.search('(?<=PRATAMA).*$', text, re.M|re.I)
        tax = taxObj.group()
        tax = re.sub('[^A-Z ]+',"", tax)
        tax = re.sub('^\s+|\s+\Z', "", tax)
        #print('TAX OFFICE -',tax)
    except:
        #print('Tax Office not found')
        tax = ""

    # Making tuples of data
    data = {}
    data['typeOfDocument'] = 'INDONESIAN NPWP'
    data['taxIdNumber'] = npwp
    data['name'] = name
    data['nationalIdNo'] = nik
    data['address'] = add
    data['regDate'] = regD
    data['taxOffice'] = tax

    # Writing data into JSON
    with open('raghavNpwp.json', 'w') as fp:
        json.dump(data, fp, indent=4)

    # Removing dummy files
    os.remove('temp.png')
    #os.remove('temp1.png')


    # Reading data back JSON
    with open('raghavNpwp.json', 'r') as f:
        ndata = json.load(f)

    cv2.destroyAllWindows()

    print("+++++++++++++++++++++++++++++++")
    print(ndata['typeOfDocument'])
    print("-------------------------------")
    print(ndata['taxIdNumber'])
    print("-------------------------------")
    print(ndata['name'])
    print("-------------------------------")
    print(ndata['nationalIdNo'])
    print("-------------------------------")
    print(ndata['address'])
    print("-------------------------------")
    print(ndata['regDate'])
    print("-------------------------------")
    print(ndata['taxOffice'])
    print("-------------------------------")


    return jsonify(ndata)