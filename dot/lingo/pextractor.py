# -*- coding:utf-8 -*-
MAX_PHRASE_LEN = 2
class PhraseExtractor(object):
    def __init__(self):
        pass
    
    def extract(self, suffixdata):
        pass
    # get right complete substring    
    def rcs(self, lcp):
        class Substring(object):
            def __init__(self, id=None, freq=None):
                self.id = id
                self.freq = freq
        N = len(lcp)
        result = []
        stack = range(N - 1)        
        sp = - 1
        i = 1
        while i < N:
            if sp < 0:
                if lcp[i] >= MAX_PHRASE_LEN:
                    sp += 1
                    stack[sp] = Substring(id=i, freq=2)
                i += 1
            else:
                r = stack[sp].id 
                #如果小于则表明有新的子串出现
                if lcp[r] < lcp[i]:
                    sp += 1
                    stack[sp] = Substring(id=i, freq=2)
                    i += 1
                elif lcp[r] == lcp[i]:
                #如果相等，则必然是同substring，因为现在是按字母顺序的有序排列
                    stack[sp].freq += 1
                    i += 1
                else:
                    #如果大于，当前堆栈中的substring已经是最后一个，可以输出到结果中
                    result.append(stack[sp])
                    f = stack[sp].freq
                    sp -= 1
                    if sp >= 0:
                        stack[sp].freq = stack[sp].freq + f - 1
                    if lcp[i] >= MAX_PHRASE_LEN  and sp < 0:
                        sp += 1
                        stack[sp] = Substring(id=i, freq=2 + f - 1)
                        i += 1
                    
       
        return result
if __name__ == '__main__':
    from dot.lingo import suffixsorter as ss
    import sys
    #text = "to_be_or_not_to_be"
    text = "a b c d . a b c d"
    suffix = ss.build_suffix_array(text)
    print suffix
    lcp = ss.calculateLcp(text, suffix)
    print lcp
    b = 1
    for i in suffix:
        sys.stdout.write('%d\t%d\t%s\n' % (i, lcp[b], ss.suffix(text, i, 10).encode('utf-8')))
        b += 1
    pe = PhraseExtractor()
    stack = pe.rcs(lcp)
    for item in stack:
        print item.id, item.freq, '|' + text[suffix[item.id]:suffix[item.id] + lcp[item.id]] + '|'