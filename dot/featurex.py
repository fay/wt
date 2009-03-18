# -*- coding: utf-8 -*-
import os
import re
import math
import bsddb
from dot import cseg
#from apps.dot.segdb import CChar
from logging import getLogger
from cPickle import dump, load, Pickler, Unpickler


BASE = os.path.dirname(__file__)
CHINESE_FEATURE_DICT = BASE + '/data/sougou_dict.txt'
ENGLISH_FEATURE_DICT = BASE + '/data/westburylab.txt'
SEG_DICT_FILE_NAME = BASE + '/data/dict.dic'
CHINESE_PATTERN = '[\u4e00-\u9fa5]'
ENGLISH_PATTERN = '[0-9A-Za-z\-\+#@_\.]{1}'
PUNCTUATION_PATTERN = '[0-9\-\+#=/@_\.\(\)\*\[\]。、，？＋＝－／（）＃￥％＠！～｀]'


class CChar:
    """
        代表一个中文汉字
    """
    def __init__(self, char):
        self.char = char
    
    def __unicode__(self):
        return self.char
    
    def __str__(self):
        return self.__unicode__()
    
    def __hash__(self): #用Unicode码作为hash值返回，减去0x4e00是为了减小存储空间
        return ord(self.char) - int(0x4e00)
    
    def __eq__(self, char):
        return self.char == char
class DictManager:
    def __init__(self, seg_dict_loader, feature_dict_loader, stop_words_dict_loader):
        self.feature_dict = feature_dict_loader.load()
        self.seg_dict = seg_dict_loader.load()
        self.stop_dict = stop_words_dict_loader.load()
        
class DictLoader():
      def load(self):
          pass

"""
加载搜狗和westburylab的特征字典
"""
class FeatureDictLoader(DictLoader):
    def load(self):
        separator = '\t'
        dictionary = {}
        ce = [CHINESE_FEATURE_DICT]
        for d in ce:
            try:
                self.text_dict = open(d, 'r')
            except IOError:
                print "IO Error"
                return None
            for line in self.text_dict.readlines():        
                #得到一行键值对：word - frequency
                wf_list = line.split(separator)
                length = len(wf_list)
                if length >= 2:  
                    #按UTF-8存储  
                    dictionary[wf_list[0].decode('utf-8')] = wf_list[1]
        return dictionary
    def __del__(self):
        self.text_dict.close()

"""
加载基于BSDDB数据库的分词字典
"""
class BSDDictLoader(DictLoader):
    def load(self):
        #Google App Engine 不支持此模块
        filename = os.path.dirname(__file__) + '/data/dict.dat'
        self.d = bsddb.btopen(filename, 'c')
        return self.d
    def close(self):
        self.d.close()
   
class CWord:
    def __init__(self, word):
        self.word = word
    
    def __hash__(self):        
        for ch in word:
            pass
            

"""
加载定制的分词字典
"""     
class MySegDictLoader(DictLoader):
    
    def recursive(self, words, i):
        if(i == len(words)):
            return None
        return { CChar(words[i]) : self.recursive(words, i=i + 1)}
        
    def load(self):
        dictionary = {}
        self.f = file(BASE + '/data/d.bin', 'rb')
        unpickler = Unpickler(self.f)
        #dictionary = unpickler.load()
        return dictionary
    def __del__(self):
        self.f.close()
      
class StopWordsDictLoader(DictLoader):
    def load(self):
        dictionary = []
        self.f = open(BASE + '/data/stop_words', 'r')
        for line in self.f.readlines():
            dictionary.append(line.strip())
        return dictionary
    def __del__(self):
        self.f.close()
class Word:
    def __init__(self, word, doc_id, frequency=0, tf_doc=0, feature_value=0, tfidf=0):
        self.word = word
        self.frequency = frequency
        self.tf_doc = tf_doc
        self.feature_value = feature_value
        self.tfidf = tfidf
        self.doc_id = doc_id
    def __unicode__(self):
        return '%s : %d %f' % (self.word, self.frequency, self.feature_value)
 
class Document:
    def __init__(self, text, dict_manager):
        self.text = text
        self.words_dict = {}
        web_dict = dict_manager.feature_dict
        seg_dict = dict_manager.seg_dict
        stopwords_dict = dict_manager.stop_dict
        words = cseg.segWords3(seg_dict, self.text)
        D = 0x5f5e100
        Dw = 0
        #计算词频
        for word in words:
            word = word.decode('utf-8')
            if not self.words_dict.has_key(word):
                word = re.sub(PUNCTUATION_PATTERN, '', word)
                word_obj = Word(word, 1)
                self.words_dict[word] = word_obj
            else:
                self.words_dict[word].frequency += 1
        #计算特征值
        stop_words = []
        for word, word_obj in self.words_dict.items():
            if web_dict.has_key(word):
                num = self.words_dict[word].frequency / float(len(text))                
                num2 = 0
                Dw = float(web_dict[word])
                num2 = abs(math.log(D / Dw))
                w = self.words_dict[word]
                word_obj.feature_value = num * num2
            elif re.search(ENGLISH_PATTERN, word):
                num = self.words_dict[word].frequency / float(len(text))                
                #暂时将英语单词num2值设为1.0
                num2 = 1.0
                w = self.words_dict[word]
                word_obj.feature_value = num * num2
            else:
                #除了中文，暂时所有英文单词均不为stop_words
                stop_words.append(word)
        for word in stop_words:
            del self.words_dict[word]

def tf_idf(docs, seg_dict):
    words_dict = {}
    context = {}
    doc_id = 0
    for doc in docs:
        words = cseg.segWords3(seg_dict, doc.encode('utf-8'))
        #计算词频
        for word in words:
            word = word.decode('utf-8')
            if not words_dict.has_key(word):
                word = re.sub(PUNCTUATION_PATTERN, '', word)
                word_obj = Word (word, doc_id, 1)
                words_dict[word] = word_obj
            else:
                words_dict[word].frequency += 1
                words_dict[word].tf_doc += 1
        context[doc_id] = len(words)
        doc_id += 1
    for word in words_dict.values():
        tf = word.tf_doc / context[word.doc_id]
        idf = math.log(float(len(docs)) / float(word.frequency) or 1)
        word.tfidf = tf*idf
    return words_dict
"""
使用余弦定理得出相似度
"""
def similitude_doc_cos(doc1, doc2):
    #doc1,doc2向量乘积和
    sum0 = 0
    #doc1分向量平方和
    sum1 = 0
    #doc2分向量平方和
    sum2 = 0
    #doc1,doc2含有相同特征词的个数
    sum3 = 0
    words_dict1 = doc1.words_dict
    words_dict2 = doc2.words_dict
    if len(doc1.words_dict) == 0 or len(doc1.words_dict) == 0 :
        return 0
    for word, word_obj1 in words_dict1.items():
        if words_dict2.has_key(word):
            word_obj2 = words_dict2[word]
            sum0 += word_obj1.feature_value * word_obj2.feature_value
            sum1 += pow(word_obj1.feature_value, 2)
            sum2 += pow(word_obj2.feature_value, 2)
            sum3 += 1
    if (float(sum3) / len(words_dict1) <= 0.1) or ((float(sum3) / len(words_dict2)) <= 0.1):
        return 0
    sum1 = math.sqrt(sum1)
    sum2 = math.sqrt(sum2)
    return sum0 / (sum1 * sum2)                               
def getDictManager():
    my_seg_dict_loader = BSDDictLoader()#MySegDictLoader()
    feature_dict_loader = FeatureDictLoader()
    stopwords_dict_loader = StopWordsDictLoader()
    return DictManager(my_seg_dict_loader, feature_dict_loader, stopwords_dict_loader)

if __name__ == "__main__":
    dm = getDictManager()

    doc0 = Document("your mind ok", dm)
    doc1 = Document("your it hi".decode('utf-8'), dm)
    doc2 = Document("如果程序语言真的是一种语言的话，那么编程应该是一种文学创作，从这种意义上来说，我是个作家。 ".decode('utf-8'), dm)
    print similitude_doc_cos(doc1, doc0)
    
    
    