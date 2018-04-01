import PIL
import pytesseract
import argparse
import cv2
import os
import time
import urllib.request

M1W = 1
M2W = 1
M3W = 1

def main(preprocess):
    starttime = time.time()
    # construct the argument parse and parse the arguments
    #ap = argparse.ArgumentParser()
    #ap.add_argument("-i", "--image", required=True,
    #	help="path to input image to be OCR'd")
    #ap.add_argument("-p", "--preprocess", type=str, default="thresh",
    #	help="type of preprocessing to be done")
    #args = vars(ap.parse_args())

    # load the example image and convert it to grayscale
    # Had issues with opencv needing full image path, hence this discusting code
    #   finds this file's path and uses it to find image
    gray = cv2.imread(os.path.realpath(__file__).replace('\\', "/").replace("ocr.py", "") + 'image.jpg', 0)

    # check to see if we should apply thresholding to preprocess the
    # image
    if preprocess == "thresh":
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # make a check to see if median blurring should be done to remove
    # noise
    elif preprocess == "blur":
        gray = cv2.medianBlur(gray, 3)

    # write the grayscale image to disk as a temporary file so we can
    # apply OCR to it
    coords = [[288, 804], [864, 988], [1048, 1173], [1223, 1363]]
    filenames = []
    for i in range(4):
        filenames.append(str(i)+"_test.png".format(os.getpid()))
        cv2.imwrite(filenames[i], gray[coords[i][0]:coords[i][1], 52:1100])

    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    out = []
    for i in range(4):
        out.append(pytesseract.image_to_string(PIL.Image.open(filenames[i])))
        os.remove(filenames[i])
        print(out[i])

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    weighted = [0, 0, 0]
    m3unweighted = [0,0,0]
    largest = 0
    largenum = 0
    for i in range(3):
        req = urllib.request.Request("https://google.com/search?q=" + (out[0] + "&as_epq=" + out[i+1]).replace(" ", "+").replace("\n", "+"), headers = headers)
        page = str(urllib.request.urlopen(req).read())
        start = page.find('\"resultStats')
        end = page.find('results', start)
        resultstr = page[start+20:end-1]
        translation_table = dict.fromkeys(map(ord, ','), None)
        resultstr = resultstr.translate(translation_table)
        num = int(resultstr)
        m3unweighted[i] = num
        if(num > largenum):
            largenum = num
            largest = i + 1

    for i in range(3):
        weighted[i] = M3W * m3unweighted[i]/largenum
    print("Method 3: " + str(largest))
    print(weighted)


    print("Took " + str(time.time() - starttime) + " seconds to  run.");
    # show the output images
    cv2.imshow("Output", cv2.resize(gray, (200, 350), interpolation = cv2.INTER_CUBIC))
    cv2.waitKey(0)

main("thresh")

#question
#288 to 804
#864-988
#1048-1173
#1223-1363
