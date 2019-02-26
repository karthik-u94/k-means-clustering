#!/usr/bin/env python
# coding: utf-8

# In[2]:


from html.parser import HTMLParser
from bs4 import BeautifulSoup
import string
import fileinput
import codecs
import re
import math
import csv
import glob, os
import sys

# In[13]:


class article:
    def __intit__(self, topic, newid, body, tokenlist,termFrequency,TermFreqSqrt,termFreqLog,Dimensions):
        self.topic=topic
        self.newid=newid
        self.body=body
        self.tokenlist=tokenlist
        self.termFrequency=termFrequency
        self.TermFreqSqrt=TermFreqSqrt
        self.termFreqLog=termFreqLog
        self.Dimensions=Dimensions
        


# In[20]:


filepath = str(sys.argv[1])
if('/' != filepath[len(filepath)-1] and 'sgm' not in filepath):
    filepath += '/'
if('sgm' not in filepath):
    filepath += '*.sgm'

allfiles = glob.glob(filepath)

FileList=["reut2-000.sgm","reut2-001.sgm","reut2-002.sgm","reut2-003.sgm","reut2-004.sgm","reut2-005.sgm","reut2-006.sgm","reut2-007.sgm","reut2-008.sgm","reut2-009.sgm","reut2-010.sgm","reut2-011.sgm","reut2-012.sgm","reut2-013.sgm","reut2-014.sgm","reut2-015.sgm","reut2-016.sgm","reut2-017.sgm","reut2-018.sgm","reut2-019.sgm","reut2-020.sgm","reut2-021.sgm"]

for f in allfiles:
    # print(f)
    with codecs.open(f, "r",encoding='utf-8', errors='ignore') as file:
#         file= open(f,"r")
        content=file.read()
        with open("aggr.sgm", "a") as myfile:
            myfile.write(content)
            


# In[21]:
# print("Written")

aggrFile=open("aggr.sgm", "r")
aggrContent=aggrFile.read()
soup=BeautifulSoup(aggrContent,"html.parser")
articles=soup.find_all("reuters")

SingleTopicArticles=[]
TopicsDictionary={}

nullcount=0
for article in articles:
    res=article.topics.findAll("d")
    
    if(len(res)==1):
        if(article.topics.string in TopicsDictionary):
            TopicsDictionary[article.topics.string]+=1
        else:
            TopicsDictionary[article.topics.string]=1
        p=article()
        p.topic=article.topics.string
        p.newid=article["newid"]
        p.body=article.body
        
        SingleTopicArticles.append(p)
    else:
        
        nullcount+=1

SingleTopicArticles=[st for st in SingleTopicArticles if st.body is not None]

TopicsDictionaryRev = dict((v,k) for k,v in TopicsDictionary.items())

Counts=list(TopicsDictionary.values())

Counts.sort(reverse=True)

Top20=Counts[:20]

Top20Topics={}
for freq in Top20:
    Top20Topics[TopicsDictionaryRev[freq]]=freq

FilteredArticles=[]


for art in SingleTopicArticles:
    if(art.topic in Top20Topics):
        FilteredArticles.append(art)

# print(len(FilteredArticles))
# print(nullcount)


# In[5]:


# print(Top20Topics)


# In[6]:


import sys

class PorterStemmer:

    def __init__(self):
        """The main part of the stemming algorithm starts here.
        b is a buffer holding a word to be stemmed. The letters are in b[k0],
        b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
        readjusted downwards as the stemming progresses. Zero termination is
        not in fact used in the algorithm.
tolencount
        Note that only lower case sequences are stemmed. Forcing to lower case
        should be done before stem(...) is called.
        """

        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0   # j is a general offset into the string

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        if self.b[i] == 'y':
            if i == self.k0:
                return 1
            else:
                return (not self.cons(i - 1))
        return 1

    def m(self):
        """m() measures the number of consonant sequences between k0 and j.
        if c is a consonant sequence and v a vowel sequence, and <..>
        indicates arbitrary presence,

           <c><v>       gives 0
           <c>vc<v>     gives 1
           <c>vcvc<v>   gives 2
           <c>vcvcvc<v> gives 3
           ....
        """
        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1

    def vowelinstem(self):
        """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def doublec(self, j):
        """doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
        if j < (self.k0 + 1):
            return 0
        if (self.b[j] != self.b[j-1]):
            return 0
        return self.cons(j)

    def cvc(self, i):
        """cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
        and also if the second c is not w,x or y. this is used when trying to
        restore an e at the end of a short  e.g.

           cav(e), lov(e), hop(e), crim(e), but
           snow, box, tray.
        """
        if i < (self.k0 + 2) or not self.cons(i) or self.cons(i-1) or not self.cons(i-2):
            return 0
        ch = self.b[i]
        if ch == 'w' or ch == 'x' or ch == 'y':
            return 0
        return 1

    def ends(self, s):
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
        length = len(s)
        self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        """step1ab() gets rid of plurals and -ed or -ing. e.g.

           caresses  ->  caress
           ponies    ->  poni
           ties      ->  ti
           caress    ->  caress
           cats      ->  cat

           feed      ->  feed
           agreed    ->  agree
           disabled  ->  disable

           matting   ->  mat
           mating    ->  mate
           meeting   ->  meet
           milling   ->  mill
           messing   ->  mess

           meetings  ->  meet
        """
        if self.b[self.k] == 's':
            if self.ends("sses"):
                self.k = self.k - 2
            elif self.ends("ies"):
                self.setto("i")
            elif self.b[self.k - 1] != 's':
                self.k = self.k - 1
        if self.ends("eed"):
            if self.m() > 0:
                self.k = self.k - 1
        elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
            self.k = self.j
            if self.ends("at"):   self.setto("ate")
            elif self.ends("bl"): self.setto("ble")
            elif self.ends("iz"): self.setto("ize")
            elif self.doublec(self.k):
                self.k = self.k - 1
                ch = self.b[self.k]
                if ch == 'l' or ch == 's' or ch == 'z':
                    self.k = self.k + 1
            elif (self.m() == 1 and self.cvc(self.k)):
                self.setto("e")

    def step1c(self):
        """step1c() turns terminal y to i when there is another vowel in the stem."""
        if (self.ends("y") and self.vowelinstem()):
            self.b = self.b[:self.k] + 'i' + self.b[self.k+1:]

    def step2(self):
        """step2() maps double suffices to single ones.
        so -ization ( = -ize plus -ation) maps to -ize etc. note that the
        string before the suffix must give m() > 0.
        """
        if self.b[self.k - 1] == 'a':
            if self.ends("ational"):   self.r("ate")
            elif self.ends("tional"):  self.r("tion")
        elif self.b[self.k - 1] == 'c':
            if self.ends("enci"):      self.r("ence")
            elif self.ends("anci"):    self.r("ance")
        elif self.b[self.k - 1] == 'e':
            if self.ends("izer"):      self.r("ize")
        elif self.b[self.k - 1] == 'l':
            if self.ends("bli"):       self.r("ble") # --DEPARTURE--
            # To match the published algorithm, replace this phrase with
            #   if self.ends("abli"):      self.r("able")
            elif self.ends("alli"):    self.r("al")
            elif self.ends("entli"):   self.r("ent")
            elif self.ends("eli"):     self.r("e")
            elif self.ends("ousli"):   self.r("ous")
        elif self.b[self.k - 1] == 'o':
            if self.ends("ization"):   self.r("ize")
            elif self.ends("ation"):   self.r("ate")
            elif self.ends("ator"):    self.r("ate")
        elif self.b[self.k - 1] == 's':
            if self.ends("alism"):     self.r("al")
            elif self.ends("iveness"): self.r("ive")
            elif self.ends("fulness"): self.r("ful")
            elif self.ends("ousness"): self.r("ous")
        elif self.b[self.k - 1] == 't':
            if self.ends("aliti"):     self.r("al")
            elif self.ends("iviti"):   self.r("ive")
            elif self.ends("biliti"):  self.r("ble")
        elif self.b[self.k - 1] == 'g': # --DEPARTURE--
            if self.ends("logi"):      self.r("log")
        # To match the published algorithm, delete this phrase

    def step3(self):
        """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
        if self.b[self.k] == 'e':
            if self.ends("icate"):     self.r("ic")
            elif self.ends("ative"):   self.r("")
            elif self.ends("alize"):   self.r("al")
        elif self.b[self.k] == 'i':
            if self.ends("iciti"):     self.r("ic")
        elif self.b[self.k] == 'l':
            if self.ends("ical"):      self.r("ic")
            elif self.ends("ful"):     self.r("")
        elif self.b[self.k] == 's':
            if self.ends("ness"):      self.r("")

    def step4(self):
        """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
        if self.b[self.k - 1] == 'a':
            if self.ends("al"): pass
            else: return
        elif self.b[self.k - 1] == 'c':
            if self.ends("ance"): pass
            elif self.ends("ence"): pass
            else: return
        elif self.b[self.k - 1] == 'e':
            if self.ends("er"): pass
            else: return
        elif self.b[self.k - 1] == 'i':
            if self.ends("ic"): pass
            else: return
        elif self.b[self.k - 1] == 'l':
            if self.ends("able"): pass
            elif self.ends("ible"): pass
            else: return
        elif self.b[self.k - 1] == 'n':
            if self.ends("ant"): pass
            elif self.ends("ement"): pass
            elif self.ends("ment"): pass
            elif self.ends("ent"): pass
            else: return
        elif self.b[self.k - 1] == 'o':
            if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'): pass
            elif self.ends("ou"): pass
            # takes care of -ous
            else: return
        elif self.b[self.k - 1] == 's':
            if self.ends("ism"): pass
            else: return
        elif self.b[self.k - 1] == 't':
            if self.ends("ate"): pass
            elif self.ends("iti"): pass
            else: return
        elif self.b[self.k - 1] == 'u':
            if self.ends("ous"): pass
            else: return
        elif self.b[self.k - 1] == 'v':
            if self.ends("ive"): pass
            else: return
        elif self.b[self.k - 1] == 'z':
            if self.ends("ize"): pass
            else: return
        else:
            return
        if self.m() > 1:
            self.k = self.j

    def step5(self):
        """step5() removes a final -e if m() > 1, and changes -ll to -l if
        m() > 1.
        """
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self.m()
            if a > 1 or (a == 1 and not self.cvc(self.k-1)):
                self.k = self.k - 1
        if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
            self.k = self.k -1

    def stem(self, p, i, j):
        """In stem(p,i,j), p is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases word length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b # --DEPARTURE--

        # With this line, strings of length 1 or 2 don't go through the
        # stemming process, although no mention is made of this in the
        # published algorithm. Remove the line to match the published
        # algorithm.

        self.step1ab()
        self.step1c()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        return self.b[self.k0:self.k+1]



# In[7]:



#remove all non-ascii characters
ProcessedArticles=[]
stopfile=open("stoplist.txt","r")
stoplist=stopfile.read()
# stoplist=stoplist.replace("\n","").split(" ")
stoplist=stoplist.split()
DocumentFrequency={}
p=PorterStemmer()

for article in FilteredArticles:
    #remove non-asci
    article.body=article.body.string
    article.body=re.sub(r'[^\x00-\x7f]',r'', article.body)
    #replace html 
    article.body=article.body.replace("&lt", "<")
    article.body=article.body.replace("&gt", ">")
    article.body=article.body.replace("&apos", "'")
    article.body=article.body.replace("&amp", "&")
    article.body=article.body.replace("&quot", "\"")
    #lowercase
    article.body=article.body.lower()
    #keep only alphanumeric
    article.body = re.sub('[^0-9a-zA-Z]+', ' ', article.body)
    #tokenize
    article.tokenlist=article.body.split(" ")


# In[8]:


for article in FilteredArticles:
    article.tokenlist=[token for token in article.tokenlist if not token=='']
    # print(len(article.tokenlist))

for article in FilteredArticles:
    article.tokenlist=[token for token in article.tokenlist if not token.isdigit()]

for article in FilteredArticles:
    #print(len(article.tokenlist))
    article.tokenlist=[token for token in article.tokenlist if token not in stoplist]
    #print(len(article.tokenlist))

for article in FilteredArticles:
    temp=[]
    for tk in article.tokenlist:
        tk=p.stem(tk, 0,len(tk)-1)
        temp.append(tk)
    article.tokenlist=temp
    for term in article.tokenlist:
        if(term not in DocumentFrequency):
            DocumentFrequency[term]=1
        else:
            DocumentFrequency[term]+=1
    #Document freq
#     UniqueTokens=list(set(article.tokenlist))
#     print(UniqueTokens)
#     print("\n\n")
#     for utk in UniqueTokens:
#         if(utk not in DocumentFrequency):
#             DocumentFrequency[utk]=1
#         else:
#             DocumentFrequency[utk]+=1

tokencount=0            
for article in FilteredArticles:
    article.tokenlist=[token for token in article.tokenlist if DocumentFrequency[token]>=5 and len(token.strip())>0]
    tokencount+=len(article.tokenlist)


# In[9]:


# print(len(DocumentFrequency))
DocumentFrequency={key: DocumentFrequency[key] for key in DocumentFrequency if DocumentFrequency[key] >= 5}
# print(len(DocumentFrequency))


# In[10]:


# print(len(DocumentFrequency))
for art in FilteredArticles:
    freq=[]
    indices=[]
    freqlog=[]
    freqSqrt=[]
    Dimensions=list(DocumentFrequency.keys())
    for index,term in enumerate(Dimensions):
        count=art.tokenlist.count(term)
        if(count!=0):
            freq.append(count)
            indices.append(index)
            freqlog.append(1+math.log(art.tokenlist.count(term),2))
            freqSqrt.append(1+math.sqrt(art.tokenlist.count(term)))
    art.Dimensions=indices  
    art.termFrequency=[fr/math.sqrt(sum(map(lambda x:x*x,freq))) for fr in freq]
    
    art.termFreqLog=[fr/math.sqrt(sum(map(lambda x:x*x,freqlog))) for fr in freqlog]
    art.TermFreqSqrt=[fr/math.sqrt(sum(map(lambda x:x*x,freqSqrt))) for fr in freqSqrt]
#     print(art.termFrequency)
#     print("\n\n")

# print("Done!!!!")


# In[11]:


with open('freq.csv', 'w') as csvfile:
    f1 = csv.writer(csvfile, delimiter=',')
    for art in FilteredArticles:
#         print(art.termFrequency)
        index=0
        for val in art.termFrequency:
            if(val!=0):
#                 print([art.newid,art.Dimensions[index],val ])
                f1.writerow([art.newid,art.Dimensions[index],round(val,2) ])
                index+=1
with open('log2freq.csv', 'w') as csvfile:
    f2 = csv.writer(csvfile, delimiter=',')
    for art in FilteredArticles:
#         print(art.termFrequency)
        index=0
        for val in art.termFreqLog:
            if(val!=0):
#                 print([art.newid,art.Dimensions[index],val ])
                f2.writerow([art.newid,art.Dimensions[index],round(val,2) ])
                index+=1
                
with open('sqrtfreq.csv', 'w') as csvfile:
    f3 = csv.writer(csvfile, delimiter=',')
    for art in FilteredArticles:
#         print(art.termFrequency)
        index=0
        for val in art.TermFreqSqrt:
            if(val!=0):
#                 print([art.newid,art.Dimensions[index],val ])
                f3.writerow([art.newid,art.Dimensions[index],round(val,2) ])
                index+=1


# In[12]:


with open('reuters21578.class', 'w') as csvfile:
    f4 = csv.writer(csvfile, delimiter=',')
    for art in FilteredArticles:
        f4.writerow([art.newid,art.topic ])


# In[13]:


print(len(DocumentFrequency))
with open('reuters21578.clabel', 'w') as csvfile:
    f4 = csv.writer(csvfile, delimiter=',')
    i=0
    for key,value in DocumentFrequency.items():
        f4.writerow([key])
        i+=1


# In[ ]:




