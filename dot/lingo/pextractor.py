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
        results = self.intersect_lcs_rcs(rcs, lcs, rcs_ordered, lcs_ordered)
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
    def intersect_lcs_rcs(self, rcs, lcs, ordered_rcs, ordered_lcs):
        i = 0
        j = 0
        results = []
        while i < len(ordered_lcs) and j < len(ordered_rcs):
            # 由于ordered_lcs等是一个list，在python中是不能作为key的（list对象是可变的）
            # 所以这里先把单词list转换为字符串
            l = self.list2str(ordered_lcs[i])
            r = self.list2str(ordered_rcs[j])
            if l == r:
                # Q: Why choose rcs as results returned?
                # A: rcs is sorted already while lcs is not
                rcs[j].text = l
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
    text = re.sub('[0-9，。,.：:;;\n]'.decode('utf-8'), '', """提起电吉他演奏，就必须提到布鲁斯音乐；提起最伟大的吉他演奏大师，人们首先会想到的是 Jimi Hendrix，但是说起依然在世的最伟大的吉他演奏家，名字只有一个——Eric Clapton爵士。自从上个世纪60年代布鲁斯摇滚乐以及布鲁斯吉他演奏成为了主流摇滚风格之后，在这种来源于黑人音乐的吉他演奏中，在所有除黑色外其他肤色的布鲁斯吉他演奏家之中，传奇人物Eric Clapton毫无疑问是其中最杰出的一位。在与Eric Clapton同时代的所有艺术家纷纷的离开人世，或者失去了原有的歌迷号召力之后，Eric Clapton是所有当年这些艺术家中为数不多的既然保持着自己高超的演奏技术以及强大的市场号召力的艺术家。
　　
Eric Clapton为人谦逊，在与其他出色的吉他演奏者比如Jimi Hendrix，B.B. King，Duane Allman，甚至后辈Stevie Ray Vaughan相比较的时候他总是非常谦恭，在与B.B. King以及Bob Dylan等人同台的时候他总是举止非常礼让，他是最有绅士风度的流行音乐家之一。同时，作为世界上最著名的吉他大师，Eric Clapton还经常热心的帮助包括英国著名流行音乐家Sting，Bon Jovi乐队主音吉他手Richie Sambora在内的其他一些音乐家去录制专辑或者拍摄音乐录影带，并且经常为一些音乐家担任吉他手作伴奏。Eric Clapton曾经协助过Bob Dylan，Aretha Franklin，Joe Cocker，Ringo Starr，Freddie King，Roger Waters等等近百位艺术家的专辑录制。 　　
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
