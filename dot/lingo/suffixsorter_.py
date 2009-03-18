# -*- coding: utf-8 -*-
import math
class SuffixSorter(object):
    def __init__(self):
        self.input = None
    def sort(self, input):
        int_codes = []
        for token in input:
            int_codes.append(ord(token))
        print int_codes
        maxcode = max(int_codes)
        mincode = min(int_codes)
        offset  = mincode
        forward = range(maxcode - mincode + 1)
        m = {}
        i = 1
        for code in int_codes:
            m[code] = i

        for k,v in m.items():
            m[k] = i
            i += 1
        for i in range(len(int_codes)):
            int_codes[i] = m[int_codes[i]]
        int_codes.append(-999999)
        int_codes.append(0)
        int_codes.append(0)
        self.input = int_codes
        print int_codes
        #for i in range(len(forward)):
           # if forward[i] == 1:
                
        orders = range(len(int_codes) - 3)
        #self.qsort(0, len(int_codes) - 1, orders)
        self.insertionSort(0, len(int_codes) - 4, orders)
        return orders
    #可选快速排序算法:    
    #lambda s:s if len(s)<2 else q([x for x in s[1:]if x<s[0]])+[s[0]]+q([x for x in s[1:]if x>=s[0]])    
    def qsort(self, left, right, orders):
        if right - left + 1 > 2:
            p = (left + right) / 2
            if self.compare(self.input[orders[left]], self.input[orders[p]]):
                self.swap(p, right, orders)
            if self.compare(self.input[orders[left]], self.input[orders[right]]):
                self.swap(left, right, orders)
            if self.compare(self.input[orders[p]], self.input[orders[right]]):
                self.swap(p, right, orders)

            j = right - 1
            self.swap(p, j, orders)
            i = left
            pivot = self.input[orders[j]]
            while True:
                while i < len(orders) - 1 and self.compare(self.input[orders[i + 1]], pivot) < 0:
                    i += 1
                while j > 1 and self.compare(self.input[orders[j - 1]], pivot) > 0:
                    j -= 1
                if i > j:
                    break
                self.swap(i, j, orders)
            self.swap(i, right - 1, orders)
            self.qsort(left, j, orders)
            self.qsort(i + 1, right, orders)
            
    def insertionSort(self,lo0, hi0, orders):
        for i in range(lo0 + 1,hi0 + 1):
            v = orders[i];
            j = i
            while j > lo0 and self.icompare(orders[j - 1], v) > 0:
                orders[j] = orders[j - 1]
                j -= 1
            orders[j] = v
    def compare(self, a, b):
        return a - b
    def icompare(self, suffixA, suffixB):
        if suffixA == suffixB: return 0

        while self.input[suffixA] == self.input[suffixB]:
            suffixA += 1 
            suffixB += 1        

        if self.input[suffixA] < self.input[suffixB]: return - 1
        if self.input[suffixA] > self.input[suffixB]: return 1

    def swap(self, a, b, orders):
        if self.input[a] != self.input[b]:
            tmp = orders[b]
            orders[b] = orders[a]
            orders[a] = tmp
    
    def build_suffix_array(self,input):
        int_codes = ''
        for token in input:
            int_codes = int_codes + str(ord(token)) +'\\'
        print int_codes
        return pysarray.build_sarray_and_lcp(int_codes)
        
    
if __name__ == '__main__':
    sorter = SuffixSorter()
    b = u'解放'
    a = sorter.sort(b)
    print a
    for i in a:
        print b[i:]
    #