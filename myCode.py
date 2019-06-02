# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:00:21 2019
"""
import numpy as np  
import matplotlib.pyplot as plt  
import pandas as pd  
import seaborn as sns
from apyori import apriori  
import csv 
from TransactionEncoder import TransactionEncoder

#Read Data by CSV library----------------------------------
def readData(data_path):
 with open(data_path, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    data = list(reader)
 return data    
#----------------------------------------------------------
#Visualize Data Frequency by seaborn and pandas library 
def visualization(data):
    te = TransactionEncoder()
    te_ary = te.fit(data).transform(data)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    df=df.applymap(lambda x: 1 if x==True else 0)
    myData=df.apply(pd.value_counts).T.sort_values(by=[1],ascending=False).head(20)
    Names=myData.index
    Freq=myData[1].values
    sns.barplot(x=Names,y=Freq)
path='data.csv'
data=readData(path)
#Call apriori algorithm from class apyori
association_rules = apriori(data, min_support=0.001, min_confidence=0.001)  
#convert assosiations to list
association_results = list(association_rules)  

print("We find "+str(len(association_results))+" assosiation rule.")  
#print(association_results)  
result=open("myresAPriory.txt", "w")
#visualization(data)

result.write("Rules\t Support \t Confidence \t Lift")
for item in association_results:
    pair = item[2][0][0]  
    items_1 = [x for x in pair]
    pair = item[2][0][1]  
    items_2 = [x for x in pair]
#    print("Rule: " + str(items_1)+ " -> " +str( items_2))
#    print("Support: " + str(item[1]))
#    print("Confidence: " + str(item[2][0][2]))
#    print("Lift: " + str(item[2][0][3]))
#    print("=====================================")
    
    result.write("\n"+ str(items_1)+ " -> " +str( items_2))
    result.write("\t" + str(item[1]))
    result.write("\t" + str(item[2][0][2]))
    result.write("\t" + str(item[2][0][3]))
#for item in association_results:
 #   result.write(str(item))
  #  result.write('----------------------------------------------'+'\n')
#    pair = item[0] 
#    items = [x for x in pair]
#    print("Rule: " + items[0] + " -> " + items[1])
#    print("Support: " + str(item[1]))
#    print("Confidence: " + str(item[2][0][2]))
#    print("Lift: " + str(item[2][0][3]))
#    print("=====================================")
result.close()
