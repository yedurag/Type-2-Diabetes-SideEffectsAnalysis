#Facebook LDA Engine
#Author Yedurag Babu yzb0005
#Date 10/20/2015



from pattern.en import ngrams
from pattern.vector import stem, PORTER, LEMMA
from nltk.corpus import stopwords
from pattern.en import parsetree

import re

import collections
import numpy as np
import lda

import time
import threading
import mysql.connector

#Function to connect to the mysql database

def dbConnect():
    connection = mysql.connector.connect(user='root',host = 'localhost',database='facebookdata',use_unicode=True)
    return connection





#To return a list of words and bigrams contained in a sentence; similar to the one in engine
def features(message):
    #List of nltk stopwords
    stop = [u'i','diabetes','diabetic','type 2 diabetes','type 2', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves',
            u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers',
            u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who',
            u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have',
            u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or',
            u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between',
            u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in',
            u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where',
            u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some',
            u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can',
            u'will', u'just', u'don', u'should', u'now','m']
    singlegrams =  [i for i in message.split() if i not in stop]#Removingstopwords
    
    singlegramsrefined = []
    #Stemming the single words
    for k in singlegrams:
        r = stem(k, stemmer=LEMMA)
        if r not in stop:
            singlegramsrefined.append(r)
    newmessage = " ".join(singlegramsrefined) 
    newmessage = re.sub("[^A-Za-z]", " ", newmessage)# Removing numbers
    newmessage = re.sub(r'[^\w]', ' ', newmessage)# Removing non alphanumerics
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
        stopping = stop +[u'hour',u'husband',u'anything',u'thing',u'way',u'n',u'number',u'person',u'd',u'x',u'dose',u'drug',u'today',u'help',u'everyone',u'bed',u'mine',u'bed',u'issue',u'anyone',u'thank' ,u'test', u'eat',u'something',u'doc',u'time',u'c',u'luck',u'lb',u'dr',u'morning','t',u'pill',u'upset',u'take',u'couple',u'month',u'use',u'exercise',u'diet',u'lot',u'vision','taking',u've',u'time',u'month',u'level',u'body',u'diet',u'food',u'release', u'time', u'meal',u'glipizide',u'week',
                          'type','yr',u'symptom',u'cause',u'tablet',u'blood',u'feel',u'like',
                          u'made',u'bad',u'work',u'still',
                          u'got',u'twice',u'i',u'mg',u'm',u'day',
                          u'sugar',u'taking',u'doctor',u'get',u'year',
                          u'side',u'went',u'med',u'one',u'better',
                          u'effect',u'problyear',u'side',u'went',u'med',u'one',u'better',u'effect',u'problem',u'also']
        if i not in stopping:
            singlewords.append(i)
    bi = []
    for r in bigrams:
        if r not in [(u'year', u'now'),(u'also', u'take'),(u'doesn', u't') ,(u'take', u'food'),(u'taking', u'metformin'),(u'i', u'diagnosed'),(u'metformin', u'mg'),(u'empty', u'stomach'),(u'couldn', u't'),(u'blood', u'sugar'),(u'diet', u'exercise'),(u'mg', u'x'),(u'type', u'diabetes'),(u'side', u'effect'),(u'i', u'm'),(u'i', u've'),(u'twice', u'day'),
                     (u'a', u'c'),(u'don', u't'),(u'slow', u'release'),(u't', u'take'),(u't', u'take'),
                     (u'good', u'luck'),(u'didn', u't'),(u'mg', u'twice'),(u'take', u'metformin'),(u'time', u'day'),
                     (u'went', u'away'),(u'year', u'ago'),(u'much', u'better'),(u'extended', u'release'),(u'started', u'taking'),
                     (u'can', u't'),(u'anyone', u'else'),(u'month', u'ago'),(u'mg', u'day')]:
            bi.append(r)      
   
    
    totalgrams = singlewords + bi
    
    
    return totalgrams

#Function to select only the message text and id from the mysql table.
#Returns a list of lists of values
def sqlQuery():
    queryResults = []
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute("SELECT message_text,post_comment_id,created_date FROM facebook_maintable where side_effect_prob > 0.5")

    for t,uid,dt in cursor:
        queryResults.append([t,uid,dt])

    
    connection.close()
    return queryResults
	
#The setup for the LDA
#We need a numpy vector matrix to achieve the objective
#This function returns an LDA model which learns based on the data
def ldaSetUp(n_topics,n_iter):
    ldaData = sqlQuery()
    

    conjointList = []
    for i in ldaData:
        if i[0] != "" and i[0] != None:
            message = i[0].lower()
            listFeatures = features(message)
            conjointList.append([i[0],listFeatures,i[1],i[2]])

    stop = [u'i','diabetes','diabetic','type 2 diabetes','type 2', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves',
            u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers',
            u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who',
            u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have',
            u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or',
            u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between',
            u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in',
            u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where',
            u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some',
            u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can',
            u'will', u'just', u'don', u'should', u'now','m',u'hour',u'husband',u'anything',u'thing',u'way',u'n',u'number',
            u'person',u'd',u'x',u'dose',u'drug',u'today',u'help',u'everyone',u'bed',u'mine',u'bed',u'issue',u'anyone',u'thank' ,
            u'test', u'eat',u'something',u'doc',u'time',u'c',u'luck',u'lb',u'dr',u'morning','t',u'pill',u'upset',u'take',
            u'couple',u'month',u'use',u'exercise',u'diet',u'lot',u'vision','taking',u've',u'time',u'month',u'level',u'body',
            u'diet',u'food',u'release', u'time', u'meal',u'glipizide',u'week','type','yr',u'symptom',u'cause',u'tablet',
            u'blood',u'feel',u'like',u'made',u'bad',u'work',u'still',u'got',u'twice',u'i',u'mg',u'm',u'day',u'sugar',u'taking',
            u'doctor',u'get',u'year',u'side',u'went',u'med',u'one',u'better',u'effect',u'problyear',u'side',u'went',u'med',u'one',
            u'better',u'effect',u'problem',u'also']
    wholelistFeatures = []
    for i in conjointList:
        for r in i[1]:
            if r not in stop:
                wholelistFeatures.append(r)
    #We need to make a vector space which is being done here
    dictFeatures = dict(collections.Counter(wholelistFeatures))
    listmainFeatures = []
    listcount = []
    for key, value in  dictFeatures.items():
        if value>1:
            listmainFeatures.append(key)
            listcount.append(value)

    featureMatrix = []

    for r in conjointList:
        listFeat = r[1]
        idofMes = r[2]
        innerMatrix = []
        for m in listmainFeatures:
            innerMatrix.append(listFeat.count(m))
        featureMatrix.append(innerMatrix)
    #The vector space converted to numpy array which is input to LDA model
    X = np.array(featureMatrix)

    model = lda.LDA(n_topics, n_iter,random_state = 1)

    return [model,listmainFeatures,X,conjointList]


#Function which runs continously and remodels the LDA
#Writes the result to the mysql db
def foo():
    ldaModel = ldaSetUp(n_topics=10,n_iter=1500)[0]
    listmainFeatures = ldaSetUp(n_topics=10,n_iter=1500)[1]
    X = ldaSetUp(n_topics=10,n_iter=1500)[2]
    conjointList = ldaSetUp(n_topics=10,n_iter=1500)[3]

    cnx = dbConnect()
    cur = cnx.cursor()

    cur.execute("DELETE FROM lda_results")
    cur.execute("DELETE FROM lda_loglikes")
    insert_data = ("INSERT INTO lda_results "
                       "(created_date, message_text,topicnum, topic_words)"
                       "VALUES (%s, %s, %s,%s)")

    insert_loglikes = ("INSERT INTO lda_loglikes "
                       "(iterationnum, loglikes)"
                       "VALUES (%s, %s)")
    #This will print out the log likelihoods to the screen
                            
    print ldaModel.fit(X)
    topic_word = ldaModel.topic_word_
    n_top_words = 10
    vocab = np.array(listmainFeatures)
    listTopics = []                       

    doc_topic = ldaModel.doc_topic_
    
    for r in range(len(conjointList)):
        docText = conjointList[r][0]
        docDate = conjointList[r][3]
        predictedTopicnum = doc_topic[r].argmax()
        
    topicList = []
    for i,topic_dist in enumerate(topic_word):
        topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
        topicInner = list(topic_words)
        topicInner2 = [str(r) for r in topicInner]
        topics = " ".join(topicInner2)
        topicList.append([i,topics])
    ldaOutput = []  
    for r in range(len(conjointList)):
        
        docText = conjointList[r][0]
        docDate = conjointList[r][3]
        predictedTopicnum = doc_topic[r].argmax()

        for i in topicList:
            if predictedTopicnum == i[0]:
                ldaOutput.append([docDate,docText,'Topic: ' + str(predictedTopicnum+1),i[1]])
    cnx = dbConnect()
    cur = cnx.cursor()

    cur.execute("DELETE FROM lda_results")
    cur.execute("DELETE FROM lda_loglikes")
    insert_data = ("INSERT INTO lda_results "
                       "(created_date, message_text,topicnum, topic_words)"
                       "VALUES (%s, %s, %s,%s)")

    insert_loglikes = ("INSERT INTO lda_loglikes "
                       "(iterationnum, loglikes)"
                       "VALUES (%s, %s)")

    for point in ldaOutput:
        cur.execute(insert_data, point)
    loglikelyhoods = list(ldaModel.loglikelihoods_[5:])
    listlogs = []
    for i in range(len(loglikelyhoods)):
        iterationpoints = i+1
        listlogs.append([iterationpoints,loglikelyhoods[i]])
        
    for k in listlogs:
        cur.execute(insert_loglikes, k)
        

        
    cnx.commit()
    cnx.close()
    print "check now"
    threading.Timer(3000, foo).start()        
            
foo()            
    


        
    
    
    
        
        
        



    
    
    
        
        
    
    



