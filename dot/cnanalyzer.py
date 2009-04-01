# -*- coding: utf-8 -*-
"""
pylucene 中文分词分析器
"""
#from dot.featurex import *
from lucene import PythonAnalyzer, CLASSPATH, initVM, \
    StringReader, PythonTokenStream, Document, RAMDirectory, Hit, \
    Field, IndexWriter, Token, StopAnalyzer, StandardAnalyzer, CJKAnalyzer, IndexReader, TermPositionVector
#from dot import cseg
import os
IO_BUFFER_SIZE = 2048
STORE_DIR = os.path.dirname(__file__) + '/index'

initVM(CLASSPATH)
"""
加载基于BSDDB数据库的分词字典
"""
class BSDDictLoader(object):
    def load(self):
        #Google App Engine 不支持此模块
        import bsddb
        filename = os.path.dirname(__file__) + '/data/dict.dat'
        self.d = bsddb.btopen(filename, 'c')
        return self.d
    def __del__(self):
        self.d.close()

class ChineseAnalyzer(PythonAnalyzer):
    def __init__(self):
        PythonAnalyzer.__init__(self)
        self.reader = None
        pass
    def tokenStream(self, fieldName, reader):
        
        class _tokenStream(PythonTokenStream):

            def __init__(self):
                super(_tokenStream, self).__init__()
                self.done = False
      
            def next(self):
                if not self.done:
                    self.done = True
                    text = JArray('char')(1024)
                    size = reader.read(text, 0, 1024)
                    return Token(text, 0, size, 0, size)
                return None

        return _tokenStream()
class StopAnalyzer2(PythonAnalyzer):

    def __init__(self, stopWords=None):

        if stopWords is None:
            self.stopWords = StopAnalyzer.ENGLISH_STOP_WORDS
        else:
            self.stopWords = stopWords

    def tokenStream(self, fieldName, reader):

        return StopFilter(LowerCaseFilter(LetterTokenizer(reader)),
                          self.stopWords)
if __name__ == '__main__':
    analyzer = CJKAnalyzer()
    directory = RAMDirectory()
    ireader = IndexReader.open(STORE_DIR)
    iwriter = IndexWriter(directory, StandardAnalyzer(), True)
    ts = ["javasd。 $#＃open所大家教唆犯地方地方即可解放大家空间艰苦奋斗矿井口地方", "所看看对抗赛不久交会法觉得拮抗剂"]
    for t in ts:
        doc = Document()
        doc.add(Field("fieldname", t,
                      Field.Store.YES, Field.Index.TOKENIZED,
                      Field.TermVector.WITH_POSITIONS_OFFSETS))
        iwriter.addDocument(doc)
    iwriter.optimize()
    iwriter.close()
    ireader = IndexReader.open(directory)
    tpv = TermPositionVector.cast_(ireader.getTermFreqVector(0, 'fieldname'))
    
    for (t, f, i) in zip(tpv.getTerms(), tpv.getTermFrequencies(), xrange(100000)):
        print 'term %s' % t
        print '  freq: %i' % f
        try:
            print '  pos: ' + str([p for p in tpv.getTermPositions(i)])
        except:
            print '  no pos'
        try:
            print '  off: ' + \
                  str(["%i-%i" % (o.getStartOffset(), o.getEndOffset())
                       for o in tpv.getOffsets(i)])
        except:
            print '  no offsets'
    text = "地方库 fd###  fd 反对 发"
    stream = analyzer.tokenStream("fieldname", StringReader(text))
    for s in stream:
        print s
    print dir(analyzer)
    
    
def b():
    from dot.searcher import Searcher, STORE_DIR
    from apps.wantown import dao
    from apps.wantown.models import Entry
    queries = ['java','google','mac','apple','淘宝','阿里巴巴','云计算','python','java google']
    searcher = Searcher()
    import datetime
    #fsock = open(str(datetime.datetime.now()),'w')
    for query in queries[0:]:
        hits = searcher.search(query)
        docs = []
        for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            docs.append(doc)
        from dot.matrixmapper import MatrixMapper
        STOP_WORDS = [u'a', u'an', u'and', u'are', u'as', u'at', u'be', u'but', u'by', u'for', u'if', u'in', u'into', 
                  u'is', u'it', u'no', u'not', u'of', u'on', u'or', u'such', u'that', u'the', u'their', u'then',
                  u'there', u'these', u'they', u'this', u'to', u'was', u'will', u'with',u'would'
                  # add by myself
                  # 的这个词应不应该作为stop word呢
                  u'i',u'been',u'about',u'的',u'么',u'是',u'个',u'不',u'们',u'这',u'那',u'我',u'你',u'很',u'了',u'以',u'与',u'为',u'一']
        mapper = MatrixMapper(STOP_WORDS)
        print 'docs:',len(docs)
        label = mapper.build(docs[0:20])
        for i in range(len(label)):
            if label[i].id != 0:
                print label[i].text,label[i].id,i+1
                #fsock.write(str(i+1)+ ","  + label[i].text.encode('utf-8') + "," + str(label[i].id)  + "\n")
        #fsock.write('----------------------------------\n')
    #fsock.close()
        #print a.title,a.summary,label[i][1]
    
    
def c():
    from apps.wantown import dao
    from apps.wantown.models import Entry,Category
    entries = Entry.objects.all()
    from dot.matrixmapper import MatrixMapper
    STOP_WORDS = [u'a', u'an', u'and', u'are', u'as', u'at', u'be', u'but', u'by', u'for', u'if', u'in', u'into', 
              u'is', u'it', u'no', u'not', u'of', u'on', u'or', u'such', u'that', u'the', u'their', u'then',
              u'there', u'these', u'they', u'this', u'to', u'was', u'will', u'with',
              # add by myself
              u'i',u'been',u'about',u'们',u'这',u'那',u'的',u'己',u'个',u'我',u'你',u'很',u'了',u'是',u'以',u'过',u'一',u'么',u'没',u'在']
    mapper = MatrixMapper(STOP_WORDS)
    ireader = IndexReader.open(STORE_DIR)
    for i in range(len(entries)):
        try:
            doc = ireader.document(i)
            link = doc.get('link')
            entry = dao.get_by_link(link, Entry)
            category = mapper.build([doc])
            weight = 0
            if category:
                cat = category[0].text
                weight = category[0].label_weight
            else:
                cat = '其他'
            entry.category = dao.save_category(cat,weight,'s')
            entry.save()
        except Exception,e:
            print i,e

    
def a():
    import os
    #loader = BSDDictLoader()
    #dic = loader.load()
    words_dict = {}
    from dot.searcher import Searcher, STORE_DIR
    from apps.wantown import dao
    from apps.wantown.models import Entry
    searcher = Searcher()
    hits = searcher.search("java")
    docs = []
    for hit in hits:
            doc = Hit.cast_(hit).getDocument()
            docs.append(doc)
    entries = []
    all = ''
    

    from dot.context import Context, Token
    context = Context()
    import re
    #all = re.sub('[0-9：;;/\(\)\t\[\]]（）\*＊#&','',all)
    #all = re.sub('[ +=-]',' ',all)

    analyzer = StandardAnalyzer()
    # doc id
    id = 0
    allToken = []
    allText = []
    pureText = ''
    c = 0
    docRange = {}
    for doc in docs[0:100]:
        link = doc.get("link")
        entry = dao.get_by_link(link, Entry)
        entries.append(entry.summary)
        all = entry.summary[:200] + entry.title
        pureText += all
        tokenType = []
        last_type = ''
        #all = """提起电吉他演奏，就必须提到布鲁斯音乐；提起最伟大的吉他演奏大师，人们首先会想到的是 Jimi Hendrix，但是说起依然在世的最伟大的吉他演奏家，名字只有一个——Eric Clapton爵士。自从上个世纪60年代布鲁斯摇滚乐以及布鲁斯吉他演奏成为了主流摇滚风格之后，在这种来源于黑人音乐的吉他演奏中，在所有除黑色外其他肤色的布鲁斯吉他演奏家之中，传奇人物Eric Clapton毫无疑问是其中最杰出的一位。在与Eric Clapton同时代的所有艺术家纷纷的离开人世，或者失去了原有的歌迷号召力之后，Eric Clapton是所有当年这些艺术家中为数不多的既然保持着自己高超的演奏技术以及强大的市场号召力的艺术家。
#　　
#Eric Clapton为人谦逊，在与其他出色的吉他演奏者比如Jimi Hendrix，B.B. King，Duane Allman，甚至后辈Stevie Ray Vaughan相比较的时候他总是非常谦恭，在与B.B. King以及Bob Dylan等人同台的时候他总是举止非常礼让，他是最有绅士风度的流行音乐家之一。同时，作为世界上最著名的吉他大师，Eric Clapton还经常热心的帮助包括英国著名流行音乐家Sting，Bon Jovi乐队主音吉他手Richie Sambora在内的其他一些音乐家去录制专辑或者拍摄音乐录影带，并且经常为一些音乐家担任吉他手作伴奏。Eric Clapton曾经协助过Bob Dylan，Aretha Franklin，Joe Cocker，Ringo Starr，Freddie King，Roger Waters等等近百位艺术家的专辑录制。 　　
#"""
        stream = analyzer.tokenStream("fieldname", StringReader(all))    
        for s in stream:
            
            #if (last_type == '<ALPHANUM>' or last_type == '<HOST>') and (s.type() == '<ALPHANUM>' or s.type() == '<HOST>'):
                #all.append(' ')
                #pass
            #last_type = s.type()
            token = Token()
            token.text = s.termText()
            token.offset = s.termLength()
            token.doc = id
            allToken.append(token)
            allText.append(s.term())
            print dir(s)
            c += 1
        docRange[len(allText)] = id
        #all = sorted(all,cmp=lambda x,y:cmp(x.termText(),y.termText()))
        id += 1
    context.tokens = allText
    
    #context.tokens.sort()
    #for i in context.tokens:
        #print i
    
    #print s
    
    context.text = ''
    context.token_types = tokenType
    context.docs = entries
    context.term_doc_range = docRange
    print len(all) 
    from dot.lingo import pextractor
    import time
    start = time.time()
    #pe = pextractor.PhraseExtractor()
    #results = pe.extract(context)
    count = 0
    r = docRange.keys()
    r.sort()
    if 0:
        for i in results:
            if len(i.text) > 1 and i.freq > 2 and len(i.text) < 20:
                id = i.id - 1
                lcp = context.lcp[id + 1]
                for f in range(i.freq):
                    begin = context.suffix[id]  
                    end = context.suffix[id] + lcp
    
                    for j in range(len(r)):
                        if begin < r[j]:
                            break
                    doc = docRange[r[j]]
                    #print context.tokens[begin:end],i.freq,begin,doc
                    if end > r[j]:
                        print 'not in the same doc'
                    id += 1
                #print  i.text.strip(), i.freq,i.doc_freq
    #print (time.time() - start)
    from dot.matrixmapper import MatrixMapper
    mapper = MatrixMapper()
    mapper.build(docs[:100])
   
    #print pureText
    import sys
    from dot.lingo import suffixsorter as ss
    #for i in range(len(context.suffix)):
     #   s = pe.list2str(context.tokens)
      #  sys.stdout.write('%d\t%d\t%s\n' % (context.suffix[i], context.lcp[i], context.tokens[context.suffix[i]:context.suffix[i] + 10]))
    #dm = getDictManager()
    #words_dict= featurex.tf_idf(entries, dm.seg_dict)
    #doc1 = featurex.Document(entries.encode('utf-8'),dm)
    #doc2 = featurex.Document(entries[0].encode('utf-8'), dm)
    #for i in words_dict.values():
        #print i.word,i.frequency,i.feature_value,i.tfidf
    #print similitude_doc_cos(doc1, doc2)
    """
ibm jdk 3 {3: 3}
不同 3 {4: 2, 7: 1}
使用 3 {8: 2, 7: 1}
可以 10 {8: 3, 3: 2, 4: 2, 7: 3}
处理 3 {8: 3}
好的 3 {8: 1, 7: 2}
字体 5 {8: 2, 4: 3}
已经 4 {9: 1, 3: 1, 4: 1, 7: 1}
平滑 4 {8: 1, 4: 3}
应用 3 {8: 1, 4: 2}
手机上 3 {7: 3}
文本 3 {8: 3}
游戏 4 {7: 4}
环境 3 {1: 1, 3: 2}
的java 6 {1: 1, 2: 1, 5: 1, 7: 3}
的文 3 {8: 3}
设置 5 {4: 5}
软件 3 {1: 1, 7: 2}
运行 3 {1: 1, 7: 2}

"""
    
    