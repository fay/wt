# -*- coding:utf-8 -*-
import os
BASE = os.path.dirname(__file__)
CHINESE_FEATURE_DICT = BASE + '/data/sougou_dict.txt'
file = 'cixing.txt'
STOP_CIXING = ['ADV','AUX','CONJ','PREP','PRON','STRU']
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

    

if __name__ == "__main__":
    a = FeatureDictLoader()
    b = a.load()
    