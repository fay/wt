# -*- coding:utf-8 -*-
import sys
from itertools import izip

class SuffixComparator(object):
    __slots__ = 'text length'.split(' ')
    
    def __init__(self, text):
        self.text = text
        self.length = len(text)

    def __call__(self, a, b):
        for i, j in izip(xrange(a, self.length), xrange(b, self.length)):
            c = cmp(self.text[i], self.text[j])
            if c: return c
        return cmp(j, i)

def build_suffix_array(text, indices=None):
    if indices is None:
        indices = range(len(text))

    indices.sort(SuffixComparator(text))
    return indices

def read_file(filename):
    fp = file(filename)
    try:
        return fp.read()
    finally:
        fp.close()

def suffix(text, index, max_length):
    last = text.find('\n', index, index + max_length)
    if last != - 1:
        return text[index:last]
    else:
        return text[index:index + max_length]
    
def calculateLcp(array, suffixorder):
    lcp_array = [0]
    for i in range(len(array) - 1):
        lcp = 0
        if i == 15:
            pass
        while cmp(array[suffixorder[i]:suffixorder[i] + lcp + 1], array[suffixorder[i + 1]:suffixorder[i + 1] + lcp + 1]) == 0:
          m = array[suffixorder[i]:suffixorder[i] + lcp + 1]
          n = array[suffixorder[i + 1]:suffixorder[i + 1] + lcp + 1]
          lcp += 1
          #if len(array) - i == lcp - 1:
             #break
        lcp_array.append(lcp)
    lcp_array.append(0)
    return  lcp_array

def most_long_match(a, b, array, i=1):
    while cmp(array[a:a + i], array[b:b + i]) == 0:
        i += 1  
        if len(array) - a == i:
            break
    return cmp(array[a:a + i], array[b:b + i])

def main(args, options):
    if args:
        text = ''.join(read_file(f) for f in args)
    else:
        text = sys.stdin.read()

    if options.encoding:
        text = text.decode(options.encoding)

    suffix_array = build_suffix_array(text)
    for i in suffix_array:
        sys.stdout.write('%d\t%s\n' % (i, suffix(text, i, 10).encode('utf-8')))

if __name__ == '__main__':
    #from optparse import OptionParser
    
    #parser = OptionParser()
    #parser.add_option('-e', '--encoding', dest='encoding',
    #                  help='input encoding', metavar='encoding')
    #(options, args) = parser.parse_args()

    #main(args, options)
    text = "to be or not to be 解放中国人"
    print text
    
    sd = build_suffix_array(text)
    print sd
    lcp = calculateLcp(text, sd)
    print lcp
    b = 1
    for i in sd:
        sys.stdout.write('%d\t%d\t%s\n' % (i, lcp[b], text[i:]))
        b += 1
        
