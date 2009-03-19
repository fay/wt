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
    

    from dot.context import Context,Token
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
        stream = analyzer.tokenStream("fieldname", StringReader(all))    
        for s in stream:
            
            #if (last_type == '<ALPHANUM>' or last_type == '<HOST>') and (s.type() == '<ALPHANUM>' or s.type() == '<HOST>'):
                #all.append(' ')
                #pass
            #last_type = s.type()
            token = Token()
            token.text = s.termText()
            token.offset =s.termLength()
            token.doc = id
            allToken.append(token)
            allText.append(s.termText())
            c += 1
        docRange[c] = id
        #all = sorted(all,cmp=lambda x,y:cmp(x.termText(),y.termText()))
        id += 1
    context.tokens = allText

    #context.tokens.sort()
    #for i in context.tokens:
        #i,i.doc
    
    #print s
    
    context.text = ''
    context.token_types = tokenType
    context.docs = entries
    print len(all) 
    from dot.lingo import pextractor
    import time
    start = time.time()
    pe = pextractor.PhraseExtractor()
    results = pe.extract(context)
    count = 0
    if 1:
        for i in results:
            if len(re.sub('[,.。,:\n的]'.decode('utf-8'),'',i.text.strip())) > 2 and i.freq > 2 and len(i.text) < 20: 
                print re.sub('[,.。,:\n]','',i.text.strip()),i.freq,context.tokens[context.suffix[i.id]:context.suffix[i.id] + context.lcp[i.id]]
    print (time.time() - start)
    #dm = getDictManager()
    #words_dict= featurex.tf_idf(entries, dm.seg_dict)
    #doc1 = featurex.Document(entries.encode('utf-8'),dm)
    #doc2 = featurex.Document(entries[0].encode('utf-8'), dm)
    #for i in words_dict.values():
        #print i.word,i.frequency,i.feature_value,i.tfidf
    #print similitude_doc_cos(doc1, doc2)
    