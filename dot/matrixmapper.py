# -*- coding:utf-8 -*-
from lucene import StandardAnalyzer, CJKAnalyzer, StringReader, initVM, CLASSPATH, TermPositionVector, IndexReader, StopAnalyzer, Term
from apps.wantown.models import Entry 
from apps.wantown import dao
from dot.context import Context
from dot.lingo import pextractor
from numpy import zeros, add, linalg, array, dot, transpose 
from numpy.linalg import norm
from dot.indexer import STORE_DIR
import math, os, re
from dot.ntlk.cseg import SimpleTokenizer

tokenizer = SimpleTokenizer()
#initVM(CLASSPATH)
#Candidate Label Threshold 
CLT = 0.95
FACTOR = 0.1
TITLE_FIELD_BOOST = 1.7

import threading  
class SaveLabelsThread(threading.Thread):  
    def __init__(self, all_labels,label_doc,entries,query):  
        self.all_labels = all_labels  
        threading.Thread.__init__(self)  
        self.entries = entries
        self.query = query
        self.label_doc = label_doc
    def run (self):  
        #for l in label_doc:
            
        for k,v in self.all_labels.items():
            for label in v:                
                try:
                    q = dao.distinct_query(self.query)
                    category = dao.save_category(label.text, label.id, 'd')
                    entry = self.entries[k]
                    ec = dao.save_entry_cat(q,entry, category, label.id)
                except Exception,e:
                    print e
                    
class MatrixMapper(object):
    def __init__(self, STOP_WORDS=StopAnalyzer.ENGLISH_STOP_WORDS):
        self.pe = pextractor.PhraseExtractor()
        self.STOP_WORDS = STOP_WORDS
        self.analyzer = StandardAnalyzer(STOP_WORDS)
        self.entries = []
    def get_cs_by_lucene_doc(self, docs, context):        
        doc_size = len(docs)
        lucene_ids = []
        categories = []
        for id in range(doc_size):
            link = docs[id].get("link")
            lucene_ids.append(int(docs[id].get("id")))
            entry = dao.get_by_link(link, Entry)
            self.entries.append(entry)
            # TODO boost title field
            summary = entry.summary[:200]
            #if entry.category != '其他':
                #categories.append(entry.category)
            stream = self.analyzer.tokenStream("summary", StringReader(summary))
            for s in stream:
                context.tokens.append(s.term())
                context.token_types.append(s.type())
            stream = self.analyzer.tokenStream("title", StringReader(entry.title))
            for s in stream:
                context.title_field.append(len(context.tokens))
                context.tokens.append(s.term())
                context.token_types.append(s.type())
            context.term_doc_range.append(len(context.tokens))
        #print 'tokens:',len(context.tokens)
        return self.pe.extract(context), lucene_ids, categories
    
    def add2matrix(self, tpv, all, term_row, lucene_ids, i,term_doc_freq):
        for (t, f) in zip(tpv.getTerms(), tpv.getTermFrequencies()):
            term = [0 for j in range(len(lucene_ids))]
            new = False
            if not term_row.has_key(t):
                term_row[t] = len(term_row)
                new = True
            row = term_row[t]
            if new:
                term[i] = f#self.tfidf(len(tpv.getTerms()), f, total_terms, dtf)
                all.append(term)
            else:
                all[row][i] = f
            term_doc_freq[t] = term_doc_freq.get(t,0) + 1
    """
        效率很低，弃用           
    """ 
    def product(self, termmatrix, labelmatrix):
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
    """
         取代label_assign方法
    """
    def assign(self, docs, labels, lucene_ids):
        term_row = {}
        all = []
        ireader = IndexReader.open(STORE_DIR)
        total_terms = 0
        term_doc_freq = {}
        for i in range(len(lucene_ids)):
            tpv = TermPositionVector.cast_(ireader.getTermFreqVector(lucene_ids[i], 'summary'))
            self.add2matrix(tpv, all, term_row, lucene_ids, i,term_doc_freq)
            """
                TODO:给属于标题的term加权
            """
            tpv = TermPositionVector.cast_(ireader.getTermFreqVector(lucene_ids[i], 'title'))
            self.add2matrix(tpv, all, term_row, lucene_ids, i,term_doc_freq)
        #for k,v in term_doc_freq.items():
         #   if v> 3:
          #      print k,v
        # 对label进行分词            
        analyzer = CJKAnalyzer()
        labelmatrix = zeros((len(all), len(labels)))
        label_term = []
        # doc -label:每个doc对应的label
        all_weight_table = {}
        #label -doc:每个label对应的doc
        label_doc = []
        label_doc_map = {}
        for i in range(len(labels)):
            nonzero_table = []
            # 一个label对应和所有doc的权重之积
            weight_table = []
            
            stream = analyzer.tokenStream('', StringReader(labels[i].text))
            terms = []            
            c = 0
            weight_row = {}
            nonzero_index = []  
            is_incomplete = False
            for token in stream:
                term = token.term()#token.decode('utf-8')#
                #print term
                if term_row.has_key(term):
                    row = term_row[term]
                    terms.append(term)
                    docs_with_current_term = all[row]
                    for j in range(len(docs_with_current_term)):
                        if docs_with_current_term[j] != 0:                                            
                            if c == 0:
                                nonzero_index.append(j)
                            if c == 0 or j in nonzero_index:
                                weight_row[j] = weight_row.get(j, 0) + docs_with_current_term[j] * term_doc_freq[term] * labels[i].label_weight 
                            else:
                                # 加1防止权重之积为0
                                # 针对第一次出现在nonzero_index中而在后面的过程中没有出现的doc  ,乘以-100使得权重乘积最小表示当前label不适用于此doc                              
                                weight_row[j] = (1 + docs_with_current_term[j] * term_doc_freq[term] * labels[i].label_weight) * (- 100)
                        # 针对第一次没有在nonzero_index中而在后面的过程中出现的doc 
                        elif docs_with_current_term[j] == 0 and j in nonzero_index:
                            # 加1防止权重之积为0
                            weight_row[j] = (1 + docs_with_current_term[j] * labels[i].label_weight) * (- 100)
                    c += 1
                else:
                    is_incomplete = True
            label_term.append(terms)
            # bugfix:如果当前label经分词后，不是所有的term都在全部doc的term中，那么放弃当前label,舍之。
            if is_incomplete:
                weight_row = {}
                    
                    
            for doc, weight in weight_row.items():  
                last = all_weight_table.get(doc)                
                if weight > 0:
                    if not label_doc_map.has_key(labels[i].text):    
                        #kc = dao.get_keyword_category_by_category(self.query, labels[i].text)
                        label_doc.append([ 0,labels[i].text,[]])
                        label_doc_map[labels[i].text] = len(label_doc) - 1
                    new_label = pextractor.Substring()
                    new_label.text = labels[i].text
                    new_label.id = weight
                    if last:
                        all_weight_table[doc].append(new_label)
                    else:
                        all_weight_table[doc] = [new_label]
                    label_doc[label_doc_map[labels[i].text]][2].append(doc)
                    label_doc[label_doc_map[labels[i].text]][0] += weight
                    
                    #try:
                     #   category = dao.save_category(labels[i].text, weight, 'd')
                      #  entry = self.entries[doc]
                       # ec = dao.save_entry_cat(entry, category, weight)
                    #except Exception,e:
                     #   print e
                    
                    #if last:
                     #   all_weight_table[doc].append(ec)
                    #else:
                     #   all_weight_table[doc] = [ec]
                # 如果doc已经存在，那么用已经存在的doc-label权重比较当前的权重，如果当前的更大则替换已经存在的，即选择最大权重的label
                #if last:
                #    if last.id < weight and weight > 0:
                 #       labels[i].id = weight
                  #      all_weight_table[doc] = labels[i]
                #else:
                 #   labels[i].id = weight
                  #  all_weight_table[doc] = labels[i]
        label_doc.sort(reverse=True)
        for k, v in all_weight_table.items():
            v.sort(reverse=True)
                
        # 因为map中键为连续的整数值，哈希算法会把他按从小到大的位置排放,所以直接返回的values是已经排好序的了
        thread = SaveLabelsThread(all_weight_table,label_doc,self.entries,self.query)
        thread.start()
        return all_weight_table,label_doc
            
    """
        废弃
    """
    def label_assign(self, docs, labels, lucene_ids):
        term_row = {}
        all = []
        ireader = IndexReader.open(STORE_DIR)
        total_terms = 0
        for i in range(len(lucene_ids)):
            tpv = TermPositionVector.cast_(ireader.getTermFreqVector(lucene_ids[i], 'summary'))
            self.add2matrix(tpv, all, term_row, lucene_ids, i)
            tpv = TermPositionVector.cast_(ireader.getTermFreqVector(lucene_ids[i], 'title'))
            self.add2matrix(tpv, all, term_row, lucene_ids, i)
        
        # 对label进行分词            
        analyzer = CJKAnalyzer()
        labelmatrix = zeros((len(all), len(labels)))
        label_term = []
        for i in range(len(labels)):
            if not labels[i].is_candicate_label and len(labels[i].text) >= 3:
                label_term.append([])
                continue
            #print labels[i].text,labels[i].id
            stream = analyzer.tokenStream('', StringReader(labels[i].text))
            terms = []
            for token in stream:
                if term_row.has_key(token.term()):
                    # weighting
                    termdocs = ireader.termDocs(Term('summary', token.term()))
                    count = 0
                    span = 0
                    terms.append(token.term())
                    while termdocs.next():
                        count += termdocs.freq()
                        span += 1
                    weight = labels[i].label_weight
                    #if float(span)/ireader.numDocs() >= 0.18 and not re.search('a-zA-z', token.term()):
                        #weight = 0
                    labelmatrix[term_row[token.term()]][i] = weight
            label_term.append(terms)
        termmatrix = array(all)
        termmatrix = transpose(termmatrix)
        #for i in range(len(labelmatrix[0])):
            #for j in range(len(termmatrix[0])):
        
        # row是doc,col是label  
        #p = self.product(termmatrix,labelmatrix)
        d = dot(termmatrix, labelmatrix)
        result = d / (norm(labelmatrix) * norm(termmatrix))
        doc_label = []
        for i in range(len(result)):
            m = - 1
            index = - 1
            group = []
            for j in range(len(result[i])):
                if result[i][j] > 0:
                    labels[j].id = result[i][j]
                    group.append(labels[j])
            # substring是按照id来排序的，这里正好用到
            group.sort()
            group.reverse()
            max_label = group[0]
            # i:doc number(just occur position in the docs)
            # label id
            # label score
            # 如果label自身并没有出现在当前doc中
            if not max_label.doc_freq.has_key(i):
                #print 'oringial:',labels[index].text
                count = 0
                overlap = ''
                for k in label_term[index]:
                    if term_row.has_key(k) and termmatrix[i][term_row[k]] != 0:
                        overlap = k
                        print k
                        count += 1
                # 至少有一个交集，并且长度大于等于2
                if count == 1 and len(overlap) >= 2 :
                    new_label = pextractor.Substring()
                    new_label.text = overlap
                    new_label.id = m
                    doc_label.append(group[0])
                    continue
                        
            #labels[index].id = m
            doc_label.append(group[0])
        return doc_label
    """
        计算tf-idf值
    """   
    def tfidf(self, terms_length, tf, docs_length, dtf):
        # results[i].freq - v可能为0,所以将v/2再相减
        return (tf / float(terms_length)) * abs(math.log((dtf - tf / 2.0) / (docs_length*10)))
    def build(self, docs,query):
        self.entries = []
        self.query = query
        context = Context()
        results, lucene_ids , categories = self.get_cs_by_lucene_doc(docs, context)
        results_size = len(results)
        doc_size = len(docs)
        stroplabels = {}
        for i in range(results_size):
            #删除一些类似‘在阿里巴巴’中的‘在’字,类似地还有‘...上’，‘...里’，‘和...’
            stream2 = tokenizer.tokenize(results[i].text.encode('utf-8'))
            if len(stream2) == 2 and len(results[i].text)>=3:     
                if (len(stream2[0].decode('utf-8')) == 1 or len(stream2[1].decode('utf-8')) == 1):
                    results[i].text = len(stream2[0].decode('utf-8')) == 1 and stream2[1].decode('utf-8') or stream2[0].decode('utf-8')
                elif (len(stream2[1].decode('utf-8')) - len(stream2[0].decode('utf-8'))) == 1 \
                        and len(stream2[1].decode('utf-8')) == len(results[i].text):
                    results[i].text = stream2[0].decode('utf-8')
            if stroplabels.has_key(results[i].text):
                same_label_name = stroplabels[results[i].text]
                results[i].freq += same_label_name.freq
                for k,v in same_label_name.doc_freq.items():                 
                    if results[i].doc_freq.has_key(k):
                        results[i].doc_freq[k] += v
                    else:
                        results[i].doc_freq[k] = v
            stroplabels[results[i].text] = results[i]
            
        results = stroplabels.values()
        results_size = len(results)
        # phrase doc matrix
        pdmatrix = zeros((results_size, doc_size))
        #for i in results:
            #print i.text,i.freq
        d = len(context.tokens)
        if results_size == 0:
            print 'no frequent phrase!'
            return []

        for i in range(results_size):
            doc_freq = results[i].doc_freq
            
            index = context.suffix[results[i].id]           
            # 如果有性能问题可以把title_field改为map
            is_title = False
            if index in context.title_field:
                is_title = True
            for k, v in doc_freq.items():
                # k is doc_id,v is doc freq
                # doc_length 所在doc的term数量
                doc_length = context.term_doc_range[k] - (k and context.term_doc_range[k - 1])                
                pdmatrix[i][k] = self.tfidf(doc_length, v, d, results[i].freq) * (is_title and TITLE_FIELD_BOOST or 1)
            results[i].label_weight = norm(pdmatrix[i])
            #if stroplabels.has_key(results[i].text):
               # stroplabels[results[i].text].label_weight+=results[i].label_weight
                
        if 1:
            # SVD-奇异值分解        
            u, s, v = linalg.svd(pdmatrix)
            
            # 试探以取得矩阵的秩
            rank = 1
            for k in range(1, len(s)):
                if norm(s[:k]) / norm(s) >= CLT:
                    rank = k
                    break
            
            # 取u中前rank列，选择最大的一个component,保存对应的label索引    
            maxes = {}
            lo = {}
            for j in range(rank):
                m = - 100
                index = - 1
                for i in range(len(u)): 
                    if u[i][j] > 0:
                        lo[i]=u[i][j]
                    if u[i][j] > m:
                        m = u[i][j]
                        # index 为 对应的label索引
                        index = i
                # 如果label之前已有则取均值
                if maxes.has_key(index):
                    maxes[index] = (maxes[index] + m) / 2.0
                else:
                    # 保存最大值
                    maxes[index] = m
    
            labels = []
            
            # k为索引，v为最大值
            for k, v in maxes.items():
                    #print results[k].text,k,v
                    #sub = pextractor.Substring()
                    #sub.text = results[k].text
                    temp = re.sub('[0-9 ]', '', results[k].text)
                    if temp == '':
                        results[k].text = temp
                    results[k].is_candicate_label = True
                    results[k].label_weight = v
                    labels.append(results[k])
                    
        return self.assign(docs, results, lucene_ids)