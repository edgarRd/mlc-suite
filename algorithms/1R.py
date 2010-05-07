__author__ = "Edgar Rodriguez" 
__email__ = "edgar.rd@gmail.com"
__copyright__ = "Copyright (C) 2010 Edgar Rodriguez" 
__license__ = "GPL" 
__version__ = "1.0" 

from read_arff import *

class Algorithm1R:

  def __init__(self, arff_file, debug=False):
    self.arff = arff_file
    self.maxErr = ();
    self.minErr = ();
    self.attrErr = []
    self.algoOutput = []
    self.rules = []
    self.debug = debug

  def getMinError(self):
    return self.minErr

  def getMaxError(self):
    return self.maxErr
    
  def calcMinError(self):
    minErr = ('',-1)
    if len(self.attrErr) > 0:
      minErrList = []
      
      for tuple in self.attrErr:
        if (minErr[1] == -1):
          minErr = tuple
          
        if (tuple[1] < minErr[1]):
          minErrList = []
          minErr = tuple
          minErrList.append(minErr)
        elif (tuple[1] == minErr[1]):
          minErrList.append(tuple)
        
      minDict = {}
      if len(minErrList) > 1:
        for minEq in minErrList:
          for attr in self.algoOutput:
            if attr.Name == minEq[0]:
              minDict[minEq] = len(attr.ValueClassDict)
        minErr = getMinValueInDict(minDict)
            
    return minErr
      
  def calcMaxError(self):
    maxErr = ('',-1)
    if len(self.attrErr) > 0:
      
      for tuple in self.attrErr:
        if (maxErr[1] == -1):
          maxErr = tuple
          
        if (tuple[1] > maxErr[1]):
          maxErr = tuple
          
    return maxErr

  def getClassificationAttr(self):
    return self.minErr[0]

  def getRules(self):
    classAttr = self.minErr[0]
    attrStruct = None
    self.rules = []
    
    for attr in self.algoOutput:
      if attr.Name == classAttr:
        attrStruct = attr
    
    if attrStruct != None:
      for value in attrStruct.ValueClassDict.keys():
        self.rules.append('if '+ attrStruct.Name +'='+ value +', then '+ \
        	self.arff.AttributeList[-1].Name +'='+ attrStruct.ValueClassDict[value][0]\
        )
    
    return self.rules
    
    
  def apply(self):
    if self.arff:
      classAttr = self.arff.AttributeList[-1]
      attrs = []
      if self.debug: print '**** Algorithm output: debug mode ****'
      for attr in self.arff.AttributeList[0:-1]:
        currentAttr = AttrStruct1R(attr.Name)
        if self.debug: print currentAttr.Name +':'
        for dVal in attr.getDifferentValues():
          classesDict = {}
          
          for i in range(0, len(attr.ValueList)):
            if attr.getValueAt(i) == dVal:
              classVal = classAttr.getValueAt(i)
              if classesDict.has_key(classVal):
                classesDict[classVal] = classesDict[classVal] + 1
              else:
                classesDict[classVal] = 1 
                
          maxClass = getMaxValueInDict(classesDict)
          numClassMax = classesDict[maxClass]
          totValueCounts = getSumValues(classesDict)
          currentAttr.addValueClass(dVal, [maxClass, totValueCounts-numClassMax, totValueCounts])
          if self.debug: print '\t', dVal, [maxClass, totValueCounts-numClassMax, totValueCounts]
          
        attrs.append(currentAttr)
        
      self.algoOutput = attrs
      self.attrErr = self.calcAttrErrors(attrs)
      self.minErr = self.calcMinError()
      self.maxErr = self.calcMaxError()
      if self.debug: print 'Attribute total errors:'
      if self.debug: print '\t', self.attrErr
      if self.debug: print '**************************************'
    else:
      print 'No arff file was provided'
      
  def calcAttrErrors(self, attrs):
    """ This method will return a list with tuples of format (attrName, totError)"""
    tupleList = []
    for attrStruct in attrs:
      errNum = 0
      errTot = 0
      valList = []
      
      for key in attrStruct.ValueClassDict.keys():
        valList = attrStruct.ValueClassDict[key]
        errNum += valList[1]
        errTot += valList[2]
        
      tupleList.append((attrStruct.Name, float(errNum)/float(errTot)))
      
    return tupleList
      
      
class AttrStruct1R:
  
  def __init__(self, attrName):
    self.Name = attrName
    self.ValueClassDict = {}
    
  def addValueClass(self, value, li):
    """The li represents the [class, errorCounts, totCounts]"""
    self.ValueClassDict[value] = li

### Support functions ###

def getMaxValueInDict(dict):
  keys = getDictSortedAsc(dict)
  return keys[-1]
  
def getMinValueInDict(dict):
  keys = getDictSortedAsc(dict)
  return keys[0]
  
def getDictSortedAsc(dict):
  klist = dict.keys()
  klist.sort( key = dict.__getitem__ )
  return klist
  
def getSumValues(dict):
  sum = 0
  for item in dict.items():
    sum += item[1]
    
  return sum
