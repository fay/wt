# -*- coding:utf-8 -*-
import os
BASE = os.path.dirname(__file__)
CHINESE_FEATURE_DICT = BASE + '/data/cixing.txt'
ENGLISH_STOP_WORDS_DICT = BASE + '/data/stop_words'
"""
加载不能用于分类名称的词语－词性字典
"""
class CixingDictLoader(object):
    def load(self):
        separator = ','
        dictionary = {}
        ce = [CHINESE_FEATURE_DICT]
        for d in ce:
            try:
                self.text_dict = open(d, 'r')
            except IOError:
                print "IO Error"
                return
            all = self.text_dict.read()
            wf_list = all.split(separator) 
            for word in wf_list:        
                #按UTF-8存储  
                dictionary[word.decode('utf-8')] = None
        return dictionary
    def __del__(self):
        self.text_dict.close()
class EnglishStopWords(object):
    def __init__(self):
        fsock = open(ENGLISH_STOP_WORDS_DICT,'r')
        self.dict = []
        for word in fsock.readlines():
             self.dict.append(unicode(word.split('\n')[0]))
        fsock.close()
        

if __name__ == '__main__':
    a = CixingDictLoader()
    b = a.load()
    for k,v in b.items()[:10]:
        print k
    if b.has_key('而且'.decode('utf-8')):
        print 'ok'