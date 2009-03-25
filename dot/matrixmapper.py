# -*- coding:utf-8 -*-
from lucene import StandardAnalyzer, CJKAnalyzer,StringReader, initVM, CLASSPATH, TermPositionVector, IndexReader,StopAnalyzer
from apps.wantown.models import Entry 
from apps.wantown import dao
from dot.context import Context
from dot.lingo import pextractor
from numpy import zeros, add, linalg, array,dot,transpose 
from numpy.linalg import norm
import math, os,re
#initVM(CLASSPATH)
STORE_DIR = os.path.dirname(__file__) + '/index'
#Candidate Label Threshold 
CLT = 0.95
FACTOR = 0.1
TITLE_FIELD_BOOST = 1.7

class MatrixMapper(object):
    def __init__(self,STOP_WORDS=StopAnalyzer.ENGLISH_STOP_WORDS):
        self.pe = pextractor.PhraseExtractor()
        
        self.analyzer = StandardAnalyzer(STOP_WORDS)
    def get_cs_by_lucene_doc(self, docs, context):        
        doc_size = len(docs)
        lucene_ids = []
        for id in range(doc_size):
            link = docs[id].get("link")
            lucene_ids.append(int(docs[id].get("id")))
            entry = dao.get_by_link(link, Entry)
            # TODO boost title field
            summary = entry.summary[:200]
            stream = self.analyzer.tokenStream("summary", StringReader(summary)) 
            for s in stream:
                context.tokens.append(s.term())
            stream = self.analyzer.tokenStream("title", StringReader(entry.title)) 
            for s in stream:
                context.title_field.append(len(context.tokens))
                context.tokens.append(s.term())
                
            context.term_doc_range.append(len(context.tokens))
        #print 'tokens:',len(context.tokens)
        return self.pe.extract(context), lucene_ids
        
        #for i in range(results_size):
            #print pdmatrix[i], results[i].text
    def label_assign(self,docs,labels,lucene_ids):
        term_row = {}
        all = []
        ireader = IndexReader.open(STORE_DIR)
        tpvs = []
        total_terms = 0
        for i in range(len(lucene_ids)):
            tpv = TermPositionVector.cast_(ireader.getTermFreqVector(lucene_ids[i], 'summary'))
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
        analyzer = CJKAnalyzer()
        labelmatrix = zeros((len(all),len(labels)))
        for i in range(len(labels)):
            stream = analyzer.tokenStream('',StringReader(labels[i].text))
            for token in stream:
                if term_row.has_key(token.term()):
                    labelmatrix[term_row[token.term()]][i] = 1
        
        termmatrix = array(all)
        termmatrix = transpose(termmatrix)
        result = dot(termmatrix,labelmatrix) / (norm(labelmatrix)*norm(termmatrix))
        doc_label =[]
        
        for i in range(len(result)):
            m = -1
            index= -1
            for j in range(len(result[i])):
                if m < result[i][j]:
                    m = result[i][j]
                    index = j
            # i:doc number(just occur position in the docs)
            # label id
            # label score
            labels[index].id = m
            doc_label.append(labels[index])
        return doc_label
        
    def tfidf(self, terms_length, tf, docs_length, dtf):
        # results[i].freq - v可能为0,所以将v/2再相减
        return (tf / float(terms_length)) * abs(math.log((dtf - tf / 2.0) / docs_length))
    def build(self, docs):
        context = Context()
        results, lucene_ids = self.get_cs_by_lucene_doc(docs, context)
        results_size = len(results)
        doc_size = len(docs)
        # phrase doc matrix
        pdmatrix = zeros((results_size, doc_size)).tolist()
        #for i in results:
            #print i.text
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
                doc_length = context.term_doc_range[k] - (k and context.term_doc_range[k - 1])                
                pdmatrix[i][k] = self.tfidf(doc_length, v, d, results[i].freq) * (is_title and TITLE_FIELD_BOOST or 1)
        u, s, v = linalg.svd(pdmatrix)
        #print u, '-------------------\n', s, '------------------------\n', v
        #print len(pdmatrix), len(pdmatrix[0]), len(u), len(u[0])
        sum = 0
        for i in s:
            sum += i * i
        frobenius_norm = math.sqrt(sum)
        
        rank = 1
        for k in range(1,len(s)):
            sum = 0
            for i in s[:k]:
                sum += i * i
            if math.sqrt(sum) / frobenius_norm >= CLT:
                rank = k
                break
        maxes ={}

        n = -100
        for j in range(rank):
            m = -100
            index = -1
            for i in range(len(u)):            
                if u[i][j] > m:
                    m = u[i][j]
                    index = i
            if maxes.has_key(index):
                maxes[index] = (maxes[index] + m)/2.0
            else:
                maxes[index] = m
            if m > n:
                n = m

        labels = []
        for k,v in maxes.items():
                #print results[k].text,k,v
                sub = pextractor.Substring()
                sub.text = results[k].text
                sub.id = v
                labels.append(sub)
        labels.sort()

        
        for i in range(len(labels)):
            
            temp = re.sub('[0-9 ]','',labels[i].text)
            if temp == '':
                labels[i].text = temp
                
            
        return self.label_assign(docs,labels,lucene_ids)
        #return labels[::-1]
            
        #暂时不考虑其他terms
        if 0:
            term_row = {}
            all = []
            ireader = IndexReader.open(STORE_DIR)
            tpvs = []
            total_terms = 0
            for i in range(len(lucene_ids)):
                tpv = TermPositionVector.cast_(ireader.getTermFreqVector(lucene_ids[i], 'summary'))
                tpvs.append(tpv)
                total_terms += len(tpv.getTerms())
            for tpv in tpvs:
                for (t, f) in zip(tpv.getTerms(), tpv.getTermFrequencies()):
                    term = [0 for j in range(len(lucene_ids))]
                    new = False
                    if not term_row.has_key(t):
                        term_row[t] = len(term_row)
                        new = True
                    row = term_row[t]
                    if new:
                        term[i] = self.tfidf(len(tpv.getTerms()), f, total_terms, dtf)
                        all.append(term)
                    else:
                        all[row][i] = f
    
            pdmatrix.extend(all)
            print pdmatrix
                #print t,f
                #docids = terms_doc.get(t)
                #if not docids:
                   # docids = []
                #docids.append((i, f))
                #terms_doc[t] = docids
        
        #tempmatrix = zeros((len(terms_doc), len(lucene_ids)))  
        #print (len(terms_doc), len(lucene_ids))
        #for i in range(len(terms_doc)):
            #for id_f in terms_doc.values()[i]:
                #print terms_doc.values()[i]
                #tempmatrix[i][id_f[0]] = id_f[1]
        #for i in tempmatrix:
            #print i
    
        """    
4 2 0.0625 8.04580193319 11i r12 [0.50286262082449418, 0.50286262082449418]
2 2 0.0148148148148 9.14441422186 2004年 [0.13547280328681505]
2 1 0.0416666666667 8.73894911375 39 t [0.19419886919448562, 0.36412287973966051]
2 2 0.0169491525424 9.14441422186 anysql db查询组件 [0.15499007155694941]
2 2 0.0148148148148 9.14441422186 aul mydul [0.13547280328681505]
6 1 0.030303030303 7.43966612962 bookmark del.icio.us posted chedong [0.10782124825538537, 0.11999461499389662, 0.29758664518486361, 0.30998608873423295, 0.091847729995328281, 0.22544442817035124]
2 1 0.04 8.73894911375 bookmark del.icio.us posted chedong java [0.1078882606636031, 0.3495579645500741]
2 1 0.0161290322581 8.73894911375 bookmark del.icio.us posted chedong jvm java [0.36412287973966051, 0.14095079215728792]
4 1 0.0625 7.89165125336 bookmark delicious saved [0.17155763594270973, 0.65763760444705399, 0.46421477960968516, 0.49322820333529049]
2 1 0.0625 8.73894911375 bookmark delicious saved fenng 4alipay java [0.72824575947932102, 0.54618431960949076]
2 2 0.05 9.14441422186 c frequent item set [0.45722071109300083]
2 2 0.018691588785 9.14441422186 c与java [0.17092363031514046]
2 2 0.018691588785 9.14441422186 c中 [0.17092363031514046]
2 2 0.018691588785 9.14441422186 c是微软公司 [0.17092363031514046]
2 2 0.0148148148148 9.14441422186 cloudbase 1.2 [0.13547280328681505]
3 1 0.00909090909091 8.22812348999 copy作者eygle发布在eygle.com [0.075487371467760189, 0.14435304368396246, 0.07480112263623509]
2 2 0.0588235294118 9.14441422186 dialog box [0.53790671893294206]
2 1 0.037037037037 8.73894911375 doesn t [0.25702791511034861, 0.32366478199080934]
2 1 0.008 8.73894911375 dom和sax [0.085675971703449524, 0.069911592910014822]
2 2 0.0125 9.14441422186 flash图表 [0.11430517777325021]
2 1 0.00625 8.73894911375 flash实现 [0.057117314468966354, 0.054618431960949079]
2 2 0.0606060606061 9.14441422186 full text search [0.55420692253697068]
2 2 0.025974025974 9.14441422186 gb下 [0.23751725251584457]
2 1 0.00917431192661 8.73894911375 gentoo linux t43 [0.10528854353917895, 0.080173845080292225]
4 1 0.00625 7.89165125336 google maps [0.13189839234740833, 0.079713649023885336, 0.049322820333529055]
2 2 0.016393442623 9.14441422186 google发布 [0.14990842986655764]
4 2 0.0125 8.04580193319 google手机 [0.064685666011185639, 0.050913879053965473, 0.10057252416489884]
2 2 0.0125 9.14441422186 google手机卫星地图 [0.11430517777325021]
4 3 0.0193548387097 8.22812348999 google的 [0.076617973333637346, 0.15925400303198439]
2 2 0.0129032258065 9.14441422186 google的移动首页 [0.11799244157238731]
2 1 0.03125 8.73894911375 have been [0.30134307288799489, 0.27309215980474538]
2 2 0.0555555555556 9.14441422186 highly scalable [0.50802301232555647]
4 1 0.0333333333333 7.89165125336 i am [0.076617973333637346, 0.27212590528843611, 0.26305504177882161, 0.26305504177882161]
2 1 0.0333333333333 8.73894911375 i put together [0.27309215980474538, 0.29129830379172839]
3 1 0.0333333333333 8.22812348999 i've been [0.3291249395994344, 0.31646628807637922, 0.27427078299952867]
2 2 0.0172413793103 9.14441422186 ibm db2信息中心 [0.15766231417000026]
3 3 0.0275229357798 8.73894911375 ibm jdk [0.24052153524087669]
2 1 0.0161290322581 8.73894911375 ibm的jvm [0.36412287973966051, 0.14095079215728792]
3 3 0.0277777777778 8.73894911375 jar包 [0.24274858649310699]
2 2 0.0153846153846 9.14441422186 java 2d api [0.14068329572092333]
3 1 0.012987012987 8.22812348999 java php [0.088474446128880224, 0.076898350373699617, 0.10685874662319299]
2 1 0.008 8.73894911375 java和 [0.084844166152930597, 0.069911592910014822]
2 1 0.00653594771242 8.73894911375 java已经输掉 [0.19419886919448562, 0.057117314468966354]
2 2 0.0215053763441 9.14441422186 java开发 [0.19665406928731219]
2 2 0.0135135135135 9.14441422186 java手机游戏 [0.12357316516027049]
2 1 0.00675675675676 8.73894911375 java游戏 [0.060268614577598981, 0.0590469534712963]
4 1 0.0116279069767 7.89165125336 java的 [0.084856465089942462, 0.044585600301495186, 0.042201343600880466, 0.091763386667030794]
5 1 0.0078125 7.64033682508 java语言 [0.063669473542364519, 0.063669473542364519, 0.056595087593212905, 0.04993684199401139, 0.059690131445966736]
2 1 0.00900900900901 8.73894911375 java运行环境 [0.3495579645500741, 0.078729271295061728]
2 2 0.0208333333333 9.14441422186 java.lang.nosuchmethoderror org.w3c.dom.element.settextcontent ljava lang string [0.19050862962208365]
3 3 0.1 8.73894911375 log buffer [0.87389491137518527]
4 1 0.04 7.89165125336 more about bookmark [0.328818802223527, 0.23914094707165601, 0.46421477960968516, 0.31566605013458593]
2 1 0.00934579439252 8.73894911375 net framework [0.081672421623849079, 0.081672421623849079]
2 2 0.0740740740741 9.14441422186 openoffice.org v2.40 [0.67736401643407518]
3 1 0.03125 8.22812348999 oracle support [0.28372839620640894, 0.25712885906205812, 0.25712885906205812]
2 2 0.0196078431373 9.14441422186 org.xml.sax.saxparseexception parser has reached entity expansion limit [0.17930223964431405]
4 1 0.010101010101 7.89165125336 os x [0.77138657718617432, 0.079713649023885336]
2 1 0.00990099009901 8.73894911375 php里 [0.081672421623849079, 0.08652424865100844]
2 2 0.015625 9.14441422186 processing processing [0.14288147221656275]
2 2 0.0434782608696 9.14441422186 project文档 [0.39758322703739196]
3 1 0.0333333333333 8.22812348999 put together [0.25712885906205812, 0.31646628807637922, 0.27427078299952867]
2 2 0.0137931034483 9.14441422186 s60操作系统的 [0.12612985133600021]
2 2 0.0196078431373 9.14441422186 set application [0.17930223964431405]
2 2 0.0625 9.14441422186 setting up couchdb lucene os x [0.571525888866251]
2 2 0.019801980198 9.14441422186 shell脚本 [0.18107750934376268]
2 2 0.0666666666667 9.14441422186 sinners cosiners [0.60962761479066774]
2 2 0.0208333333333 9.14441422186 sql plus [0.19050862962208365]
2 1 0.0175438596491 8.73894911375 sql select [0.087389491137518524, 0.15331489673248863]
2 1 0.00740740740741 8.73894911375 sql来 [0.087389491137518524, 0.064732956398161873]
2 1 0.00740740740741 8.73894911375 sql的 [0.063787949735414975, 0.064732956398161873]
3 3 0.0882352941176 8.73894911375 t2000 servers [0.77108374533104584]
2 2 0.0444444444444 9.14441422186 than lucene [0.4064184098604452]
2 2 0.0235294117647 9.14441422186 tom的 [0.21516268757317683]
2 2 0.0114942528736 9.14441422186 web应用系统的 [0.10510820944666685]
2 2 0.0130718954248 9.14441422186 web开发语言 [0.11953482642954269]
2 2 0.0114942528736 9.14441422186 web网站 [0.10510820944666685]
5 2 0.0168067226891 7.75811986074 webchart的 [0.064748617161726627, 0.12718229279901846, 0.13038856908806931]
3 2 0.016393442623 8.4512670413 webchart的技术结构 [0.069729860084625936, 0.13854536133278805]
2 1 0.00769230769231 8.73894911375 windows下的 [0.1078882606636031, 0.067222685490398865]
2 2 0.0169491525424 9.14441422186 x window [0.15499007155694941]
5 1 0.008 7.64033682508 xml文件 [0.12614829041853864, 0.074905262991017074, 0.070743859491516126, 0.061122694600669943]
2 1 0.0104166666667 8.73894911375 xml文档 [0.069911592910014822, 0.091030719934915127]
3 1 0.00980392156863 8.22812348999 xml的 [0.13741897628130198, 0.08066787735280255]
2 1 0.00980392156863 8.73894911375 xml的程序 [0.071048366778470345, 0.085675971703449524]
2 2 0.018691588785 9.14441422186 xslt安全 [0.17092363031514046]
10 1 0.00819672131148 6.89312242325 一下 [0.056041645717508311, 0.045053087733683148, 0.041776499534869824, 0.11236922018765368, 0.10292132806701922, 0.050314762213529346, 0.056501003469291163]
40 1 0.0175438596491 5.46811354995 一个 [0.056959516145343121, 0.13049648989834212, 0.080012446361027292, 0.13185014353359065, 0.04050454481446622, 0.20024829316849563, 0.043397726586928094, 0.053608956372087645, 0.10149726992093276, 0.084124823845429852, 0.056959516145343121, 0.16481267941698832, 0.067664846613955179, 0.030893296892389489, 0.063582715697127201, 0.032355701479011477, 0.072116481259610121, 0.031791357848563601, 0.068510657196629618, 0.035739304248058434, 0.044820602868466723, 0.092895806368311351, 0.089850042225088037, 0.044456207723194641, 0.095931816665841038]
3 2 0.0238095238095 8.4512670413 一个java [0.048687121242519879, 0.20122064384047786]
2 1 0.0104166666667 8.73894911375 一个xml文 [0.071048366778470345, 0.091030719934915127]
2 1 0.00909090909091 8.73894911375 一个工 [0.069356738998030576, 0.079444991943198651]
2 1 0.0116279069767 8.73894911375 一个很 [0.057117314468966354, 0.10161568736920758]
2 1 0.00625 8.73894911375 一个简单 [0.064732956398161873, 0.054618431960949079]
9 1 0.00534759358289 7.00434805836 一些 [0.064260073929942624, 0.060382310847963319, 0.084389735642936697, 0.041445846499193757, 0.057412689002981521, 0.040722953827696196, 0.045780052669044086, 0.040254873898642213, 0.037456406729217885]
4 1 0.0104166666667 7.89165125336 一切 [0.13200198112276781, 0.082204700555881749]
3 3 0.0160427807487 8.73894911375 一切都是对象 [0.14019704460564469]
2 1 0.00840336134454 8.73894911375 一定 [0.051709758069537586, 0.073436547174385317]
2 1 0.00740740740741 8.73894911375 一文 [0.19419886919448562, 0.064732956398161873]
3 3 0.0181818181818 8.73894911375 一本 [0.1588899838863973]
4 1 0.00581395348837 7.89165125336 一条 [0.04535431754807269, 0.065763760444705402, 0.065763760444705402, 0.045881693333515397]
3 1 0.00900900900901 8.22812348999 一样 [0.06744363516381853, 0.053084667677328126, 0.074127238648521263]
"""