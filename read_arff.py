import string
import math

class AttributeException(Exception):
    "Class for attribute exceptions"

InvalidAttributeValue = AttributeException("The attribute value is not in the valid attribute values list.")

class Attribute:

    def __init__(self, attrname, attrtype, validlist=[]):
        self.Name = attrname
        self.Type = attrtype
        self.ValidAttribList = validlist
        self.ValueList = []

    def addValue(self, value):
    	if value.strip() == "?":
    		self.ValueList.append(None)
        elif self.Type == "integer":
            self.ValueList.append(int(value))
        elif self.Type == "real":
            self.ValueList.append(float(value))
        elif self.Type == "numeric":
        	self.ValueList.append(float(value))
        else:
            if value in self.ValidAttribList:
                self.ValueList.append(value)
            elif value.strip() in self.ValidAttribList:
                self.ValueList.append(value.strip())
            else:
                print value, self.ValidAttribList
                raise InvalidAttributeValue

    def getValueAt(self, index):
        return self.ValueList[index]

    def getDifferentValues(self):
        diffValues = []
        for val in self.ValueList:
            if val not in diffValues and val != None:
                diffValues.append(val)
        return diffValues

            
class Arff:

    def __init__(self):
        self.AttributeList = []

    def addAttribute(self, attribute):
        self.AttributeList.append(attribute)

    def getInstance(self, i):
        instance = []
        for attribute in self.AttributeList:
            instance.append(attribute.ValueList[i])
        return instance
        
    def getInstanceDict(self, i):
        instance = {}
        for attribute in self.AttributeList:
            instance[attribute.Name] = attribute.ValueList[i]
        return instance

    def getNumInstances(self):
        if len(self.AttributeList) == 0:
            return 0
        else:
            return len(self.AttributeList[0].ValueList)
            
    def splitInTwo(self, percentage=70):
        ''' Added by: Edgar Rodriguez <edgar.rd@gmail.com>
        Splits an Arff object in two others. Receives as a parameter as the cutting point 
        (0 to 100 %) where the instances will be separated, by default, it will be cut at 70, 
        returning two Arff objects, one with 70% of the original Arff and other one with the
        remaining 30% of the original Arff object.'''
        first = Arff()
        second = Arff()
        cutPoint = math.floor( (float(percentage)/100) * self.getNumInstances() )
        
        for attr in self.AttributeList:
            nAttrFirst = Attribute(attr.Name, attr.Type, attr.ValidAttribList)
            nAttrSecond = Attribute(attr.Name, attr.Type, attr.ValidAttribList)
            count = 0
            for val in attr.ValueList:
                if val == None: val = '?'
                if count < cutPoint:
                    nAttrFirst.addValue( str(val) )
                else:
                    nAttrSecond.addValue( str(val) )
                count += 1
            
            first.addAttribute(nAttrFirst)
            second.addAttribute(nAttrSecond)
            
        return (first, second)


def getArff(fname):
    lines = open(fname, "r").readlines()

    (START,
     ATTRIBUTES,
     DATA) = range(3)

    state = START

    arff = Arff()

    for line in lines:
        if line[0] != "%":
            if state == START:
                items = line.strip().split()
                if (len(items) == 2) and (items[0].lower() == "@relation"):
                    dbname = items[1]
                    state = ATTRIBUTES
            elif state == ATTRIBUTES:
                items = line.strip().split()
                if (len(items) > 2) and (items[0].lower() == "@attribute"):
                    attribname = items[1]
                    attribfield = string.join(items[2:])
                    if attribfield.lower() == "real":
                        attribute = Attribute(attribname, "real")
                    elif attribfield.lower() == "numeric":
                        attribute = Attribute(attribname, "numeric")
                    elif attribfield.lower() == "integer":
                        attribute = Attribute(attribname, "integer")
                    elif (attribfield[0] == "{") and (attribfield[-1] == "}"):
                        attribtype = "nominal"
                        valuelist = attribfield[1:-1].split(",")
                        for i in range(len(valuelist)):
                            valuelist[i] = valuelist[i].strip()
                        attribute = Attribute(attribname, "nominal", valuelist)
                    else:
                        print "Unknown type:", attribfield
                        break
                    arff.addAttribute(attribute)
                if (len(items) == 1) and (items[0].lower() == "@data"):
                    state = DATA
            elif (state == DATA):
                datalist = line.strip().split(",")
                if len(datalist) == len(arff.AttributeList):
                    for i in range(len(arff.AttributeList)):
                        arff.AttributeList[i].addValue(datalist[i])
                elif len(line.strip()):
                    print line
                    print "Incorrect number of attributes on instance: %i" %len(datalist)
    return arff


