# -*- coding: utf-8 -*-
import re

def segWords(dict, sentence):
    sentence = re.sub(u"[。，,！……!《》<>\"':：？\?、\|“”‘’；,.\(\)]", " ", sentence)
    length = len(sentence)
    i = length
    result = []
    while True:
        if i <= 0:break
        found = - 1
        tempi = i
        tok = sentence[i - 1:i]
        while re.search("[0-9A-Za-z\-\+#@_\.]{1}", tok) <> None:
            i -= 1
            tok = sentence[i - 1:i]
        if tempi - i > 0:
            result.append(sentence[i:tempi].lower().encode('utf-8'))  
        for j in xrange(4, 0, - 1):
            if i - j < 0:continue
            utf8Word = sentence[i - j:i].encode('utf-8')
            d = dict
            w = utf8Word.decode('utf-8')
            count = 0    
            for ch in w:
                if(d.has_key(CChar(ch))):
                    count = count + 1
                    d = d[CChar(ch)]
                else:
                    break

            if count == len(w) and d.has_key(None):
                found = i - j
                result.append(utf8Word)
                break

        if found == - 1:
            if i < length and sentence[i].strip() == "":
                result.append(sentence[i - 1].encode('utf-8'))
            elif(sentence[i - 1:i].strip() != ""):
                if len(result) > 0 and len(result[ - 1]) < 12:
                    result.append(sentence[i - 1:i].encode('utf-8') + result[ - 1])
                else:
                    result.append(sentence[i - 1:i].encode('utf-8'))
            i -= 1
        else:
            i = found
    goodR = []
    for w in result:
        if w.strip() <> "":
            goodR.append(w)
    return goodR
  
def segWords2(dict, sentence):
    try:
        sentence = sentence.decode('utf-8')
    except:
        return []

    length = len(sentence)
    i = length
    result = []
    while True:
        if i <= 0:break
        found = - 1
        tempi = i
        tok = sentence[i - 1:i]
        while re.search("[0-9A-Za-z\-\+#@_\.]{1}", tok) <> None:
            i -= 1
            tok = sentence[i - 1:i]
        if tempi - i > 0:
            result.append(sentence[i:tempi].lower().encode('utf-8'))
        for j in xrange(4, 0, - 1):
            if i - j < 0:continue
            utf8Word = sentence[i - j:i].encode('utf-8')
            if(dict.has_key(utf8Word)):
                print utf8Word
                found = i - j
                result.append(utf8Word)
                break

        if found == - 1:
            result.append(sentence[i - 1:i].encode('utf-8'))
            i -= 1
        else:
            i = found
    goodR = []
    for w in result:
        if w.strip() <> "":
            goodR.append(w)
    return goodR

def segWords3(dict, sentence):
        try:
            sentence = sentence.decode('utf-8')
        except:
            print 'utf-8 problem'
            return []
        sentence = re.sub(u"[。，,！……!《》<>\"':：？\?、\|“”‘’；]", " ", sentence)
        length = len(sentence)
        i = length
        result = []
        while True:
            if i <= 0:break
            found = - 1
            tempi = i
            tok = sentence[i - 1:i]
            while re.search("[0-9A-Za-z\-\+#@_\.]{1}", tok) <> None:
                i -= 1
                tok = sentence[i - 1:i]
            if tempi - i > 0:
                result.append(sentence[i:tempi].lower().encode('utf-8'))
                
            for j in xrange(4, 0, - 1):
                if i - j < 0:continue
                utf8Word = sentence[i - j:i].encode('utf-8')
                if(dict.has_key(utf8Word)):
                    found = i - j
                    result.append(utf8Word)
                    break

            if found == - 1:
                if i < length and sentence[i].strip() == "":
                    result.append(sentence[i - 1].encode('utf-8'))
                elif(sentence[i - 1:i].strip() != ""):
                    if len(result) > 0 and len(result[ - 1]) < 12:
                        result.append(sentence[i - 1:i].encode('utf-8') + result[ - 1])
                    else:
                        result.append(sentence[i - 1:i].encode('utf-8'))
                i -= 1
            else:
                i = found
        goodR = []
        for w in result:
            if w.strip() <> "":
                goodR.append(w)
        return goodR