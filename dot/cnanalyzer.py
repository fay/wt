# -*- coding: utf-8 -*-
"""
pylucene 中文分词分析器
"""
from dot.featurex import *
from lucene import PythonAnalyzer, CLASSPATH, initVM, \
    StringReader, PythonTokenStream, Document, RAMDirectory,Hit, \
    Field, IndexWriter, Token,StopAnalyzer,StandardAnalyzer,CJKAnalyzer,IndexReader,TermPositionVector
from dot import cseg
IO_BUFFER_SIZE = 2048
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
    
    for (t,f,i) in zip(tpv.getTerms(),tpv.getTermFrequencies(),xrange(100000)):
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
    
    
    
    
    
    
def a():
    import os
    #loader = BSDDictLoader()
    #dic = loader.load()
    words_dict  = {}
    from dot.searcher import Searcher,STORE_DIR
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
    for doc in docs[0:10]:
        link = doc.get("link")
        entry = dao.get_by_link(link, Entry)
        entries.append(entry.summary )
        all += entry.summary
    import re
    re.sub('[0-9，。,.：:;;的\n]','',all)
    print len(all)
    from dot.lingo import pextractor
    pe = pextractor.PhraseExtractor()
    results = pe.extract(all)
    for i,v in results.items():
        i = i.strip()
        if len(i) > 4 and v > 2:
            print i,v 
    #dm = getDictManager()
    #words_dict= featurex.tf_idf(entries, dm.seg_dict)
    #doc1 = featurex.Document(entries.encode('utf-8'),dm)
    #doc2 = featurex.Document(entries[0].encode('utf-8'), dm)
    for i in words_dict.values():
        print i.word,i.frequency,i.feature_value,i.tfidf
    #print similitude_doc_cos(doc1, doc2)
    