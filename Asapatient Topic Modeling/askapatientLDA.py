#Ask A patient LDA Engine
#Author Yedurag Babu yzb0005
#Date 10/26/2015



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





#Function to extract only the needed features from a text message
#Will be used in classification
def featureExtractor(textMessage,countgrams):
    textMessage = textMessage.lower()
    #Function to remove stop words
    stopWords = [u'i','m', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself',
                 u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its',
                 u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom',
                 u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have',
                 u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or',
                 u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between',
                 u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on',
                 u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how',
                 u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only',
                 u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now']
   
    
    avoidList1 = ['diabetes','type 2','diabetic']
    avoidList = stopWords + avoidList1
    #Removing these stop words and general cleaning
    singleGrams =  [i for i in textMessage.split() if i not in avoidList]
    singlegramsRefined = []

    #Stemming the words for normalization
    for k in singleGrams:
        r = stem(k, stemmer=LEMMA)
        singlegramsRefined.append(r)
    newMessage = " ".join(singlegramsRefined) 
    newMessage = re.sub("[^A-Za-z]", " ", newMessage)# Removing numbers
    newMessage = re.sub(r'[^\w]', ' ', newMessage)# Removing all non alphanumeric chars
    singleGrams= [i for i in newMessage.split()] #Again splitting to single grams


    singlegramsRefined2 = [word for word in singleGrams] #Keep this now because it works
    biGrams = ngrams(newMessage, n=2)# Generating bigrams
    triGrams = ngrams(newMessage, n=3)#Generating trigrams

    totalGramsrefined = []
    if countgrams == 1:
        
        totalGrams = singlegramsRefined2
        
        totalGramsrefined = [i for i in totalGrams]# We want only those features in the text data which is in the model

    elif countgrams == 2:
        totalGrams = singlegramsRefined2+biGrams
        
        totalGramsrefined = [i for i in totalGrams]

    elif countgrams == 3:
        totalGrams = singlegramsRefined2+biGrams + triGrams
        
        totalGramsrefined = [i for i in totalGrams]
        

    return totalGramsrefined

#Function to select only the required data from the mysql table.
#Returns a list of lists of values
def sqlQuery():
    queryResults = []
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute("SELECT unique_id,rating,side_effects,comments,gender,age, age_bin, duration_days,date_entered,drug_name FROM askapatient_maintable where rating<4")

    for unique_id,rating,side_effects,comments,gender,age, age_bin, duration_days,date_entered,drug_name in cursor:
        queryResults.append([unique_id,rating,side_effects,comments,gender,age, age_bin, duration_days,date_entered,drug_name])

    
    connection.close()
    return queryResults
	
#The setup for the LDA
#We need a numpy vector matrix to achieve the objective
#This function returns an LDA model which learns based on the data
def ldaSetUp(n_topics,n_iter):
    ldaData = sqlQuery()

    print "query complete"

    conjointList = []
    for i in ldaData:
        if i[2] != "" and i[2] != None:
            message = i[2].lower()
            listFeatures = featureExtractor(message,countgrams=2)
                                #unique_id,rating,side_effects,comments,gender,age, age_bin, duration_days,date_entered,drug_name
            conjointList.append([i[0],i[1],i[2],listFeatures,i[3],i[4],i[5],i[6],i[7],i[8],i[9]])

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
            u'better',u'effect',u'problem',u'also',"would","could","felt","started","injection",
            "took","thought","feeling","site","stopped","almost","away","first","constant","two","los","first",
             "ankle","foot","leg",(u'side', u'effect'),"acto","back","stopped",
            "started","ago","within","put","reported","lost","increased",(u'effect', u'reported'),"well",
            "started", (u'i', u'm'),"last",(u'i', u've'),"going",(u'didn', u't'),
            "go","didn","noticed",(u'can', u't'),"never","experienced","leg","extreme","back","left","severe",
            "los","high","even","problems","lose","fat","though","however","began","none","see",(u'stopped', u'taking'),
            "tried","daily","medication","months","retention","legs","hands","eating","night","walk", (u'a', u'c'),
            "medication","think","good","little","due", "come","since","next", (u'don', u't'),"stop",
            "getting","couldn",(u'couldn', u't'),"eating","legs","knee","shoulder","heart","arm",
            (u'blood', u'sugar'), "sleep","much","sure","seem","dosage","infection","shot",(u'started', u'taking'),
            "reading","may","normal","already","make","really","read","days","weeks","hungry","low","control","great","said","know"
            "starting",(u'injection', u'site'),"effects",(u'side', u'effects'),"water", "caused","taken","stopping","became","failure","years",
            "lower","hard","told","start","changed","many","alway","else","life","later","developed","say","hand","without","able","long",
            "fast","new","know"]
    wholelistFeatures = []
    for i in conjointList:
        for r in i[3]:
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
    print len(listmainFeatures)
    featureMatrix = []
    print "feature matrix created"
    for r in conjointList:
        listFeat = r[3]
        idofMes = r[0]
        innerMatrix = []
        for m in listmainFeatures:
            innerMatrix.append(listFeat.count(m))
        featureMatrix.append(innerMatrix)
    print len(featureMatrix)

    #The vector space converted to numpy array which is input to LDA model
    X = np.array(featureMatrix)
    print X.size
    model = lda.LDA(n_topics, n_iter,random_state = 1)
    print "lda model complete"
    return [model,listmainFeatures,X,conjointList]


#Function which runs continously and remodels the LDA
#Writes the result to the mysql db
def foo():
    ldaModel = ldaSetUp(n_topics=8,n_iter=1500)[0]
    listmainFeatures = ldaSetUp(n_topics=8,n_iter=1500)[1]
    X = ldaSetUp(n_topics=8,n_iter=1500)[2]
    conjointList = ldaSetUp(n_topics=8,n_iter=1500)[3]
    
    cnx = dbConnect()
    cur = cnx.cursor()

    cur.execute("DELETE FROM askapatient_lda_results")
    cur.execute("DELETE FROM askapatient_lda_loglikes")
    insert_data = ("INSERT INTO askapatient_lda_results "
                       "(rating,side_effects,comments,gender,age, age_bin, duration_days,date_entered,drug_name,topicnum, topic_words)"
                       "VALUES (%s, %s, %s,%s,%s, %s, %s,%s,%s, %s, %s)")

    insert_loglikes = ("INSERT INTO askapatient_lda_loglikes "
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
        docText = conjointList[r][2]
        docDate = conjointList[r][9]
        predictedTopicnum = doc_topic[r].argmax()
        
    topicList = []
    for i,topic_dist in enumerate(topic_word):
        topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
        topicInner = list(topic_words)
        topicInner2 = [str(r) for r in topicInner]
        topics = " ; ".join(topicInner2)
        topicList.append([i,topics])
    ldaOutput = []  
    for r in range(len(conjointList)):
        rating = conjointList[r][1]
        
        docText = conjointList[r][2]
        comments = conjointList[r][4]
        gender = conjointList[r][5]
        age = conjointList[r][6]
        age_bin = conjointList[r][7]
        duration_days = conjointList[r][8]
        
        docDate = conjointList[r][9]
        drug_name = conjointList[r][10]
        predictedTopicnum = doc_topic[r].argmax()

        for i in topicList:
            if predictedTopicnum == i[0]:
                ldaOutput.append([rating,docText,comments,gender,age,age_bin,duration_days,docDate,drug_name,'Topic: ' + str(predictedTopicnum+1),i[1]])
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
    threading.Timer(120, foo).start()        
            
foo()            
    


        
    
    
    
        
        
        



    
    
    
        
        
    
    



