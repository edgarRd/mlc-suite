# ##################################### #
# ITESM Campus Monterrey / SBC          #
# Edgar Hernan Rodriguez Diaz  790543   #
# Ivan Gonzalez  791688                 #
# ##################################### #

from read_arff import *
import math

class Rules:

	def __init__(self, arff_file):
		self.arff = arff_file
		self.perfectRules = []

	def getPerfectRules(self,tipo): #tipo = true, entonces utiliza p/t, sino utiliza p(log...
		classAttr = self.arff.AttributeList[-1]
		indices = [] #indices para los cuales ya hay una regla
		Attributes = []
		for attr in self.arff.AttributeList[0:-1]:
			if attr.Type == 'nominal':
				Attributes.append(attr)
			else:				
				newClass = numericToClasses(attr,classAttr.ValueList)
				attr = Attribute(attr.Name,attr.Type)
				attr.ValueList = newClass
				Attributes.append(attr)
		while len(indices) < len(classAttr.ValueList):
			ruleSet = {}
			for clase in classAttr.getDifferentValues():
				end = False
				ratio = 0
				Pp = 1
				Tt = len(classAttr.ValueList)
				dictElements = {}
				orden = []
				for attr in Attributes: #primero ordeno del mayor a menor
					arrayAttr = []
					arrayValues = []
					arrayAttr = attr.getDifferentValues()
					for value in arrayAttr:
						arrayValues.append([getMaxCont(value,clase,attr.ValueList,classAttr.ValueList),value])
					arrayValues = sortList2D(arrayValues)
					orden.append([arrayValues[0][0],arrayValues[0][1],attr])
				orden = sortList2D(orden)
				orden = minimize(orden)
				for attr in orden:
					if not end:
						#print attr.Name,clase,len(indices)
						dictItem = {}
						arrayAttr = attr.getDifferentValues()
						for value in arrayAttr:			
							dictItem[value] = 0
							for index in range(0,len(classAttr.ValueList)):
								if index not in indices:
									flag = True
									for key in dictElements.keys():
										if dictElements[key] <> key.ValueList[index]:
											flag = False
									if attr.ValueList[index] == value and flag:
										if classAttr.ValueList[index] == clase:
											dictItem[value] = dictItem[value] + 1
						dictElements[attr] = getMaxDict(dictItem)
						p = 0;
						t = 0;
						for index in range(0,len(classAttr.ValueList)):
							if index not in indices:
								flag = True
								for key in dictElements.keys():
									if dictElements[key] <> key.ValueList[index]:
										flag = False
								if flag:
									t = t + 1
									if classAttr.ValueList[index] == clase:
										p = p + 1
						#print p,t
						if t > 0:
							if tipo:
								razon = float(p)/float(t)
							else:
							    razon = p*(-math.log10(float(Pp)/float(Tt)))
							    Pp = p
							    Tt = t
                                
							otraFlag = True
							#print ratio,razon
							if len(self.perfectRules) > 0:
								lastSetRules = self.perfectRules[-1]
								#print len(lastSetRules[clase]),len(dictElements)
								if len(lastSetRules[clase]) > len(dictElements):
									 otraFlag = False
							if ratio > razon and otraFlag:
								end = True
							else:
								ratio = razon
							if tipo:
								if ratio == 1 and otraFlag:
									end = True
							else:
								if ratio == 0 and otraFlag:
									end = True
						else:
							del dictElements[attr]
							end = True
				if len(dictElements) > 0:
					ruleSet[clase] = dictElements
					for index in range(0,len(classAttr.ValueList)):
						if index not in indices:
							flag = True
							for key in dictElements.keys():
								if dictElements[key] <> key.ValueList[index]:
									flag = False
							if flag:
								#print index
								indices.append(index)
			self.perfectRules.append(ruleSet)

	def printRules(self,tipo):
		if tipo:
			print "Using p/t ratio: "
		else:
			print "Using gain information: "
		print
		for ruleSet in self.perfectRules:
			for clase in ruleSet.keys():
				rule = ruleSet[clase]
				print 'IF',
				index = 0
				for item in rule.keys():
					if item.Type == 'nominal':
						print '(%s IS %s)' % (item.Name,rule[item]),
					else:
						print '(%s IS IN RANGE %s)' % (item.Name,rule[item]),
					if index < len(rule) - 1:
						print 'AND',
						index = index + 1
				print 'THEN %s' % (clase)
				print

	def apply(self,tipo):
		self.getPerfectRules(tipo)
		self.printRules(tipo)

# Support functions

def numericToClasses(attr,classes):
	temp = []
	valores = []
	clases = []
	indices = []
	N = 0
	S = 0
	for i in attr.ValueList:
		if i <> None:
			N = N + 1
			S = S + i
	meanValue = float(S)/float(N)
	for i in range(0,len(attr.ValueList)):
		if attr.ValueList[i] <> None:
			temp.append([attr.ValueList[i],classes[i],i])
		else:
			temp.append([meanValue,classes[i],i])
	lista = sortList2D(temp)
	lista.reverse()
	for i in range(0,len(lista)):
		valores.append(lista[i][0])
		clases.append(lista[i][1])
		indices.append(lista[i][2])
	newClases = []
	sep = 0
	for index in range(0,len(valores)+1):
		temp = clases[sep:index]
		flag = True
		for i in temp:
			if (temp.count(i) > 2 and flag) or index == len(valores):
				if index == len(valores):
					for cont in range(sep,index):
						if attr.Type is 'integer':
							newClases.append('%i to %i' % (valores[sep],valores[index-1]))
						else:
							newClases.append('%f to %f' % (valores[sep],valores[index-1]))
				else:
					if clases[index] <> clases[index-1]:
						for cont in range(sep,index):
							if attr.Type is 'integer':
								newClases.append('%i to %i' % (valores[sep],valores[index]))
							else:
								newClases.append('%f to %f' % (valores[sep],valores[index]))
						sep = index
						flag = False
	finalClases = []
	temp = []
	for i in range(0,len(attr.ValueList)):
		temp.append([indices[i],newClases[i],i])
	lista = sortList2D(temp)
	lista.reverse()
	for i in range(0,len(lista)):
		finalClases.append(lista[i][1])
	return finalClases

def getMaxDict(dict):
	values = dict.values()
	values.sort()
	values.reverse()
	maximum = ''
	for key in dict.keys():
		if dict[key] == values[0]:
			maximum = key
	return maximum

def getMaxCont(valor,clase,values,clases):
	cont = 0
	for index in range(0,len(clases)):
		if values[index] == valor and clases[index] == clase:
			cont = cont + 1
	return cont

def sortList2D(list):
	for i in range(0,len(list)-1):
		for j in range(0,len(list)-1):
			if list[j][0] < list[j+1][0]:
				temp = list[j]
				list[j] = list[j+1]
				list[j+1] = temp
	return list

def minimize(list):
	temp = []
	for dato in list:
		temp.append(dato[2])
	return temp

###############################################################################
