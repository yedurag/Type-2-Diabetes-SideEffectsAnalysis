from pattern.vector import Model, Document, NB, MULTINOMIAL, IG, MAJORITY,kfoldcv
from pattern.db import csv
from pattern.en import ngrams
from pattern.vector import stem, PORTER, LEMMA
from nltk.corpus import stopwords
from pattern.en import parsetree
import re
import csv as csv1
import collections
import numpy as np
import lda




#List of nltk stopwords
stop = [u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now']

medlist1 = ["diabetes","actos", "pioglitazone hydrochloride", "pioglitazone",  "glustin", "glizone", "pioz", "zactos"]

medlist2 = ["medformin","glucophage", "metformin", "glucophage xr", "metformin hydrochloride", "carbophage sr", "riomet", "fortamet", "glumetza", "obimet", "gluformin", "dianben", "diabex", "diaformin", "siofor","metfogamma", "riomet"]

medlist3 = ["byetta", "bydureon", "exenatide"]

medlist4 = ["victoza", "liraglutide", "saxenda"]

medlist5 = ["invokana", "canagliflozin"]

medlist6 = ["avandia", "rosiglitazone"]

medlist7 = ["insulin glargine",  "lantus", "toujeo", "abasaglar", "basaglar","insulin"]

medlist8 = ["sitagliptin", "janumet", "januvia", "juvisync",'mg']

medlist9 = ["amaryl", "glimepiride", "gleam", "k-glim-1", "glucoryl",  "glimpid", "glimy",'m','side','effect','ve','c','don','slow','release','t','didn','take']
medlist = medlist1 + medlist2 + medlist3 + medlist4 + medlist5 + medlist6 + medlist7 + medlist8 + medlist9

newmedlist = []

#converting to unicode#
for r in medlist:
    newmedlist.append(unicode(r, "utf-8"))
    
#now stop words include medicine names and common words in English#
stop = stop + newmedlist
print stop


#To return a list of words and bigrams contained in a sentence
def features(message):
    singlegrams =  [i for i in message.split() if i not in stop]#Removingstopwords
    
    singlegramsrefined = []
    #Stemming the single words
    for k in singlegrams:
        r = stem(k, stemmer=LEMMA)
        if r not in stop:
            singlegramsrefined.append(r)
    newmessage = " ".join(singlegramsrefined) 
    newmessage = re.sub("[^A-Za-z]", " ", newmessage)# Removing numbers
    newmessage = re.sub(r'[^\w]', ' ', newmessage)# Removing stopwords
    singlegrams= [i for i in newmessage.split() if len(i) > 1]

    singlegramsrefined2 = []
    
    for word in singlegrams:
        singlegramsrefined2.append(word)
        
    bigrams = ngrams(newmessage, n=2)#bigrams
    trigrams = ngrams(newmessage, n=3)#trigrams
    v = parsetree(newmessage, lemmata=True)[0]
    v = [w.lemma for w in v if w.tag.startswith(('NN'))]
    singlewords = []
    for i in v:
        stopping = stop + [u'glipizide',u'week',u'blood',u'feel',u'like',u'made',u'bad',u'work',u'still',u'got',u'twice',u'i',u'mg',u'm',u'day',u'sugar',u'taking',u'doctor',u'get',u'year',u'side',u'went',u'med',u'one',u'better',u'effect',u'problyear',u'side',u'went',u'med',u'one',u'better',u'effect',u'problem',u'also']
        if i not in stopping:
            singlewords.append(i)
    bi = []
    for r in bigrams:
        if r not in [(u'side', u'effect'),(u'i', u'm'),(u'i', u've'),(u'twice', u'day'),(u'a', u'c'),(u'don', u't'),(u'slow', u'release'),(u't', u'take'),(u't', u'take'),(u'good', u'luck'),(u'didn', u't'),(u'mg', u'twice'),(u'take', u'metformin'),(u'time', u'day'),(u'went', u'away'),(u'year', u'ago'),(u'much', u'better'),(u'extended', u'release'),(u'started', u'taking'),(u'can', u't'),(u'anyone', u'else'),(u'month', u'ago'),(u'mg', u'day')]:
            bi.append(r)      
   
    
    totalgrams = singlewords + bi + trigrams
    
    
    return totalgrams

ldaData = csv('output.csv')

conjointList = []
for i in ldaData:
    if i[0] != "" and i[0] != None:
        message = i[0].lower()
        listFeatures = features(message)
        conjointList.append([i[0].encode('utf-8'),listFeatures,i[1]])


wholelistFeatures = []
for i in conjointList:
    for r in i[1]:
        if r not in stop:
            wholelistFeatures.append(r)

dictFeatures = dict(collections.Counter(wholelistFeatures))
listmainFeatures = []
listcount = []
for key, value in  dictFeatures.items():
    if value>1:
        listmainFeatures.append(key)
        listcount.append(value)
print sum(listcount)
print len(listmainFeatures)        

featureMatrix = []

for r in conjointList:
    listFeat = r[1]
    idofMes = r[2]
    innerMatrix = []
    for m in listmainFeatures:
        innerMatrix.append(listFeat.count(m))
    featureMatrix.append(innerMatrix)

X = np.array(featureMatrix)

model = lda.LDA(n_topics = 10, n_iter=1500,random_state = 1)

print model.fit(X)
topic_word = model.topic_word_
n_top_words = 8
vocab = np.array(listmainFeatures)
for i, topic_dist in enumerate(topic_word):
    topic_words = vocab[np.argsort(topic_dist)][:-n_top_words:-1]
    print('Topic {}: {}'.format(i, topic_words))
   
        
    
    
    
        
        
        



    
    
    
        
        
    
    



