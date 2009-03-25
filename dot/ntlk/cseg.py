# -*- coding: utf-8 -*-
import re,bsddb,os
from nltk.tokenize.api import TokenizerI
import nltk
"""
加载基于BSDDB数据库的分词字典
"""
class BSDDictLoader(object):
    def load(self):
        filename = os.path.dirname(__file__) + '/../data/dict.dat'
        self.d = bsddb.btopen(filename, 'c')
        return self.d
    def close(self):
        self.d.close()
class SimpleTokenizer(TokenizerI):
    def __init__(self):
        TokenizerI.__init__(TokenizerI)
        loader = BSDDictLoader()
        self.dict = loader.load()
    def tokenize(self, sentence):
            try:
                sentence = sentence.decode('utf-8')
            except:
                print 'utf-8 problem'
                return []
            sentence = re.sub(u"[。，,！……!《》<>\"':：？\?、\|“”‘’；]", " ", sentence)
            length = len(sentence)
            i = length
            result = []
            while True:
                if i <= 0:break
                found = - 1
                tempi = i
                tok = sentence[i - 1:i]
                while re.search("[0-9A-Za-z\-\+#@_\.]{1}", tok) <> None:
                    i -= 1
                    tok = sentence[i - 1:i]
                if tempi - i > 0:
                    result.append(sentence[i:tempi].lower().encode('utf-8'))
                    
                for j in xrange(4, 0, - 1):
                    if i - j < 0:continue
                    utf8Word = sentence[i - j:i].encode('utf-8')
                    if(self.dict.has_key(utf8Word)):
                        found = i - j
                        result.append(utf8Word)
                        break
    
                if found == - 1:
                    if i < length and sentence[i].strip() == "":
                        result.append(sentence[i - 1].encode('utf-8'))
                    elif(sentence[i - 1:i].strip() != ""):
                        if len(result) > 0 and len(result[ - 1]) < 12:
                            result.append(sentence[i - 1:i].encode('utf-8') + result[ - 1])
                        else:
                            result.append(sentence[i - 1:i].encode('utf-8'))
                    i -= 1
                else:
                    i = found
            goodR = []
            for w in result:
                if w.strip() <> "":
                    goodR.append(w)
            return goodR
if __name__ == '__main__':
    a = SimpleTokenizer()
    a.tokenize("谷歌安装IBM JDK 对于jdk有很多种选择，可以通过emerge -s jdk列出，我的环境以IBM产品为主，因此选择安装ibm jdk，其已经包含在Gentoo官方ebuild中，可以直接emerge，但jdk安装文件因为license 问题没有放入Gentoo mirror，需要自己下载，手工放入Portage，再继续emerge。 ibm jdk 目前最新版本是1.5（也称为 5.0)...")

