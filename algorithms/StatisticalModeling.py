__author__ = "Edgar Rodriguez" 
__email__ = "edgar.rd@gmail.com"
__copyright__ = "Copyright (C) 2010 Edgar Rodriguez" 
__license__ = "GPL" 
__version__ = "1.0"

from read_arff import *
from fractions import Fraction
import math

class AlgorithmStatisticalModeling:
    
    def __init__ (self, debug=False, miu=1.0):
        self.debug = debug
        self.miu = miu
        self.attrProb = {}
        self.classProb = {}
        
    def train(self, training_arff):
        classCount = {}
        if training_arff:
            classAttr = training_arff.AttributeList[-1]
            classCount = self._classCount(classAttr)
            if self.debug: print 'Classes count: ', classCount
            if self.debug: print '**** Algorithm output: debug mode ****'
             
            for attr in training_arff.AttributeList[0:-1]:
                attrProbE = AttributeProbability(attr)
                    
                if attr.Type == 'nominal':
                    for dVal in attr.getDifferentValues():
                        dictCount = self._initializeDictCount(classCount)
                        for sClass in classCount.keys():
                            for i in range(0, len(attr.ValueList)):
                                if attr.getValueAt(i) == dVal and attr.getValueAt(i) != None:
                                    classVal = classAttr.getValueAt(i)
                                        
                                    if classVal == sClass:
                                        if dictCount.has_key(sClass):
                                            dictCount[sClass] += 1
                                            
                            #dictCount[sClass] = Fraction( dictCount[sClass] + self.miu/3, classCount[sClass] + self.miu )
                            dictCount[sClass] = ( float(dictCount[sClass]) + float(self.miu)/3.0 ) / ( float(classCount[sClass]) + float(self.miu) )
                            
                        if self.debug: print str(dVal)+':'
                        if self.debug: print '\t',dictCount
                        attrProbE.addValueProbability(dVal, dictCount)
                        
                    self.attrProb[attr.Name] = attrProbE
                else:
                    dictCount = {}
                    if self.debug: print attr.Name+":"
                    for sClass in classCount.keys():
                        if self.debug: print '\t',sClass+":"
                        normalDist = None
                        listVal = []
                        for i in range(0, len(attr.ValueList)):
                            if sClass == classAttr.getValueAt(i) and attr.getValueAt(i) != None:
                                listVal.append(attr.getValueAt(i))
                        
                        if self.debug: print listVal
                        if self.debug: print prettyFloatFormat(listVal)
                        normalDist = NormalDistribution(mean=computeMean(listVal), variance=computeVariance(listVal))
                        dictCount[sClass] = normalDist
                        if self.debug: print '\t\t', dictCount[sClass]
                        
                    attrProbE.addValueProbability('_normaldist', dictCount)
                    self.attrProb[attr.Name] = attrProbE
                        
            if len(classCount) > 0:
                totalInstances = self._classTotalCount(classCount)
                for cVal in classCount.keys():
                    #classCount[cVal] = Fraction(classCount[cVal], totalInstances)
                    classCount[cVal] = float(classCount[cVal]) / float(totalInstances)
            
                self.classProb = classCount
                if self.debug: print 'Classes Probability:'
                if self.debug: print '\t', self.classProb
    
    def _initializeDictCount(self, classCount):
        dictCount = {}
        for classKey in classCount.keys():
            dictCount[classKey] = 0
        return dictCount
                
    def _classCount(self, classAttr):
        dictClassesCount = {}
        for classVal in classAttr.ValueList:
            if dictClassesCount.has_key(classVal):
                dictClassesCount[classVal] += 1
            else:
                dictClassesCount[classVal] = 1
        return dictClassesCount
        
    def _classTotalCount(self, dictClassCount):
        sum = 0
        for key in dictClassCount.keys():
            sum += dictClassCount[key]
        return sum
        
    def predict(self, predict_arff):
        ''' Returns a prediction of certain number of events (as an instance of a arff file).
        NOTE: Sometimes probabilities are too small and due to printing in 4 digits, they may 
        appear as 0.0000.'''
        classAttr = predict_arff.AttributeList[-1]
        countMatch = 0
        countMismatch = 0
        if len(self.attrProb) > 0 and len(self.classProb) > 0:
            print 'Predictions:'
            for i in range(0, predict_arff.getNumInstances()):
                realClass = classAttr.getValueAt(i)
                dictInstance = {}
                for attr in predict_arff.AttributeList[0:-1]:
                    dictInstance[attr.Name] = attr.getValueAt(i)
                print 'Instance:'
                print dictInstance
                predict = self._makePrediction( dictInstance )
                print '\t-->', predict
                if realClass == predict:
                    countMatch += 1
                else:
                    countMismatch += 1
            print 'Summary:'
            print '\t','Total Predictions: %d' % (predict_arff.getNumInstances())
            print '\t','Matched Predictions: %d' % (countMatch)
            print '\t','Mismatch Predictions: %d' % (countMismatch)
            print '\t','Efficiency: %.2f%%' % ( (float(countMatch) / float(predict_arff.getNumInstances()))*100.0 )
        else:
            print "Can't make prediction: The algorithm has not been trained!"
        
    def _makePrediction(self, dictAttrVal):
        probabilities = []
        dictPredictions = {}
        for strClass in self.classProb.keys():
            probabilities = []
            for attr_name in dictAttrVal.keys():
                probabilities.append(self._getProbabilityOf(attr_name, dictAttrVal[attr_name], strClass))
                
            probabilities.append(self.classProb[strClass])
            print '\tProbabilities for '+strClass+': ', prettyFloatFormat(probabilities)
            dictPredictions[strClass] = self._computeProbabilityEvents(probabilities)
            
        normVal = self._classTotalCount(dictPredictions)
        
        # Normalize probabilities
        for ekey in dictPredictions.keys():
            dictPredictions[ekey] = float(dictPredictions[ekey]) / float(normVal)
           
        print '\t', prettyFloatFormat(dictPredictions)
        return getMaxValueInDict(dictPredictions)
            
    def _getProbabilityOf(self, attr_name, attr_val, strClass):
        prob = -1.0
        if self.attrProb.has_key(attr_name) and attr_val != None:
            attrProbE = self.attrProb[attr_name]
            
            if attrProbE.attribute.Type == 'nominal':
                if attrProbE.ValueProbDict.has_key(attr_val):
                    attrProbVal = attrProbE.ValueProbDict[attr_val]
                    if attrProbVal.has_key(strClass):
                        prob = attrProbVal[strClass]
            else:
                attrProbVal = attrProbE.ValueProbDict['_normaldist']
                if attrProbVal.has_key(strClass):
                    ndist = attrProbVal[strClass]
                    prob = ndist.computeProbability(attr_val)
        return prob
    
    def _computeProbabilityEvents(self, probabilies):
        probTot = 1.0
        for prob in probabilies:
            if prob != -1.0:
                probTot *= prob    
        return probTot

class AttributeProbability:
    
    def __init__(self, attribute):
        self.attribute = attribute 
        self.ValueProbDict = {}
    
    def addValueProbability(self, value, prob):
        ''' prob is a dictionary with the properties for every class
        as key '''
        self.ValueProbDict[value] = prob

class NormalDistribution:
    
    def __init__( self, mean=0.0, variance=0.0 ):
        self.mean = mean
        self.variance = variance
    
    def __str__( self ):
    	return "{ mean="+ '%.2f' % (self.mean)+", variance="+ '%.2f' % (self.variance) +" }"
    
    def computeProbability( self, x ):
        if self.variance == 0:
            if x == self.mean:
                return 1.0
            else:
                return 0.0
        else:
            expArg = ( -1.0 * math.pow((x - self.mean), 2.0) )/( 2.0 * self.variance )
            fact = 1.0 / math.sqrt( 2.0 * math.pi * self.variance )
            return fact * math.exp(expArg)

### Support functions ###

def getDictSortedAsc(dict):
    klist = dict.keys()
    klist.sort( key = dict.__getitem__ )
    return klist

def getMaxValueInDict(dict):
    keys = getDictSortedAsc(dict)
    return keys[-1]

def prettyFloatFormat(list):
    ''' Prints a list of numbers in a set format'''
    if type(list) == type([]):
        strFormat = '['
        for num in list:
            strFormat += '%.4f, ' % (num)
        return strFormat[0:-2] + ']'
    elif type(list) == type({}):
        strFormat = '{'
        for skey in list.keys():
            strFormat += "'"+skey+"': "+ '%.4f, ' % (list[skey])
        return strFormat[0:-2] + '}'
    else:
        return str(list)
    
def computeMean(valueList):
    sum = 0.0
    for num in valueList:
        sum += float(num)
    return float(sum) / float(len(valueList))

def computeVariance(valueList):
    mean = computeMean(valueList)
    sum = 0.0
    for num in valueList:
        sum += float( math.pow( (num - mean), 2 ) )
    return ( 1.0 / float(len(valueList) - 1.0) ) * sum
