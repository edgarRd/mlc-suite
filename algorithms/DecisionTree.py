# ##################################### #
# ITESM Campus Monterrey / SBC          #
# Edgar Hernan Rodriguez Diaz  790543   #
# Ivan Gonzalez  791688                 #
# ##################################### #

import math
import copy

class DecisionTree:
    
    def __init__(self, debug = False):
        self.debug = debug
        self.tree = None
        self.train_arff = None
        
    def create(self, training_arff):
        self.train_arff = training_arff
        self.tree = Tree()
        self.tree.setRoot(self._buildDecisionTree(None, self.train_arff.AttributeList, -1, [], []))
        self.printTree()
    
    def predict(self, prediction_arff):
        pass
    
    def _buildDecisionTree(self, parent, attributeList, infQtySelected, filterAttrs, filterVals):
        attr = None
        gains = {}
        if attributeList != None and len(attributeList) > 0:
            if infQtySelected == -1:
                attr = attributeList[-1]
                valueCounts = countValues(attr)
                infQty = getInformationQuantity(valueCounts)
                attributeList = attributeList[0:-1]
            else:
                infQty = infQtySelected
                
            for nextAttr in attributeList:
                valCounts = countValuesClass(filterAttrs, filterVals, nextAttr, self.train_arff.AttributeList[-1])
                infQty_ = getAttrInformationQuantity(valCounts)
                gain = float(infQty) - float(infQty_)
                # Hack to handle same gain in more than one attribute, rarely though.
                if gains.has_key(gain):
                    gains[gain-0.00000000001] = nextAttr
                else:
                    gains[gain] = nextAttr
            
            maxGain = max(gains.keys())
            selectedAttr = gains[maxGain]
            
            valCountsSelected = countValuesClass(filterAttrs, filterVals, selectedAttr, self.train_arff.AttributeList[-1])
            infQtySelected_ = getAttrInformationQuantity(valCountsSelected)
            
            filterAttrs.append(selectedAttr)

            attributeList = copy.copy(attributeList)
            attributeList.remove(selectedAttr)
            
            nodeAttr = Node('_attr', selectedAttr.Name, parent, [])
            
            for validVal in selectedAttr.ValidAttribList:
                filterVals.append(validVal)
                nodeVal = Node('_val', validVal, nodeAttr, [])
                nodeVal.addChild(self._buildDecisionTree(nodeVal, attributeList, infQtySelected_, filterAttrs, filterVals))
                nodeAttr.addChild(nodeVal)
                filterVals = filterVals[0:-1]
             
            filterAttrs = filterAttrs[0:-1]   
            
            return nodeAttr
        else:
            return None
        
    def printTree(self):
        if self.tree != None:
            self._printTreeImp(0, self.tree.root)
        
    def _printTreeImp(self, level, start_node):
        spaces = ' ' * 6
        if start_node != None:
            strSpaces = spaces * level
            print strSpaces + '|__' + start_node.type + ':' + start_node.value
            for child in start_node.childs:
                if child != None:
                    self._printTreeImp(level+1, child)
                

class Node:
    
    def __init__(self, _type, _value, _parent, _childs):
        self.type = _type
        self.value = _value
        self.parent = _parent
        self.childs = _childs
        
    def addChild(self, childObj):
        self.childs.append(childObj)
    
    def removeChild(self, childObj):
        self.childs.remove(childObj)    
    
    def setParent(self, parentObj):
        self.parent = parentObj
        
class Tree:
    
    def __init__(self, _root=None):
        ''' Defines the tree based in a Root Node '''
        self.root = _root
        
    def setRoot(self, _root):
        self.root = _root

### Support Functions ###

def countValues(attr):
    count = 0
    countList = []
    for validValue in attr.ValidAttribList:
        count = 0
        for val in attr.ValueList:
            if val == validValue:
                count += 1
        countList.append(count)
    return countList

def countValuesClass(attrs, vals, attrAll, class_attr):
    '''attrs is a dictionary with attr:val filter'''
    rows = range(0, len(attrAll.ValueList))
    subset = []
    index = 0
    countList = []
    
    if len(attrs) == len(vals):
        for attr in attrs:
            for x in rows:
                if attr.getValueAt(x) == vals[index]:
                    subset.append(x)
            index += 1
            rows = subset
            subset = []
        
    for validValue in attrAll.ValidAttribList:
        count = []
        classCount = {}
        missing = 0
        for i in rows:
            if attrAll.getValueAt(i)  == validValue:
                currentKey = class_attr.getValueAt(i)
                if classCount.has_key(currentKey):
                    classCount[currentKey] += 1
                else:
                    classCount[currentKey] = 1
        
        for key in classCount.keys():
            count.append(classCount[key])
        
        if len(count) != len(class_attr.ValidAttribList):
            missing = len(class_attr.ValidAttribList) - len(count)
        
        for j in range(0, missing):
            count.append(0)
            
        countList.append(count)
    return countList
        
def getClassForAttr(attrs, vals, class_attr):
    rows = range(0, len(attrs[0].ValueList))
    subset = []
    index = 0
    
    if len(attrs) == len(vals):
        for attr in attrs:
            for x in rows:
                if attr.getValueAt(x) == vals[index]:
                    subset.append(x)
            index += 1
            rows = subset
            subset = []
        
    currentClass = class_attr.getValueAt(rows[0])
    
    return currentClass

def countValuesClass2(attr, class_attr):
    countList = []
    for validValue in attr.ValidAttribList:
        count = []
        classCount = {}
        missing = 0
        for i in range(0, len(attr.ValueList)):
            if attr.getValueAt(i) == validValue:
                currentKey = class_attr.getValueAt(i)
                if classCount.has_key(currentKey):
                    classCount[currentKey] += 1
                else:
                    classCount[currentKey] = 1
            
        for key in classCount.keys():
            count.append(classCount[key])
            
        if len(count) != len(class_attr.ValidAttribList):
            missing = len(class_attr.ValidAttribList) - len(count)
            
        for j in range(0, missing):
            count.append(0)
        
        countList.append(count)
    return countList

def getInformationQuantity(valueCounts):
    acc = 0.0
    sumOfList = sumList(valueCounts)
    if len(valueCounts) - countElemInList(valueCounts, 0) > 1:
        for count in valueCounts:
            if count != 0:
                frac = (float(count) / sumOfList)
                acc += (-1.0) * frac * (math.log(frac, 2))
    
    return acc

def countElemInList(list, elem):
    count = 0
    for val in list:
        if val == elem:
            count += 1
    return count

def getAttrInformationQuantity(attrVals):
    acc = 0.0
    sumOfLists = sumListOfLists(attrVals)
    if sumOfLists != 0.0:
        for attr in attrVals:
            frac = (float(math.fsum(attr)) / sumOfLists)
            acc += frac * getInformationQuantity(attr)
    return acc
    
def sumList(list):
    return math.fsum(list)

def sumListOfLists(lists):
    acc = 0.0
    for li in lists:
        acc += math.fsum(li)
    return acc
        
def getDictSortedAsc(dict):
    klist = dict.keys()
    klist.sort( key = dict.__getitem__ )
    return klist

def getMaxValueInDict(dict):
    keys = getDictSortedAsc(dict)
    return keys[-1]