# ##################################### #
# ITESM Campus Monterrey / SBC          #
# Edgar Hernan Rodriguez Diaz  790543   #
# Ivan Gonzalez  791688                 #
# ##################################### #

from read_arff import *
from algorithms.DecisionTree import *
from algorithms.Rules import *
from algorithms.StatisticalModeling import *
from algorithms.a1R import *

import sys

FILE_NAME = '../test_files/weather.nominal.arff'
#FILE_NAME = '../test_files/iris.arff'
#FILE_NAME = '../test_files/labor.arff'
#FILE_NAME = '../test_files/segment-challenge.arff'

def main(option, file_name):
    """ This is the main procedure"""
    arff = getArff(file_name) 
    
    if option == '-1R':
        print '--> Running 1R Classification Algorithm for file: '+ file_name
        rules = []
        a1R = Algorithm1R(arff, debug=True)
        a1R.apply()
        print '--> Selected Classification Attribute:'
        print '\t', a1R.getClassificationAttr()
        print '--> Attribute details (name, total error):'
        print '\t', a1R.getMinError()
        print '--> Rules Generated:'
        rules = a1R.getRules()
        for rule in rules:
            print '\t', rule

    elif option == '-SM':
        print '\n','--> Running Statistical Modeling Classification Algorithm for file: '+ file_name
        training_arff, prediction_arff = arff.splitInTwo(percentage=70)
        aSM = AlgorithmStatisticalModeling(debug=False)
        aSM.train(training_arff)
        aSM.predict(prediction_arff)
        
    elif option == '-rules1':
        rules = Rules(arff)
        rules.apply(True)
        
    elif option == '-rules2':
        rules = Rules(arff)
        rules.apply(False)
        
    elif option == '-DT':
        aDT = DecisionTree(debug=False)
        print '\n','--> Running Decision Tree Classification Algorithm for file: '+ file_name
        print
        aDT.create(arff)
        
    else:
        print 'Option invalid, please read README file'
  

if __name__ == '__main__':
    #main(FILE_NAME)
    if len(sys.argv) > 1:
      main(sys.argv[1], sys.argv[-1])
    else:
      msg = u'''You need to specify the path of the file as: python mlc-suite.py <option> <filename>
      where <option>:
      -1R runs 1R algorithm
      -SM runs Statistical modeling algorithm
      -rules1 runs Rule classification with P/t
      -rules2 runs Rule classification with p(log P/t - log P/T)
      -DT creates the corresponding decision tree (only for nominal values and no missing values)'''
      print msg