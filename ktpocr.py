import os.path
import json
import pytesseract
import re
import cv2
from flask import jsonify
import imutils
from PIL import Image


def ktpocr(resized):
    print('In eKTP code')
    grey = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    resized = imutils.resize(grey, height=500)
    crop = resized[0:resized.shape[0], 0:600]

    #cv2.imshow('cropped', crop)
    #cv2.waitKey(0)

    cv2.imwrite("temp.png", crop)

    text = pytesseract.image_to_string(Image.open('temp.png'))

    lines = ""
    for item in text:
        lines = lines + item
    print(lines)

    # NIK ID No
    try:

        nikObj = re.compile('(?<=NIK)(.*?)(?=Nama)', re.IGNORECASE | re.DOTALL).search(lines)
        nik = nikObj.group()
        nikObj = re.search(r'\b\d?.*', nik)
        nik = nikObj.group()
        #print(nik)
        nik = re.sub('b', '6', nik)
        nik = re.sub('S', '5', nik)
        nik = re.sub('[?]', '7', nik)
        nik = re.sub('[^0-9]+', "", nik)
        nik = re.sub('^\s+|\s+\Z', "", nik)

    except:
        try:
            nikObj = re.search('\d{16,17}', lines, re.M | re.I)
            nik = nikObj.group()

        except:
            try:
                nikObj = re.search('(?<=NIK).*$', lines, re.M | re.I)
                nik = nikObj.group()
                nikObj = re.search(r'\b\d?.*', nik)
                nik = nikObj.group()
                nik = re.sub('b', '6', nik)
                nik = re.sub('S', '5', nik)
                nik = re.sub('[?]', '7', nik)
                nik = re.sub('[^0-9]+', "", nik)
                nik = re.sub('^\s+|\s+\Z', "", nik)

            except:
                print('NIK not found')
                nik = ""

    # Name
    try:

        nameObj = re.search('(?<=Nama).*$', lines, re.M|re.I)
        name = nameObj.group()
        name = re.sub('[^A-Z ]+',"", name)
        name = re.sub('^\s+|\s+\Z', "", name)
        #print(name)
    except:
        print('Name not found')
        name = ""

    # Place of Birth
    try:
        if re.search('(?<=Lah).*$', lines, re.M|re.I):
            pobObj = re.search('(?<=Lah).*$', lines, re.M|re.I)
            pob = pobObj.group()
            pob = re.sub('[^A-Z]+',"", pob)
            pob = re.sub('^\s+|\s+\Z', "", pob)

        else:
            pobObj = re.search('(?<=hir).*$', lines, re.M | re.I)
            pob = pobObj.group()
            pob = re.sub('[^A-Z]+', "", pob)
            pob = re.sub('^\s+|\s+\Z', "", pob)

    except:
        print('Place of birth not found')
        pob = ""

    # Date of Birth
    try:

        dateObj = re.search('\d{2}[-]\d{2}[-]\d{4}', lines, re.M|re.I)
        dob = dateObj.group()
        #print(dob)

    except:
        print('Date of birth not found')
        dob = ""

    # Gender
    try:
        maleString = '(LAKI|LAKE|LAK|LAKI-|LAKILAKI|LEKI|LEK|LAKL|LAKL-|-LAKI)'
        femaleString = '(PEREMPUAN|PEREMPUAM|PERENPUAN|PERENPUAM|PUAN|PEREM)'

        if re.search(maleString, lines):
            gen = 'LAKI-LAKI'
        elif re.search(femaleString, lines):
            gen = 'PEREMPUAN'
        else:
            genObj = re.compile('(?<=elamin)(.*?)(?=Gol)').search(lines)
            gen = genObj.group()
            gen = re.sub('[^A-Z- ]+', "", gen)
            gen = re.sub('^\s+|\s+\Z', "", gen)
            #print(gen)

    except:
        print('Gender not found')
        gen = ""

    # Blood Group
    try:

        bloodObj = re.search('(?<=Darah).*$', lines, re.M|re.I)
        blood = bloodObj.group()
        blood = re.sub('[^ABO-]+',"", blood)
        if re.search(r'\b\w+\b', blood):
            blood = re.sub('[^ABO]+', "", blood)
        else:
            blood = '-'
    except:
        print('Blood group not found')
        blood = ""

    # Address
    try:

        addObj = re.compile('(?<=Alamat)(.*?)(?=RT)|(?<=Alamat)(.*?)(?=RI)|(?<=Alarnat)(.*?)(?=RT)|(?<=Alamat)(.*?)(?=RU)', re.IGNORECASE | re.DOTALL).search(lines)
        add = addObj.group()
        add = re.sub('¥',"V", add)
        add = re.sub('[^A-Z0-9. \n]+',"", add)
        add = re.sub('\n'," ", add)
        add = re.sub('^\s+|\s+\Z', "", add)
        #print(add)

    except:
        print('Address not found')
        add = ""

    # Neighborhood/ Hamlet Code
    try:

        rtrwObj = re.search('\d{3}[/]\d{3}|\d{3}\s[/]\s\d{3}', lines, re.M|re.I)
        rtrw = rtrwObj.group()
        rtrw = re.sub('^\s+|\s+\Z', "", rtrw)
        #print(rtrw)

    except:
        print('RT/RW not found')
        rtrw = ""

    # Urban Village/ Village
    try:

        vilObj = re.search('(?<=Desa).*$', lines, re.M|re.I)
        vil = vilObj.group()
        vil = re.sub('[!]',"I", vil)
        vil = re.sub('[^A-Z ]+',"", vil)
        vil = re.sub('^\s+|\s+\Z', "", vil)
        #print(vil)
    except:
        print('Village not found')
        vil = ""

    # Sub-District
    try:

        subObj = re.search('(?<=Kecamatan).*$', lines, re.M|re.I)
        subd = subObj.group()
        subd = re.sub('[^A-Z]+',"", subd)
        subd = re.sub('^\s+|\s+\Z', "", subd)
        #print(subd)

    except:
        print('Sub-District not found')
        subd = ""


    # Religion
    try:

        relString = '(ISLAM|SISLAM|ISLA|SLAM|ISLAMA|ISLAN|SLAN)'

        if re.search(relString, lines):
            #print('Found ISLAM')
            reli = 'ISLAM'

        else:
            relObj = re.search('(?<=Agama|Agame).*$', lines, re.M|re.I)
            reli = relObj.group()
            reli = re.sub('[^A-Z]+',"", reli)
            reli = re.sub('^\s+|\s+\Z', "", reli)
            #print(reli)

    except:
        print('Religion not found')
        reli = ""

    # Marital Status
    try:

        marString = '(KAWIN|KAWIM|KAVIN|KAVIM)'
        unmString = '(BELUM|BELUN|ELUM|ELUN|BEIUM)'

        if re.search(unmString, lines):
            #print('Found Single')
            mari = 'BELUM KAWIN'

        elif re.search(marString, lines):
            #print('Found married')
            mari = 'KAWIN'

        else:
            marObj = re.search('(?<=winan).*$', lines, re.M|re.I)
            print('Found other option')
            mari = marObj.group()
            mari = re.sub('[^A-Z ]+',"", mari)
            mari = re.sub('^\s+|\s+\Z', "", mari)
            #print(mari)

    except:
        print('Marital status not found')
        mari = ""

    # Work Type
    try:

        workObj = re.search('(?<=Pekerjaan).*$', lines, re.M|re.I)
        work = workObj.group()
        work = re.sub('[^A-Z/ ]+',"", work)
        work = re.sub('^\s+|\s+\Z', "", work)
        #print(work)

    except:
        print('Work type not found')
        work = ""

    # Citizenship
    try:

        citObj = re.search('(?<=Kewarganegaraan|Kewatganegaraan).*$', lines, re.M|re.I)
        citi = citObj.group()
        citi = citi.upper()
        citi = re.sub('[^A-Z]+',"", citi)
        citi.upper()
        citi = re.sub('^\s+|\s+\Z', "", citi)
        #print(citi)

    except:
        print('Citizenship not found')
        citi = ""

    # Valid Period
    try:

        valObj = re.search('(?<=Hingga).*$', lines, re.M|re.I)
        valid = valObj.group()
        valid = re.sub('[^A-Z0-9- ]+',"", valid)
        valid = re.sub('^\s+|\s+\Z', "", valid)
        #print(valid)

    except:
        print('Valid period not found')
        valid = ""

    # Making tuples of data
    data = {}
    data['typeOfDocument'] = 'INDONESIAN KTP'
    data['nationalIdNo'] = nik
    data['name'] = name
    data['placeOfBirth'] = pob
    data['dateOfBirth'] = dob
    data['gender'] = gen
    data['bloodGroup'] = blood
    data['address'] = add
    data['neighborhoodCode'] = rtrw
    data['urbanVillage'] = vil
    data['subDistrict'] = subd
    data['religion'] = reli
    data['maritalStatus'] = mari
    data['workType'] = work
    data['citizenship'] = citi
    data['validPeriod'] = valid


    # Writing data into JSON
    with open('raghav.json', 'w') as fp:
        json.dump(data, fp, indent=4)

    # Removing dummy files
    os.remove('temp.png')


    # Reading data back JSON
    with open('raghav.json', 'r') as f:
        ndata = json.load(f)

    print("+++++++++++++++++++++++++++++++")
    print(ndata['typeOfDocument'])
    print("-------------------------------")
    print(ndata['nationalIdNo'])
    print("-------------------------------")
    print(ndata['name'])
    print("-------------------------------")
    print(ndata['placeOfBirth'])
    print("-------------------------------")
    print(ndata['dateOfBirth'])
    print("-------------------------------")
    print(ndata['gender'])
    print("-------------------------------")
    print(ndata['bloodGroup'])
    print("-------------------------------")
    print(ndata['address'])
    print("-------------------------------")
    print(ndata['neighborhoodCode'])
    print("-------------------------------")
    print(ndata['urbanVillage'])
    print("-------------------------------")
    print(ndata['subDistrict'])
    print("-------------------------------")
    print(ndata['religion'])
    print("-------------------------------")
    print(ndata['maritalStatus'])
    print("-------------------------------")
    print(ndata['workType'])
    print("-------------------------------")
    print(ndata['citizenship'])
    print("-------------------------------")
    print(ndata['validPeriod'])
    print("-------------------------------")

    return jsonify(ndata)

