import json
import random
import pandas as pd
import re
import base64 as b64
from PIL import Image
from .imageFormatter import ImageFormatter


class OutputHTMLCreator(object):
	def __init__(self):
		jsonData = {}
		error = False
		self.templatePath = "templateHTML.html"
		self.convertImages2b64 = True
		self.reduceImages = True
		self.imageType = "web"
		self.jsonkey_forfiles = "generatedFiles"
		self.fileCount = 0
		
	#===========================================================================
	# def config(self,rawData, path_outHTML = 'filledTemplate.html', nodeNumber = 0, fromDB = False, fromFile = False):
	# 	if(fromDB):
	# 		#TO - DO
	# 		pass
	# 	elif(fromFile):
	# 		try:
	# 			jsonData = json.load(open(rawData,'r'))
	# 		except: 
	# 			print("The data from the file can't be processed as JSON or the file does not exist, please check the output file to find more information.")
	# 			error = True
	# 	else:
	# 		if(isinstance(rawData,dict)):
	# 			jsonData = rawData
	# 		else:
	# 			try: 
	# 				jsonData = json.load(rawData)
	# 			except:
	# 				print("The data can't be processed as JSON, please check the output data to find more information.")
	# 				error = True
	# 	return jsonData
	#===========================================================================
		#self.create(jsonData, path_outHTML, nodeNumber, error)
				
	def getNestedLists(self,actualDict,htmlList = '', depth=1, isList= False, hierarchy = []):
		mainC = 0
		for k in actualDict:
			try:
				v = actualDict.get(k)
			except:
				v = k
				k = mainC
			if(self.jsonkey_forfiles in k):
				filespath = v["names"]
				image_formatter = ImageFormatter()
				formattedImages = image_formatter.prepareImgs(filespath, self.convertImages2b64, self.reduceImages, self.imageType)
				htmlList += '\n' + self.addtabs(depth) + '<ul>\n'
				htmlList += self.addtabs(depth) + '<details>\n'
				htmlList += self.addtabs(depth) + '<summary>'
				htmlList += str(k) + " : "
				htmlList += '</summary>\n'
				htmlList += self.addImages(formattedImages, depth)
				htmlList += self.addtabs(depth) + '</details>\n'
				htmlList += self.addtabs(depth) + '</ul>\n'
				
			if(isinstance(v, dict)):
				depth += 1
				htmlList += self.addHeading_newElement(v, summaryLabel = str(k),depth=depth)
				hierarchy.append(k)
				htmlList += self.getNestedLists(v,'',depth,hierarchy = hierarchy)
			elif(isinstance(v, list) and len(v)>0 and (isinstance(v[0], dict) or isinstance(v[0], list))):
				depth += 1
				#htmlList += '\n' + addtabs(depth) + '<ul onclick="console.log(\'Uhhhh\')">\n'
				htmlList += self.addHeading_newElement(v, summaryLabel = str(k) + " [",depth=depth)
				counter = 0
				hierarchy.append(k)
				for dictvals in v:
					htmlList += self.addtabs(depth) + '<li>'
					htmlList += self.addHeading_newElement(dictvals,summaryLabel = "List Index : " + str(counter),depth=depth)
					hierarchy.append(counter)
					htmlList += self.getNestedLists(dictvals,'',depth, isList = True, hierarchy = hierarchy)
					hierarchy.pop()
					htmlList += self.addClosing_newElement(depth)
					htmlList += self.addtabs(depth) + '</li>\n'
					counter += 1
				htmlList += " ]"
				htmlList += self.addClosing_newElement(depth)
			elif(isinstance(v, list)):
				#htmlList += '\n' + addtabs(depth) + '<ul onclick="console.log(\'Uhhhh\')">\n'
				htmlList += self.addHeading_newElement(v,summaryLabel = str(k) + " : ",depth=depth)
				hierarchy.append(k)
				htmlList += self.addtabs(depth) + '<li>'
				htmlList += str(v)
				htmlList += self.addtabs(depth) + '</li>\n'
				htmlList += self.addClosing_newElement(depth)
			else:
				htmlList += self.addtabs(depth) + '<li>'
				if(not isList):
					hierarchy.append(k)
					htmlList += str(k) + ":" + str(v)
				else:
					hierarchy.append(k)
					htmlList += str(k) + ":" + str(v)
				#print("key: ", k, ", Value: ", v, ", \n\thierarchy: ", hierarchy)
				htmlList += self.addtabs(depth) + '</li>\n'
			hierarchy.pop()
			mainC += 1
		if(not isList):
			htmlList += self.addClosing_newElement(depth)
		return htmlList

	def takeDescription(self,dictvals):
		description = pd.Series(dictvals).describe()
		str_description = str(description.astype("string"))
		html_description = str_description.replace('\n','</p><p>')
		format_description = re.sub(' +', ': ', html_description)
		return format_description
		
	def addHeading_newElement(self,rawData, summaryLabel,depth):
		htmlSummary = ''
		htmlSummary += '\n' + self.addtabs(depth) + '<ul>\n'
		htmlSummary += self.addtabs(depth) + '<details>\n'
		htmlSummary += self.addtabs(depth) + '<summary>'
		htmlSummary += self.addtabs(depth) + '<span class="tooltiptext"><p>' + self.takeDescription(rawData) +'</p></span>'
		htmlSummary += summaryLabel
		htmlSummary += '</summary>\n'
		return htmlSummary
		
	def addClosing_newElement(self,depth):
		htmlSummary = ''
		htmlSummary += self.addtabs(depth) + '</details>\n'
		htmlSummary += self.addtabs(depth) + '</ul>\n'
		return htmlSummary
	
	def addImages(self, imagesArray, depth):
		htmlImages = ''
		size = len(imagesArray)
		if(size>=4):
			rowlen = int(size/4)
		else:
			rowlen = 1
		counter = 0
		#htmlImages += self.addtabs(depth) +'<div class="row">\n'
		#htmlImages += self.addtabs(depth) +'<div class="column">\n'
		htmlImages += self.addtabs(depth) +'<section class="gallery">\n'
		htmlImages += self.addtabs(depth) +'<div class="gallery__item">\n'
		for b64image in imagesArray:
			if(counter >= rowlen):
				htmlImages += self.addtabs(depth) +'</div>\n'
				#htmlImages += self.addtabs(depth) +'<div class="column">\n'
				htmlImages += self.addtabs(depth) +'<div class="gallery__item">\n'
				counter = 0
			htmlImages += self.addImageColumn(b64image,depth, self.fileCount)
			self.fileCount = self.fileCount + 1
			counter = counter + 1
		# htmlImages += self.addtabs(depth) +'</div>\n'
		# htmlImages += self.addtabs(depth) +'</div>\n'
		htmlImages += self.addtabs(depth) +'</div>\n'
		htmlImages += self.addtabs(depth) +'</section>\n'
		return htmlImages

	def addImageColumn(self,b64content, depth, count):
		htmlImage = ''
		htmlImage += self.addtabs(depth) + '<input type="radio" id="img-' + str(count) + '" checked name="gallery" class="gallery__selector"/>\n'
		htmlImage += self.addtabs(depth) + '<img class="gallery__img" src="data:image/jpeg;base64,'+ str(b64content) +'"/>\n'
		htmlImage += self.addtabs(depth) + '<label for="img-' + str(count) + '" class="gallery__thumb"><img src="data:image/jpeg;base64,'+ str(b64content) +'"/></label>\n'
		return htmlImage
		  
		
		
	def addImage(self):
		pass

	def addtabs(self,number):
		outtabs = ''
		for i in range(0,number):
			outtabs += '\t'
		return outtabs

	def getHTMLasString(self):
		text_file = open(self.path_outHTML, "r")
		data = text_file.read()
		text_file.close()
		return data

	def create(self,rawData, path_outHTML = 'filledTemplate.html', nodeNumber = 0, fromDB = False, fromFile = False):
		if(fromDB):
			#TO - DO
			pass
		elif(fromFile):
			try:
				outputJSON = json.load(open(rawData,'r'))
			except: 
				print("The data from the file can't be processed as JSON or the file does not exist, please check the output file to find more information.")
				error = True
		else:
			if(isinstance(rawData,dict)):
				outputJSON = rawData
			else:
				try: 
					outputJSON = json.load(rawData)
				except:
					print("The data can't be processed as JSON, please check the output data to find more information.")
					error = True
		self.path_outHTML = path_outHTML
		htmlfile = open(self.templatePath,'r')
		newFile = open(path_outHTML,'w')
		for line in htmlfile:
			if(not error):
				if('///**RawData**///' in line):
					newFile.write('outputData =' + json.dumps(outputJSON))
				elif('///**HtmlNodeNumber**///' in line):
					newFile.write('<summary>Output from node: '+ str(nodeNumber) +'</summary>')
				elif('///**HtmlData**///' in line):
					newFile.write(self.getNestedLists(outputJSON,''))
				elif('///**HtmlImages**///' in line):
					# htmlImage = ''
					# htmlImage += '<div>'
					# htmlImage += '<p>Images from node</p>'
					# htmlImage += '<img src="data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==" alt="Red dot" />'
					# htmlImage += '</div>'
					# newFile.write(htmlImage)
					pass
				else:
					newFile.write(line)
			else:
				if('///**HtmlData**///' in line):
					newFile.write('<h1> Error found when procesing the output data as JSON, please check the data and paths </h1>')
		newFile.close()
		htmlfile.close()

