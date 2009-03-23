# -*- coding:utf-8 -*-
from dot.lingo import suffixsorter
import re
# 最小短语长度
MIN_PHRASE_LEN = 2
MAX_PHRASE_LEN = 20
class Substring(object):
    def __init__(self, id=None, freq=None):
        #id means position
        self.id = id
        self.freq = freq
        self.text = None
        self.doc_freq = {}

    def __cmp__(self,other):
        return cmp(self.id,other.id)
class PhraseExtractor(object):
    def __init__(self):
        pass
    def extract(self, context):
        # 这个text可能就是一个字符串，但也可能是一个单词(中文、英文混杂)的list
        text = context.tokens
        text_inversed = text[:: - 1]
        suffix = suffixsorter.build_suffix_array(text)
        context.suffix = suffix
        # 得到text逆序后的suffix array
        suffix_inversed = suffixsorter.build_suffix_array(text_inversed)
        lcp = suffixsorter.calculateLcp(text, suffix)
        context.lcp = lcp
        lcp_inversed = suffixsorter.calculateLcp(text_inversed, suffix_inversed)
        # 得到right complete substring
        rcs = self.rcs(lcp)
        # sort rcs by id
        # (it works because suffix array is already sorted 
        # and the rcs list just have changed a little due to the stack's effect in intersect_lcs_rcs)
        rcs.sort()
        #for i in rcs:
            #print i.id,context.tokens[context.suffix[i.id]:context.suffix[i.id]+context.lcp[i.id]],self.list2str(context.tokens[context.suffix[i.id]:context.suffix[i.id]+context.lcp[i.id]]),i.freq
        # 得到left complete substring
        lcs = self.rcs(lcp_inversed)
        rcs_ordered = []
        lcs_ordered = []
        for item in rcs:
            rcs_ordered.append(text[suffix[item.id]:suffix[item.id] + lcp[item.id]])
        for item in lcs:
            lcs_ordered.append(text_inversed[suffix_inversed[item.id]:suffix_inversed[item.id] + lcp_inversed[item.id]][:: - 1])
        #rcs needn't sort now
        #rcs_ordered.sort()
        lcs_ordered.sort()
        results = self.intersect_lcs_rcs(rcs, lcs, rcs_ordered, lcs_ordered,context)
        return results
        
    # get right complete substring    
    def rcs(self, lcp):
        
        N = len(lcp)
        result = []
        stack = range(N - 1)        
        sp = - 1
        i = 1
        while i < N:
            if sp < 0:
                if lcp[i] >= MIN_PHRASE_LEN and lcp[i] <= MAX_PHRASE_LEN:
                    sp += 1
                    stack[sp] = Substring(id=i, freq=2)
                i += 1
            else:
                r = stack[sp].id 
                # 如果小于则表明有新的子串出现
                if lcp[r] < lcp[i]:
                    sp += 1
                    stack[sp] = Substring(id=i, freq=2)
                    i += 1
                elif lcp[r] == lcp[i]:
                # 如果相等，则必然是同substring，因为现在是按字母顺序的有序排列
                    stack[sp].freq += 1
                    i += 1
                else:
                # 如果大于，当前堆栈中的substring已经是最后一个，可以输出到结果中
                    result.append(stack[sp])
                    f = stack[sp].freq
                    sp -= 1
                    if sp >= 0:
                        stack[sp].freq = stack[sp].freq + f - 1
                    if lcp[i] >= MIN_PHRASE_LEN and lcp[i] <= MAX_PHRASE_LEN and sp < 0:
                        sp += 1
                        stack[sp] = Substring(id=i, freq=2 + f - 1)
                        i += 1
                    
       
        return result
    #将list中的字符连接成一个字符串
    def list2str(self, lst):
        #如果本来就是字符串直接返回
        if type(lst) == str or type(lst) == unicode:
            return lst
        s = ''
        is_alpha = False
        for k in lst:
            if type(k) != str and type(k) != unicode:
                k = k.text 
            tt = re.search('[0-9a-zA-Z]', k)
            # 如果当前term与前面的term都为英文，则之间加个空格
            if is_alpha and tt:
                s += " "
            is_alpha = tt
            s += k
        return s
    def intersect_lcs_rcs(self, rcs, lcs, ordered_rcs, ordered_lcs,context):
        i = 0
        j = 0
        results = []

        tdr = context.term_doc_range
        while i < len(ordered_lcs) and j < len(ordered_rcs):
            # 由于ordered_lcs等是一个list，在python中是不能作为key的（list对象是可变的）
            # 所以这里先把单词list转换为字符串
            l = self.list2str(ordered_lcs[i])
            r = self.list2str(ordered_rcs[j])
            # 找到lcs,rcs的交集
            if l == r:
                rcs[j].text = l
                # 求出complete substring 在每个文档里的出现freq
                id = rcs[j].id - 1
                lcp = context.lcp[id + 1]
                for m in range(rcs[j].freq):
                    begin = context.suffix[id]  
                    end = context.suffix[id] + lcp
                    for n in range(len(tdr)):
                        if begin < tdr[n]:
                            break
                    doc_id = n
                    rcs[j].doc_freq[doc_id] = rcs[j].doc_freq.get(doc_id,0) + 1
                    id += 1
                # Q: Why choose rcs's substring as results returned?
                # A: rcs is sorted already while lcs is not    
                results.append(rcs[j])
                i += 1
                j += 1
            elif l < r:
                i += 1
            else:
                j += 1
        return results

if __name__ == '__main__':
    from dot.lingo import suffixsorter as ss
    import sys, re
    text = re.sub('[0-9，。,.：:;;\n]'.decode('utf-8'), '', """Just because theres room on the dialog box, doesnt mean you have to put something there. The Java installer starts off with a dialog box that manages to repeat the word Java six times without really“By installing Java, you will be able to experience the power of Java Java运行环境下载，
    
         bookmark this on del.icio.us
        -
        posted 
        by chedong
        to
            java
            - more about this bookmark...下载免费的 Java 软件 - Sun Microsystems作者:d.c.b.a, 订阅AnySQL, Oracle数据库恢复,  DBA工具, WebChart报表等某一天, 在oramon的监控日志中, 突然看到数据库的事务数和日志生成量出现下跌的情况, 持续时间长达30秒, 这个原因得好好查查. 在oramon的Active SQL日志中发现了大量的锁等待, 被等待的语句发生在两个相对比较忙的表中. www.AnySQL.net C该死的Java Full GC安装IBM JDK

对于jdk有很多种选择，可以通过emerge -s jdk列出，我的环境以IBM产品为主，因此选择安装ibm jdk，其已经包含在Gentoo官方ebuild中，可以直接emerge，但jdk安装文件因为license 问题没有放入Gentoo mirror，需要自己下载，手工放入Portage，再继续emerge。


ibm jdk 目前最新版本是1.5（也称为 5.0)Gentoo Linux on T43 (12) Java 环境在Java的不同版本中：字体的平滑设置有不同的方法，Java 6 中已经可以自动适应系统设置。应用中有些也有字体平滑的设置： Freemind中可以通过设置 antialiasAll=true antialias=antialias_all 实现编辑的内
    
         bookmark this on del.icio.us
        -
        posted 
   Java应用的字体平滑设置： anti-aliasing : Java GlossaryA collection of Concurrent and Highly Scalable Utilities. These are intended as direct replacements for the java.util.* or java.util.concurrent.* collections but with better performance when many CPUsSourceForge.net: Highly Scalable Java  充分利用多CPU并发计算的JAVA基础类库IBM的JVM下载
    
         bookmark this on del.icio.us
        -
        posted 
        by chedong
        to
            jvm
            java
            ibm
            - more about this bookmark...
developerWorks : Java™ technology : IBM developer kits : Linux : Download information　　手机上的Java即J2ME（Java 2 Micro Edition）是Sun公司专门用于嵌入式设备的Java软件，开发的软件和游戏可以实现跨平台使用，具有良好的兼容性。当今Java游戏已经有了非常华丽的画面表现，可玩性也很不错，可以在不同品牌的手机上运行。　　这里，我总结了我玩过的十个个人感觉最好的Java手机游戏，分辨率为240x320的，可以在各个主流的240x320分辨率的手机上运行，十大经典Java手机游戏Windows下的 ClearType 能使字体看上去更平滑，但似乎对于 java 小程序里面的文字没有作用。不过可以用 Java 2D API 提供的文本处理功能进行美化。Java 2D API 的文本功能包括：
  
    使用抗锯齿处理和微调（hinting）以达到更好的输出质量 
    可以使用系统安装的所有字体 
    可以将对图形对象的操作（旋转、缩放、着色、剪切等等）应用到文本[存] java.awt.Graphics2D抗锯齿处理As community driven projects these languages do not have a specification nor is their development hindered by corporate bureaucracy. On the contrary, these languages are being developed by their usersPHP创始人之一Andi Gutmans: Java已经输掉Web之战.  Andi on Web &amp; IT: Java is losing the battle for the modern Web. Can the JVM save the vendors?
>>> 
""".decode('utf-8'))
    print text
    
    #text = re.sub(' ','',"a b c d . a b c d")
    text2 = text[:: - 1]
    suffix = ss.build_suffix_array(text)
    suffix2 = ss.build_suffix_array(text2)
    print suffix
    lcp = ss.calculateLcp(text, suffix)
    lcp2 = ss.calculateLcp(text2, suffix2)
    print lcp
    b = 1
    for i in suffix:
        sys.stdout.write('%d\t%d\t%s\n' % (i, lcp[b], ss.suffix(text, i, 10).encode('utf-8')))
        b += 1
    pe = PhraseExtractor()
    stack = pe.rcs(lcp)
    stack2 = pe.rcs(lcp2)
    stack.sort()
    ordered_stack = []
    for item in stack:
        ordered_stack.append(text[suffix[item.id]:suffix[item.id] + lcp[item.id]])
        print item.id, item.freq, '|' + text[suffix[item.id]:suffix[item.id] + lcp[item.id]] + '|'
    print '-----------------------'
    ordered_stack2 = []
    for item in stack2:
        ordered_stack2.append(text2[suffix2[item.id]:suffix2[item.id] + lcp2[item.id]][:: - 1])
        print item.id, item.freq, '|' + text2[suffix2[item.id]:suffix2[item.id] + lcp2[item.id]] + '|'
    q = lambda s:s if len(s) < 2 else q([x for x in s[1:]if x < s[0]]) + [s[0]] + q([x for x in s[1:]if x >= s[0]])
    ordered_stack2 = q(ordered_stack2)
    ordered_stack = q(ordered_stack)
    print ordered_stack2
    print ordered_stack
    print "complete substring-----------------"
    from dot.context import Context
    context = Context()
    context.tokens = text
    results = pe.extract(context)#pe.intersect_lcs_rcs(stack,stack2,ordered_stack,ordered_stack2)
    for i in results:
        if len(i.text) > 4 and i.freq > 1:
            print i.text,i.freq
