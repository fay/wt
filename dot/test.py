# -*- coding:utf-8 -*-
import os
BASE = os.path.dirname(__file__)
CHINESE_FEATURE_DICT = BASE + '/data/sougou_dict.txt'
file = 'cixing.txt'
STOP_CIXING = ['ADV','AUX','CONJ','PREP','PRON','QUES','STRU']
"""
加载搜狗和的特征字典
"""
class FeatureDictLoader(object):
    def load(self):
        separator = '\t'
        dictionary = {}
        fsock = open(file,'w')
        ce = [CHINESE_FEATURE_DICT]
        for d in ce:
            try:
                self.text_dict = open(d, 'r')
            except IOError:
                print "IO Error"
                return
            for line in self.text_dict.readlines():        
                #得到一行键值对：word - (frequency,cixing list)
                wf_list = line.split(separator)
                length = len(wf_list)
                if length >= 3:  
                    #按UTF-8存储  
                    cixing_list = wf_list[2].split(',')
                    for cixing in cixing_list:
                        if cixing in STOP_CIXING:
                            fsock.write(wf_list[0]+',')
                            break
        return dictionary
    def __del__(self):
        self.text_dict.close()

def product(termmatrix,labelmatrix):
    row = []            
    for i in range(len(termmatrix)):
        col = []
        for j in range(len(labelmatrix[0])):
            #k是a的列，b的行
            e = []
            for k in range(len(termmatrix[0])):
                c = termmatrix[i][k]                    
                d = labelmatrix[k][j]
                e.append(c * d)
            col.append(sum(e))
        row.append(col)   
    return row

if __name__ == "__main__":
    #a = FeatureDictLoader()
    #b = a.load()
    a= [[1,2,3],
        [3,4,5]]
    b = [[1,2,3],
         [1,2,4],
         [3,2,4]]
    
    print product(a,b)
    import numpy
    print numpy.dot(a,b)