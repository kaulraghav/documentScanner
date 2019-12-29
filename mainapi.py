from flask import Flask, request
from crop import *
from ktpUpdated import *
from panUpdated import *
from aadharUpdated import *
from npwpUpdated import *

app = Flask(__name__)

@app.route("/mainapi", methods = ['POST'])

def processImage():
    imageSent = request.files['imagefile']
    imageSent.save('filesent.jpg')
    try:
        image = cv2.imread('filesent.jpg')
        imageCopy = image.copy()
        #cv2.imshow('Initial', image)
    except:
        return jsonify('Image file not correct')

    print(image.shape)
    imageHeight, imageWidth, channel = image.shape
    path = "filesent.jpg"
    out_path = path.replace('.jpg', '.crop.jpg')

    crop = process_image(path, out_path)
    print('Crop Coordinates',  crop)

    if (imageWidth - crop[2]) / imageWidth > 0.01 or (imageHeight - crop[3]) / imageHeight > 0.01:
        print('Crop required')
        crop_img = image[crop[1]: crop[3], crop[0]: crop[2]]
        #cv2.imshow('Final', crop_img)
        #cv2.waitKey(0)
    else:
        print('Crop not required')
        crop_img = image
        #cv2.imshow('Final', crop_img)
        #cv2.waitKey(0)
    image = crop_img
    resized = getResizedImage(image)

    imageType = getImageType(resized)
    print(imageType)
    if imageType == 'PAN':
        ocrJson = panocr(resized)
    elif imageType == 'AADHAR':
        ocrJson = aadharocr(imageCopy, resized)
    elif imageType == 'INDONESIAN KTP':
        ocrJson = ktpocr(resized)
    elif imageType == 'INDONESIAN NPWP':
        ocrJson = npwpocr(imageCopy)
    else:
        ocrJson = 'INVALID DOCUMENT'
    return ocrJson


def getResizedImage(image):
    if image.shape[1] > 4000 or image.shape[0] > 3000:
        print('XXL')
        resized = cv2.resize(image, None, fx=0.2, fy=0.2, interpolation = cv2.INTER_AREA)
    elif image.shape[1] > 3000 or image.shape[0] > 2000:
        print('XL')
        resized = cv2.resize(image, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_AREA)
    elif image.shape[1] > 2000 or image.shape[0] > 1200:
        print('L')
        resized = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation = cv2.INTER_AREA)
    elif image.shape[1] > 1000 or image.shape[0] > 800:
        print('M')
        resized = cv2.resize(image, None, fx=0.8, fy=0.8, interpolation = cv2.INTER_AREA)
    else:
        print('S')
        resized = image
        
    return resized



def getImageType(resized):
    text = pytesseract.image_to_string(resized)

    lines = ""
    for item in text:
        lines = lines + item
    #print(lines)
    # Determining which type of document
    panarr = ['INCOME', 'TAX', 'DEPARTMENT', 'Permanent', 'Account', 'GOVT.']
    aadarr = ['GOVERNMENT', 'MALE', 'FEMALE', 'DOB', 'Male', 'Female']
    ktparr = ['PROVINSI', 'Alamat', 'Jenis', 'Agama', 'Status']
    npwarr = ['DIREKTORAT','JENDERAL','PAJAK','TERDAFTAR', 'NPWP']

    if any(re.findall('|'.join(panarr), lines)):
        print('Document is PAN Card')
        document = 'PAN'
    elif any(re.findall('|'.join(aadarr), lines)):
        print('Document is Aadhar Card')
        document = 'AADHAR'
    elif any(re.findall('|'.join(ktparr), lines)):
        print('Document is Indonesian KTP')
        document = 'INDONESIAN KTP'
    elif any(re.findall('|'.join(npwarr), lines)):
        print('Document is Indonesian NPWP')
        document = 'INDONESIAN NPWP'
    else:
        document = 'INVALID DOCUMENT'

    return document

if __name__ == '__main__':
    app.run(debug=True)

