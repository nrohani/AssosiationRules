# -*- coding: utf-8 -*-
"""
Created on Fri May 10 19:06:44 2019

@author: Programmer
"""





import csv
import numpy as np
import pandas as pd
from TransactionEncoder import TransactionEncoder
from collections import namedtuple
from itertools import combinations

def readData(data_path):

 with open(data_path, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    data = list(reader)

 return data
def compute_LK(LK_, support_list, k, num_trans, min_support):
    LK = []
    supportK = {}
    for i in range(len(LK_)):
       for j in range(i+1, len(LK_)):  
            L1 = sorted(list(LK_[i])[:k-2])
            L2 = sorted(list(LK_[j])[:k-2])
            if L1 == L2: # if the first k-1 terms are the same in two itemsets, calculate the intersection support
                union = np.multiply(support_list[LK_[i]], support_list[LK_[j]])
                union_support = np.sum(union) / num_trans
                if union_support >= min_support:
         
                    new_itemset= frozenset(sorted(list(LK_[i] | LK_[j])))

                    if new_itemset not in LK:
                        LK.append(new_itemset)
                        supportK[new_itemset] = union
    return sorted(LK), supportK
#
#def compute_L1(data, num_trans, min_support):
#	L1 = []
#	support_list = {}
#	for idx in data:
#		support = np.sum(data.get(idx)) / num_trans
#		if support >= min_support:
#                 support_list[frozenset([idx])] = data[idx]
#                 L1.append([idx])
#                 print([idx],support, np.sum(data[idx]))
#	return list(map(frozenset, sorted(L1))), support_list
#
def compute_L1(data, idx2item, num_trans, min_support):
	L1 = []
	support_list = {}
	for idx, bit_list in enumerate(data):
		support = np.sum(bit_list) / num_trans
		if support >= min_support:
                 support_list[frozenset([idx2item[idx]])] = bit_list
                 L1.append([idx2item[idx]])
                # print([idx2item[idx]],support)

	return list(map(frozenset, sorted(L1))), support_list


def calc_support(items,data,idx2item,num_transaction):
        idx2itemm=dict(zip(idx2item.values(),idx2item.keys()))
        if not items:
            return 1.0

        if not num_transaction:
            return 0.0

        sum_indexes = None
        for item in items:
            item=item.strip()

            indexes =data[idx2itemm[item]]
#            indexes=frozenset(indexes)
#            if indexes is None:
#                return 0.0

            if sum_indexes is None:
                sum_indexes = indexes
            else:
                sum_indexes = np.multiply(sum_indexes, indexes)

        return float(np.sum(sum_indexes)) / num_transaction 
class eclat_runner:

   def __init__(self, num_trans, min_support):
        self.num_trans = num_trans
        self.min_support = min_support * num_trans
        self.support_list = {}
		

   def run(self, prefix, supportK):
		
       print('Running Eclat in recursive: number of itemsets found:', len(self.support_list), end='\r')
       while supportK:
            itemset, bitvector = supportK.pop(0)
            support = np.sum(bitvector)

            if support >= self.min_support:
                self.support_list[frozenset(sorted(prefix + [itemset]))] = int(support)

                suffix = []
                for itemset_sub, bitvector_sub in supportK:
                    if np.sum(bitvector_sub) >= self.min_support:
                        union_bitvector = np.multiply(bitvector, bitvector_sub)
                        if np.sum(union_bitvector) >= self.min_support:
                           suffix.append([itemset_sub, union_bitvector])

                self.run(prefix+[itemset], sorted(suffix, key=lambda x: (x[0]), reverse=True))

   def eclat(data, min_support):
       OrderedStatistic = namedtuple( 
      'OrderedStatistic', ('items_base', 'items_add', 'confidence', 'lift',))
       num_trans = float(len(data))
       vb_data, idx2item=compute_vertical_bitvector_data(data)

       L1, support_list = compute_L1(vb_data, idx2item, num_trans, min_support)
       L = [L1]
       f = open("myresEclat.txt", "w")

       k=1
       while (True):
            print('Running Eclat: the %i-th iteration with %i itemsets in L%i...' % (k, len(L[-1]), k))
            k += 1
            LK, supportK = compute_LK(L[-1], support_list, k, num_trans, min_support)
            if len(LK) == 0:
                L = [sorted([tuple(sorted(itemset)) for itemset in LK]) for LK in L]
                support_list = dict((tuple(sorted(k)), np.sum(v)) for k, v in support_list.items())
                print('Running Eclat: the %i-th iteration. Terminating ...' % (k-1))

                break
            else:
                L.append(LK)
                print(len(supportK),k)
                support_list.update(supportK)
       print(len(support_list))
       for suppRec in  support_list:
        
        items=suppRec
        items=frozenset(items)
        for combination_set in combinations(sorted(items), len(items) - 1):
         items_base = frozenset(combination_set)
         items_add = frozenset(items.difference(items_base))
#         confidence = (support_list.get(suppRec) / calc_support(items_base,data))
         confidence = (calc_support(suppRec,vb_data,idx2item,9835) / calc_support(items_base,vb_data,idx2item,9835))

         lift = confidence / calc_support(items_add,vb_data,idx2item,9835)
         #print('items',items,'combination_set',combination_set,confidence,lift,calc_support(suppRec,vb_data,idx2item,9835),calc_support(items_base,vb_data,idx2item,9835),calc_support(items_add,vb_data,idx2item,9835))
         if(confidence>0.1):
           f.write(str(items))
           f.write(',')
           f.write(str(items_base))
           f.write(',')
           f.write(str(items_add))
           f.write(',')
           f.write(str(calc_support(suppRec,vb_data,idx2item,9835)))
           f.write(',')
           f.write(str(confidence))
           f.write(',')
           f.write(str(lift)+'\n')
           OrderedStatistic=(frozenset(items_base), frozenset(items_add), confidence, lift)
       #print(OrderedStatistic)
       f.close()

       return L, support_list,OrderedStatistic

   def get_result(self):
        print()
        return self.support_list


def output_handling(support_list):
	L = []
	for itemset, count in sorted(support_list.items(), key=lambda x: len(x[0])):
		itemset = tuple(sorted(list(itemset), key=lambda x: (x)))
		if len(L) == 0:
			L.append([itemset])
		elif len(L[-1][0]) == len(itemset):
			L[-1].append(itemset)
		elif len(L[-1][0]) != len(itemset):
			L[-1] = sorted(L[-1])
			L.append([itemset])
		else: raise ValueError()
	if len(L) != 0: L[-1] = sorted(L[-1])
	L = tuple(L)
	support_list = dict((tuple(sorted(list(k), key=lambda x: (x))), v) for k, v in support_list.items())
	return L, support_list
def compute_vertical_bitvector_data(data):
	#---build item to idx mapping---#
	idx = 0
	item2idx = {}
	for transaction in data:
		for item in transaction:
                 item=item.strip()
                 if not item in item2idx:
                       item2idx[item] = idx
                       idx += 1
	idx2item = { idx : item for item, idx in item2idx.items() }
	#---build vertical data---#
	vb_data = np.zeros((len(item2idx), len(data)), dtype=int)
	for trans_id, transaction in enumerate(data):
		for item in transaction:
			vb_data[item2idx[item.strip()], trans_id] = 1
	
	print('Data transformed into vertical bitvector representation with shape: ', np.shape(vb_data))
	return vb_data, idx2item
def GetData(transactions):
    transaction_index_map={}
    __num_transaction = 0
    items=[]
    for transaction in transactions:

        for item in transaction:
            if item not in transaction_index_map:
                items.append(item)
                transaction_index_map[item] = set()
            transaction_index_map[item].add(__num_transaction)
        __num_transaction += 1
    return transaction_index_map
    
def write_result(result, result_path):
	if len(result[0]) == 0: print('Found 0 frequent itemset, please try again with a lower minimum support value!')
	with open(result_path, 'w', encoding='big5') as file:
		file_data = csv.writer(file, delimiter=',', quotechar='\r')
		for itemset_K in result[0]:
			for itemset in itemset_K:
				output_string = ''
				for item in itemset: output_string += str(item)+' '
				output_string += '(' + str(result[1][itemset]) +  ')'
				file_data.writerow([output_string])
	print('Results have been successfully saved to: %s' % (result_path))

data=readData('data.csv')
#pdata=GetData(data)
#print(pdata)
#df = pd.DataFrame(te_ary, columns=te.columns_)
#df=df.applymap(lambda x: 1 if x==True else 0)
#myData=df.apply(pd.value_counts).T.sort_values(by=[1],ascending=False)
#Names=myData.index
#Freq=myData[1].values
#mylist=df.values.tolist()
#mydict=dict(zip(Names, mylist))
#data=mydict
result =eclat_runner.eclat(data,0.006)
write_result(result,'out.txt')
