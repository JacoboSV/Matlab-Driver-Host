import base64 as b64
import os

class ImageFormatter(object):
    def __init__(self):
        pass
    
    def prepareImgs(self, filePath, reduced, returnb64, type):
        if(reduced):
            filePaths = self.reduceSize(filePath, type=type)
        if(returnb64):
            imgsArr = self.files2b64(filePaths)
            return imgsArr
        else:
            return filePath 
        
    def file2b64string(self,filePath):
        with open(filePath, "rb") as img:
            b64_string = b64.b64encode(img.read())
        return b64_string.decode('utf-8')
    
    def files2b64(self,file):
        return self.file2b64string(file)
    
    def reduceSize(self, imgPath, type="web"):
        expectedSizes = {
            "max":  (1000,1000),
            "web":    (630,630),
            "logo":    (250,250),
            "thumbnail": (150,150),
            "icon":    (100,100),
            "minimum":    (32,32),
            "micro":    (5,5)
        }
        try:
            image = Image.open(imgPath)
            imgSize = image.size
            print("The size of the image is: ", image.size)
            maxwidth = expectedSizes[type][1]
            maxheight = expectedSizes[type][0]
            ratio = min(maxwidth/imgSize[1], maxheight/imgSize[0])
            newSize = (int(imgSize[0]*ratio), int(imgSize[1]*ratio))
            print("---> The new size of the image is: ", newSize)
            image = image.resize(newSize,Image.ANTIALIAS)
            filename = os.path.basename(imgPath)
            dirname = os.path.dirname(os.path.abspath(imgPath))
            filename =  "scaled__" + type + "__" + filename
            newPath = os.path.join(dirname,filename)
            image.save(newPath, optimize=True, quality=95)
        except:
            newPath = imgPath
        return newPath