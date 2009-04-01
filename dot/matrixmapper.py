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
#initVM(CLASSPATH)
#Candidate Label Threshold 
CLT = 0.95
FACTOR = 0.1
TITLE_FIELD_BOOST = 1.7

class MatrixMapper(object):
    def __init__(self, STOP_WORDS=StopAnalyzer.ENGLISH_STOP_WORDS):
        self.pe = pextractor.PhraseExtractor()
        self.STOP_WORDS = STOP_WORDS
        self.analyzer = StandardAnalyzer(STOP_WORDS)
    def get_cs_by_lucene_doc(self, docs, context):        
        doc_size = len(docs)
        lucene_ids = []
        categories = []
        for id in range(doc_size):
            link = docs[id].get("link")
            lucene_ids.append(int(docs[id].get("id")))
            entry = dao.get_by_link(link, Entry)
            # TODO boost title field
            summary = entry.summary[:200]
            #if entry.category != '默认':
                #categories.append(entry.category)
            stream = self.analyzer.tokenStream("summary", StringReader(summary)) 
            for s in stream:
                context.tokens.append(s.term())
            stream = self.analyzer.tokenStream("title", StringReader(entry.title)) 
            for s in stream:
                context.title_field.append(len(context.tokens))
                context.tokens.append(s.term())
                
            context.term_doc_range.append(len(context.tokens))
        #print 'tokens:',len(context.tokens)
        return self.pe.extract(context), lucene_ids, categories
    
    def add2matrix(self, tpv, all, term_row, lucene_ids, i):
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
        for i in range(len(lucene_ids)):
            tpv = TermPositionVector.cast_(ireader.getTermFreqVector(lucene_ids[i], 'summary'))
            self.add2matrix(tpv, all, term_row, lucene_ids, i)
            """
                TODO:给属于标题的term加权
            """
            tpv = TermPositionVector.cast_(ireader.getTermFreqVector(lucene_ids[i], 'title'))
            self.add2matrix(tpv, all, term_row, lucene_ids, i)
        
        # 对label进行分词            
        analyzer = CJKAnalyzer()
        labelmatrix = zeros((len(all), len(labels)))
        label_term = []
        all_weight_table = {}
        sum_pow_label = []
        for i in range(len(labels)):
            sum_pow_label.append(labels[i].label_weight)
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
                label_term.append(token.term())                
                if term_row.has_key(token.term()):
                    row = term_row[token.term()]
                    terms.append(token.term())
                    docs_with_current_term = all[row]
                    a = []
                    for j in range(len(docs_with_current_term)):
                        if docs_with_current_term[j] != 0:                                            
                            if c == 0:
                                nonzero_index.append(j)
                            if c == 0 or j in nonzero_index:
                                
                                weight_row[j] = weight_row.get(j, 0) + docs_with_current_term[j] * labels[i].label_weight 
                            else:
                                # 加1防止权重之积为0
                                # 针对第一次出现在nonzero_index中而在后面的过程中没有出现的doc  ,乘以-100使得权重乘积最小表示当前label不适用于此doc                              
                                weight_row[j] = (1 + docs_with_current_term[j] * labels[i].label_weight) * (- 100)
                        # 针对第一次没有在nonzero_index中而在后面的过程中出现的doc 
                        elif docs_with_current_term[j] == 0 and j in nonzero_index:
                            # 加1防止权重之积为0
                            weight_row[j] = (1 + docs_with_current_term[j] * labels[i].label_weight) * (- 100)
                    c += 1
                else:
                    is_incomplete = True
                
            # bugfix:如果当前label经分词后，不是所有的term都在全部doc的term中，那么放弃当前label,舍之。
            if is_incomplete:
                weight_row={}
                    
                    
            for doc, weight in weight_row.items():  
                last = all_weight_table.get(doc)
                # 如果doc已经存在，那么用已经存在的doc-label权重比较当前的权重，如果当前的更大则替换已经存在的，即选择最大权重的label
                if last:
                    if last.id < weight and weight > 0:
                        labels[i].id = weight
                        all_weight_table[doc] = labels[i]
                else:
                    labels[i].id = weight
                    all_weight_table[doc] = labels[i]
        #for k, v in all_weight_table.items():
            #print k + 1, v.text,v.id
        return all_weight_table.values()
            
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
        return (tf / float(terms_length)) * abs(math.log((dtf - tf / 2.0) / docs_length))
    def build(self, docs):
        context = Context()
        results, lucene_ids , categories = self.get_cs_by_lucene_doc(docs, context)
        results_size = len(results)
        doc_size = len(docs)
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
            for j in range(rank):
                m = - 100
                index = - 1
                for i in range(len(u)):            
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