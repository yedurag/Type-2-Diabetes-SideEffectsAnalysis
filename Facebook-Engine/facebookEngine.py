#Facebook Engine
#Author Yedurag Babu yzb0005
#Date 10/18/2015
#Most of the basic framework for this engine is taken from the tutorial given below.
#Thanks to scott@simplebeautifuldata.com
#http://simplebeautifuldata.com/2014/09/09/harvesting-facebook-posts-and-comments-with-python-part-1/

from pattern.vector import Model, Document, NB, MULTINOMIAL, IG, MAJORITY
from pattern.db import csv
from pattern.en import ngrams
from pattern.vector import stem, PORTER, LEMMA

import re

import urllib2
import json
import csv
import datetime
import time
import threading
import mysql.connector

#Function to connect to the mysql database

def dbConnect():
    connection = mysql.connector.connect(user='root',host = 'localhost',database='facebookdata',use_unicode=True)
    return connection
    
#Function to initialize the classification Model
def initializeModel():
    classifierModel = Model.load('classificationModel.slp')
    return classifierModel

#Function to initialize the NB classifier

def initializeNBclassifier():
    classifierModel = initializeModel()
    nbClassifier = NB(classifierModel,baseline=MAJORITY, method=MULTINOMIAL, alpha=0.0001)
    return nbClassifier

#Function to get list of features in the model
def modelFeatures():
    classifierModel = initializeModel()
    listModelfeatures = classifierModel.features
    return listModelfeatures


#Function to extract only the needed features from a text message
#Will be used in classification
def featureExtractor(textMessage,countgrams):
    textMessage = textMessage.lower()
    #Function to remove stop words
    stopWords = [u'i','m', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now']
    avoidList1 = ["actos", "pioglitazone hydrochloride", "pioglitazone",  "glustin", "glizone", "pioz", "zactos"]

    avoidList2 = ["medformin","metfornin","metforin","glucophage", "metformin", "glucophage xr", "metformin hydrochloride","carbophage sr", "riomet", "fortamet", "glumetza", "obimet", "gluformin", "dianben", "diabex", "diaformin", "siofor","metfogamma", "riomet","diformin","metformi","metphormin","metaforming","metfirman","metoformin","metfomin"]

    avoidList3 = ["byetta", "bydureon", "exenatide","byetta"]

    avoidList4 = ["victosa","victoza", "liraglutide", "saxenda","victoza"]

    avoidList5 = ["invokana", "invokana","canagliflozin"]

    avoidList6 = ["avandia", "rosiglitazone"]

    avoidList7 = ["insu","humalog","levimir","novolog","insuline","insulin glargine","insulins","lantus", "toujeo", "abasaglar", "basaglar","insulin","insulins","levamir","levemir"]

    avoidList8 = ["sitagliptin", "janumet", "januvia", "juvisync","junuvia","januvia","sitaglipton"]

    avoidList9 = ["amaryl", "glimepiride", "gleam", "k-glim-1", "glucoryl",  "glimpid", "glimy","ameryl"]
    
    avoidList10 = ['diabetes','type 2','diabetic']
    avoidList = stopWords + avoidList1 + avoidList2 + avoidList3 + avoidList4 + avoidList5 + avoidList6 + avoidList7 + avoidList8 + avoidList9 + avoidList10
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
    listModelfeatures = modelFeatures()
    totalGramsrefined = []
    if countgrams == 1:
        
        totalGrams = singlegramsRefined2
        
        totalGramsrefined = [i for i in totalGrams if i in listModelfeatures]# We want only those features in the text data which is in the model

    elif countgrams == 2:
        totalGrams = singlegramsRefined2+biGrams
        
        totalGramsrefined = [i for i in totalGrams if i in listModelfeatures]

    elif countgrams == 3:
        totalGrams = singlegramsRefined2+biGrams + triGrams
        
        totalGramsrefined = [i for i in totalGrams if i in listModelfeatures]
        

    return totalGramsrefined
    
    
    

#Function to construct the url for scraping the posts

#Source: http://simplebeautifuldata.com/2014/09/09/harvesting-facebook-posts-and-comments-with-python-part-1/

 
def urlMaker(initUrl, appId, appSecret): 
    
    urlPart = "/posts/?key=value&access_token=" + appId + "|" + appSecret
    madeUrl = initUrl + urlPart
 
    return madeUrl


#Function to convert the response into json
#Source: http://simplebeautifuldata.com/2014/09/09/harvesting-facebook-posts-and-comments-with-python-part-1/

def toJson(urlArg):
    
    webResponse = urllib2.urlopen(urlArg)

    #Converting to readable data
    readData = webResponse.read()

    #Converting to json
    jsonData = json.loads(readData)
    
    return jsonData

#This function will continously scrape the data objects on the graph until it reaches the end
#Source: http://simplebeautifuldata.com/2014/09/09/harvesting-facebook-posts-and-comments-with-python-part-1/

def scrapePosts(urlArg,postData, appId, appSecret):
    #Convert the input url to json data
    jsonData = toJson(urlArg)
    
    #To traverse through the next page
    if "paging" in jsonData.keys():
        if "next" in jsonData["paging"].keys():
            #Setting the next page url
            nextPage = jsonData["paging"]["next"]
        else:
            nextPage = ""
    else:
        nextPage = ""
        
        
    
    #Getting all the data
    jsonData = jsonData["data"]
    

    
    #To get all Meta Data that we can get
    for obj in jsonData:
        try:
            #We try to collect the post id, the post message and created time
            currentObj = [obj["id"].encode('utf-8'),obj["created_time"].encode('utf-8'),(datetime.datetime.strptime((obj["created_time"].encode('utf-8'))[:-5],"%Y-%m-%dT%H:%M:%S")).strftime('%Y'),(datetime.datetime.strptime((obj["created_time"].encode('utf-8'))[:-5],"%Y-%m-%dT%H:%M:%S")).strftime('%Y-%m'),(datetime.datetime.strptime((obj["created_time"].encode('utf-8'))[:-5],"%Y-%m-%dT%H:%M:%S")).strftime('%Y-%m-%d'),''.join(i for i in obj["message"].encode('utf-8')  if ord(i)<128)]
            
                            
        except Exception:
            currentObj = [ "error", "error", "error","error","error","error"]
            
        if currentObj[2] != "error":

            
            postData.append(currentObj)
            
            
    
    
    #Scraping the next url         

    if nextPage != "":
        #Here the function calls itself; This is called function recursion
        #Source: http://simplebeautifuldata.com/2014/09/16/harvesting-facebook-posts-and-comments-with-python-part-2/
        scrapePosts(nextPage, postData, appId, appSecret)
        
    
    
    return postData
        



#We have a separate url for comments. This url is constructed by this function
#Source: http://simplebeautifuldata.com/2014/09/09/harvesting-facebook-posts-and-comments-with-python-part-1/


def urlMakerComments(urlArg, postId, appId, appSecret):
    #Making the url for the comments
    commentsInitargs = postId + "/comments/?key=value&access_token=" + appId + "|" + appSecret
    commentsUrlmade = urlArg + commentsInitargs
    
    return commentsUrlmade

#This function will continously scrape the comment objects on the graph until it reaches the end
#Source: http://simplebeautifuldata.com/2014/09/09/harvesting-facebook-posts-and-comments-with-python-part-1/

def scrapeComments(urlArg, commentData, postId,postMessage):
    #Converting to json
    comments = toJson(urlArg)

    #Getting the comments data
    comments = comments["data"]

    
    #for each comment capture data
    for comment in comments:
        try:
            #We try to collect the comment id, comment message and time
            currentComment = [comment["id"].encode('utf-8'),comment["created_time"].encode('utf-8'),(datetime.datetime.strptime((comment["created_time"].encode('utf-8'))[:-5],"%Y-%m-%dT%H:%M:%S")).strftime('%Y'),(datetime.datetime.strptime((comment["created_time"].encode('utf-8'))[:-5],"%Y-%m-%dT%H:%M:%S")).strftime('%Y-%m'),(datetime.datetime.strptime((comment["created_time"].encode('utf-8'))[:-5],"%Y-%m-%dT%H:%M:%S")).strftime('%Y-%m-%d'), ''.join(i for i in comment["message"].encode('utf-8')  if ord(i)<128),''.join(i for i in postMessage  if ord(i)<128)]
            
            
            
        except Exception:
            currentComment = ["error", "error", "error", "error","error","error","error"]

        if currentComment[1] != "error":
            commentData.append(currentComment)
        if currentComment == None:
            commentData.append(["None","None","None","None","None","None",''.join(i for i in postMessage  if ord(i)<128)])
            
    #check if there is another page for the comments data to traverse
    try:
        #To get next page url if it exists
        nextPage = comments["paging"]["next"]
    except Exception:
        nextPage = None
            
            
    #if we have another page traverse that
    if nextPage is not None:
        scrapeComments(nextPage, commentData, postId, postMessage)
    else:
        return commentData

#This is the main function where the data pull, text analysis and output to the flask url happens
#Source: http://simplebeautifuldata.com/2014/09/09/harvesting-facebook-posts-and-comments-with-python-part-1/

def foo():
    #We need to see the times at which things are going on
    
    print(time.ctime())

    #Connection to the local mysql db
    
    connection = dbConnect()

    #cursor to the connection
    cursor = connection.cursor()

    #Deleting old data
    
    cursor.execute("DELETE FROM facebook_maintable")

    
    #Here we enter the app secret and app id
    appSecret = "ef5d6dc05fedba4f54508fc522285982"
    appId = "1670164576554241"
    
    #We have a list of facebook pages for which we are collecting the data. Right now we
    #get data from the T2Diabetes fb page only. Intend to add other pages in future
    listPages = ["T2Diabetes"]
    basicUrl = "https://graph.facebook.com/"
    
   
    #Need to modify this soon
    insert_data = ("INSERT INTO facebook_maintable ""(created_time,created_year,created_year_month,created_date,message_text,text_type,side_effect_prob,side_effect_indicator,actos,glucophage,byetta,victoza,invokana,avandia,lantus,januvia,amaryl,other_no_med,nausea,weight_loss_gain,hypoglycaemia,diarrhoea,dizziness,breathing_issues,headache,fatigue,pancreatitis,pain,kidney_problem,gastric_problem,skin_problem,vision_problem,mental_problem,other_no_problem,post_comment_id)""VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    


    #Getting the NB Classifier

    nbclassifier = initializeNBclassifier()



    #We intend to collect data for all the pages in the list
    for page in listPages:

        #Constructing the url based on the basic url
        currentPage = basicUrl + page
        
        #Here we try to extract the post data
        #For this we create the initial url. Rest everything will happen by itself based on function recursion
        postUrl = urlMaker(currentPage, appId, appSecret)

        #Initializing the list to collect our posts
        postData = []

        # Now we use the recursive function to get the data we need
        postData = scrapePosts(postUrl,postData, appId, appSecret)

        #Initializing a new list to carry everything regarding posts
        
        postDatarefined = []

        # This long loop here basically constructs the matrix for the post
        for post in postData:
            #Checking for nulls or Nones
            if post[5] != "" and post[5] != None and post[5] != 'None':
                postText = post[5].lower() #Lowercase for safety
                
                featuresText = featureExtractor(postText,3)#Extracting the features from the post text
                
                classifyDict = nbclassifier.classify(Document(featuresText),discrete = False)#Classifying the post text

                probDictionary = dict(classifyDict) #Converting it to a dictionary

                sideeffectProb = probDictionary[1] #Probability that the post has side effect content

                sideeffectIndicator = 0

                if float(sideeffectProb) > 0.500000: #Based on the probability we are calculating the binary variable indicator
                    sideeffectIndicator = 1
                else:
                    sideeffectIndicator = 0


                #In the following few lines we check for the presence of keywords in the post text and generate binary indicator variables
                #The code includes constructed lexicons of medicines based on LSA
                actosList = ["actos", "pioglitazone hydrochloride", "pioglitazone",  "glustin", "glizone", "pioz", "zactos"]

                actosInd = 0
                if any(word.lower() in postText for word in actosList):
                    actosInd = 1
                else:
                    actosInd = 0

                glucophageList = ["medformin","metfornin","metforin","glucophage", "metformin", "glucophage xr", "metformin hydrochloride","carbophage sr", "riomet", "fortamet", "glumetza", "obimet", "gluformin", "dianben", "diabex", "diaformin", "siofor","metfogamma", "riomet","diformin","metformi","metphormin","metaforming","metfirman","metoformin","metfomin"]

                glucophageInd = 0
                if any(word.lower() in postText for word in glucophageList):
                    glucophageInd = 1
                else:
                    glucophageInd = 0

                byettaList = ["byetta", "bydureon", "exenatide","byetta"]

                byettaInd = 0
                if any(word.lower() in postText for word in byettaList):
                    byettaInd = 1
                else:
                    byettaInd = 0

                victozaList = ["victosa","victoza", "liraglutide", "saxenda","victoza"]

                victozaInd = 0
                if any(word.lower() in postText for word in victozaList):
                    victozaInd = 1
                else:
                    victozaInd = 0

                invokanaList = ["invokana", "invokana","canagliflozin","invokona","invakona","invakana"]

                invokanaInd = 0
                if any(word.lower() in postText for word in invokanaList):
                    invokanaInd = 1
                else:
                    invokanaInd = 0

                avandiaList = ["avandia", "rosiglitazone"]

                avandiaInd = 0
                if any(word.lower() in postText for word in avandiaList):
                    avandiaInd = 1
                else:
                    avandiaInd = 0

                lantusList = ["insu","humalog","levimir","novolog","insuline","insulin glargine","insulins","lantus", "toujeo", "abasaglar", "basaglar","insulin","insulins","levamir","levemir"]
                

                lantusInd = 0
                if any(word.lower() in postText for word in lantusList):
                    lantusInd = 1
                else:
                    lantusInd = 0

                januviaList = ["sitagliptin", "janumet", "januvia", "juvisync","junuvia","januvia","sitaglipton"]

                januviaInd = 0
                if any(word.lower() in postText for word in januviaList):
                    januviaInd = 1
                else:
                    januviaInd = 0

                amarylList = ["amaryl", "glimepiride", "gleam", "k-glim-1", "glucoryl",  "glimpid", "glimy","ameryl"]

                amarylInd = 0
                if any(word.lower() in postText for word in amarylList):
                    amarylInd = 1
                else:
                    amarylInd = 0

                otherNoInd = 0
                if [actosInd,glucophageInd,byettaInd,victozaInd,invokanaInd,avandiaInd,lantusInd,januviaInd,amarylInd]== [0,0,0,0,0,0,0,0,0]:
                    otherNoInd = 1
                else:
                    otherNoInd = 0

                #Constructed lexicons for major side effects based on LSA
                nauseaList = ["nauseated","nauseou","nausium","nausiated","nauseous","nausea","ondanesteron","vomitting","throwing","vomiting","throw","vomit","puking"]

                weightlossGainlist = ["size","loss","slim","kg","loosing","lb","reduce","lose","wieght","weigh","kilo","pound","weight","lbs",(u'helped', u'weight'),(u'lost', u'pounds'),(u'dropped', u'size'),(u'lose', u'weight'),(u'lost', u'weight'),(u'lose', u'pound'),(u'weight', u'los'),(u'lost', u'almost'),(u'lost', u'lb'),(u'loosing', u'pounds'),(u'much', u'wieght'),"gained","gain","wieght","weigh","overweight",(u'weight', u'gain'),(u'kilo', u'gained'),(u'gained', u'weight')]

                hypoglycaemiaList = ["hypoglycaemia","lows","decrease","hypoglycaemium","lowered","hypoglycemia","dropped","lower",(u'causing', u'lows')]

                diarrhoeaList = ["diarrhoea","direahea","runs","diarrea","shit","imodium","stool","diarreha","poop","loose","diarrhoea","diarhhea","diahreah","bathroom","crap","diarriah","diahorrium","dehydration","diarrhea","diaherrium","bms"]

                dizzinessList = ["dizziness","dizzy"]

                breathingIssueslist = [("breathing", "issues"),"bronchitis","breathing","breath"]

                headacheList = ["headache","migraine","headaches","head","headnes","headache","headach",("head", "ache")]

                fatigueList = ["fatigue","fibromyalgium","exhausted","tired","stress","tirednes","weak","bed","sick","sweaty","tiredness",(u'felt', u'awful'),"sicknes"]

                pancreatitisList = ["pancreatitis","pancreatitis","pancreas","pancrea","pancreatus"]

                painList = ["pain","aches","ach","painful","pains","ache","pain","hurt"]

                kidneyProblemlist = [("kidney", "problems"),"stone","kidney","dialysi","kidneys"]

                gastricProblemlist = ["cramps","gas","gasto","bloated","cramping","bloating","bowel","gastrointestinal","gastro","indigestion","intestinal","tum","hiccup","abdominal","gall","belching","digestion","digestive","tummy","appetite","gut","peptide","belly","cramp","stomac","stomach","gi","ga","constipation"]

                skinProblemlist = ["burne","infections","rash","itch","sensation","itchy","infection","itchiness","itching","burning"]

                visionProblemlist = ["blurred","eye","vision","optician","blurry"]

                mentalProblemlist = ["depression","mental"]

                otherProblems = [(u'hair', u'loss'),"thyroid","hypothyroidism","paralysis","palsy","heart"]

                bifeaturesText = featureExtractor(postText,2)#Extracting the features from the post text
                
                
                nauseaInd = 0
                weightlossGainInd = 0
                hypoglycaemiaInd = 0
                diarrhoeaInd = 0
                dizzinessInd = 0
                breathingIssuesInd = 0
                headacheInd = 0
                fatigueInd = 0
                pancreatitisInd = 0
                painInd = 0
                kidneyProblemInd = 0
                gastricProblemInd = 0
                skinProblemInd = 0
                visionProblemInd = 0
                mentalProblemInd = 0
                otherProblemsInd = 0

                if set(bifeaturesText)& set(nauseaList):
                    nauseaInd = 1
                else:
                    nauseaInd = 0
                    
                if set(bifeaturesText)& set(weightlossGainlist):
                    weightlossGainInd = 1
                else:
                    weightlossGainInd = 0

                if set(bifeaturesText)& set(hypoglycaemiaList):
                    hypoglycaemiaInd = 1
                else:
                    hypoglycaemiaInd = 0

                if set(bifeaturesText)& set(diarrhoeaList):
                    diarrhoeaInd = 1
                else:
                    diarrhoeaInd = 0

                if set(bifeaturesText)& set(dizzinessList):
                    dizzinessInd = 1
                else:
                    dizzinessInd = 0

                if set(bifeaturesText)& set(breathingIssueslist):
                    breathingIssuesInd = 1
                else:
                    breathingIssuesInd = 0

                if set(bifeaturesText)& set(headacheList):
                    headacheInd = 1
                else:
                    headacheInd = 0

                if set(bifeaturesText)& set(fatigueList):
                    fatigueInd = 1
                else:
                    fatigueInd = 0

                if set(bifeaturesText)& set(pancreatitisList):
                    pancreatitisInd = 1
                else:
                    pancreatitisInd = 0

                if set(bifeaturesText)& set(painList):
                    painInd = 1
                else:
                    painInd = 0


                if set(bifeaturesText)& set(kidneyProblemlist):
                    kidneyProblemInd = 1
                else:
                    kidneyProblemInd = 0

                if set(bifeaturesText)& set(gastricProblemlist):
                    gastricProblemInd = 1
                else:
                    gastricProblemInd = 0

                if set(bifeaturesText)& set(skinProblemlist):
                    skinProblemInd = 1
                else:
                    skinProblemInd = 0

                if set(bifeaturesText)& set(visionProblemlist):
                    visionProblemInd = 1
                else:
                    visionProblemInd = 0

                if set(bifeaturesText)& set(mentalProblemlist):
                    mentalProblemInd = 1
                else:
                    mentalProblemInd = 0

                if set(bifeaturesText)& set(otherProblems):
                    otherProblemsInd = 1
                else:
                    otherProblemsInd = 0

                postDatarefined.append([post[1],post[2],post[3],post[4],post[5],'post',
                                        sideeffectProb,sideeffectIndicator,actosInd,glucophageInd,
                                        byettaInd,victozaInd,invokanaInd,avandiaInd,lantusInd,januviaInd,
                                        amarylInd,otherNoInd,nauseaInd,weightlossGainInd,hypoglycaemiaInd,
                                        diarrhoeaInd,dizzinessInd,breathingIssuesInd,headacheInd,fatigueInd,
                                        pancreatitisInd,painInd,kidneyProblemInd,gastricProblemInd,skinProblemInd,
                                        visionProblemInd,mentalProblemInd,otherProblemsInd,post[0]])
    
        #Initializing the list to collect our comments  
        commentData = []

        #Keep this for now
        all_comments = []

        for post in postData:
            commentUrl = urlMakerComments(basicUrl, post[0], appId, appSecret)
            
            # Now we use the recursive function on top to get the data we need
            
            commentData = scrapeComments(commentUrl, commentData, post[0], post[5])

        #Initializing new list for comment data
        commentDatarefined = []
        for post in commentData:
            if post[5] != "" and post[5] != None and post[5] != 'None':
                postText = post[5].lower() #Lowercase for safety
                postText1 = ''
                if post[6] != "" and post[6] != None and post[6] != 'None':
                    
                    postText1 = post[6].lower() #Lowercase for safety
                else:
                    postText1=''
                    
                
                featuresText = featureExtractor(postText,3)#Extracting the features from the post text
                
                classifyDict = nbclassifier.classify(Document(featuresText),discrete = False)#Classifying the post text

                probDictionary = dict(classifyDict) #Converting it to a dictionary

                sideeffectProb = probDictionary[1] #Probability that the post has side effect content

                sideeffectIndicator = 0

                if float(sideeffectProb) > 0.500000: #Based on the probability we are calculating the binary variable indicator
                    sideeffectIndicator = 1
                else:
                    sideeffectIndicator = 0


                #In the following few lines we check for the presence of keywords in the post text and generate binary indicator variables
                #The code includes constructed lexicons of medicines based on LSA
                actosList = ["actos", "pioglitazone hydrochloride", "pioglitazone",  "glustin", "glizone", "pioz", "zactos"]

                actosInd = 0
                if any(word.lower() in postText for word in actosList) or any(word.lower() in postText1 for word in actosList):
                    actosInd = 1
                else:
                    actosInd = 0

                glucophageList = ["medformin","metfornin","metforin","glucophage", "metformin", "glucophage xr", "metformin hydrochloride","carbophage sr", "riomet", "fortamet", "glumetza", "obimet", "gluformin", "dianben", "diabex", "diaformin", "siofor","metfogamma", "riomet","diformin","metformi","metphormin","metaforming","metfirman","metoformin","metfomin"]

                glucophageInd = 0
                if any(word.lower() in postText for word in glucophageList) or any(word.lower() in postText1 for word in glucophageList):
                    glucophageInd = 1
                else:
                    glucophageInd = 0

                byettaList = ["byetta", "bydureon", "exenatide","byetta"]

                byettaInd = 0
                if any(word.lower() in postText for word in byettaList) or any(word.lower() in postText1 for word in byettaList):
                    byettaInd = 1
                else:
                    byettaInd = 0

                victozaList = ["victosa","victoza", "liraglutide", "saxenda","victoza"]

                victozaInd = 0
                if any(word.lower() in postText for word in victozaList) or any(word.lower() in postText1 for word in victozaList):
                    victozaInd = 1
                else:
                    victozaInd = 0

                invokanaList = ["invokana", "invokana","canagliflozin","invokona","invakona","invakana"]

                invokanaInd = 0
                if any(word.lower() in postText for word in invokanaList) or any(word.lower() in postText1 for word in invokanaList):
                    invokanaInd = 1
                else:
                    invokanaInd = 0

                avandiaList = ["avandia", "rosiglitazone"]

                avandiaInd = 0
                if any(word.lower() in postText for word in avandiaList) or any(word.lower() in postText1 for word in avandiaList):
                    avandiaInd = 1
                else:
                    avandiaInd = 0

                lantusList = ["insu","humalog","levimir","novolog","insuline","insulin glargine","insulins","lantus", "toujeo", "abasaglar", "basaglar","insulin","insulins","levamir","levemir"]
                

                lantusInd = 0
                if any(word.lower() in postText for word in lantusList) or any(word.lower() in postText1 for word in lantusList):
                    lantusInd = 1
                else:
                    lantusInd = 0

                januviaList = ["sitagliptin", "janumet", "januvia", "juvisync","junuvia","januvia","sitaglipton"]

                januviaInd = 0
                if any(word.lower() in postText for word in januviaList) or any(word.lower() in postText1 for word in januviaList):
                    januviaInd = 1
                else:
                    januviaInd = 0

                amarylList = ["amaryl", "glimepiride", "gleam", "k-glim-1", "glucoryl",  "glimpid", "glimy","ameryl"]

                amarylInd = 0
                if any(word.lower() in postText for word in amarylList) or any(word.lower() in postText1 for word in amarylList):
                    amarylInd = 1
                else:
                    amarylInd = 0

                otherNoInd = 0
                if [actosInd,glucophageInd,byettaInd,victozaInd,invokanaInd,avandiaInd,lantusInd,januviaInd,amarylInd]== [0,0,0,0,0,0,0,0,0]:
                    otherNoInd = 1
                else:
                    otherNoInd = 0

                #Constructed lexicons for major side effects based on LSA
                nauseaList = ["nauseated","nauseou","nausium","nausiated","nauseous","nausea","ondanesteron","vomitting","throwing","vomiting","throw","vomit","puking"]

                weightlossGainlist = ["size","loss","slim","kg","loosing","lb","reduce","lose","wieght","weigh","kilo","pound","weight","lbs",(u'helped', u'weight'),(u'lost', u'pounds'),(u'dropped', u'size'),(u'lose', u'weight'),(u'lost', u'weight'),(u'lose', u'pound'),(u'weight', u'los'),(u'lost', u'almost'),(u'lost', u'lb'),(u'loosing', u'pounds'),(u'much', u'wieght'),"gained","gain","wieght","weigh","overweight",(u'weight', u'gain'),(u'kilo', u'gained'),(u'gained', u'weight')]

                hypoglycaemiaList = ["hypoglycaemia","lows","decrease","hypoglycaemium","lowered","hypoglycemia","dropped","lower",(u'causing', u'lows')]

                diarrhoeaList = ["diarrhoea","direahea","runs","diarrea","shit","imodium","stool","diarreha","poop","loose","diarrhoea","diarhhea","diahreah","bathroom","crap","diarriah","diahorrium","dehydration","diarrhea","diaherrium","bms"]

                dizzinessList = ["dizziness","dizzy"]

                breathingIssueslist = [("breathing", "issues"),"bronchitis","breathing","breath"]

                headacheList = ["headache","migraine","headaches","head","headnes","headache","headach",("head", "ache")]

                fatigueList = ["fatigue","fibromyalgium","exhausted","tired","stress","tirednes","weak","bed","sick","sweaty","tiredness",(u'felt', u'awful'),"sicknes"]

                pancreatitisList = ["pancreatitis","pancreatitis","pancreas","pancrea","pancreatus"]

                painList = ["pain","aches","ach","painful","pains","ache","pain","hurt"]

                kidneyProblemlist = [("kidney", "problems"),"stone","kidney","dialysi","kidneys"]

                gastricProblemlist = ["cramps","gas","gasto","bloated","cramping","bloating","bowel","gastrointestinal","gastro","indigestion","intestinal","tum","hiccup","abdominal","gall","belching","digestion","digestive","tummy","appetite","gut","peptide","belly","cramp","stomac","stomach","gi","ga","constipation"]

                skinProblemlist = ["burne","infections","rash","itch","sensation","itchy","infection","itchiness","itching","burning"]

                visionProblemlist = ["blurred","eye","vision","optician","blurry"]

                mentalProblemlist = ["depression","mental"]

                otherProblems = [(u'hair', u'loss'),"thyroid","hypothyroidism","paralysis","palsy","heart"]

                bifeaturesText = featureExtractor(postText,2)#Extracting the features from the post text
                
                
                nauseaInd = 0
                weightlossGainInd = 0
                hypoglycaemiaInd = 0
                diarrhoeaInd = 0
                dizzinessInd = 0
                breathingIssuesInd = 0
                headacheInd = 0
                fatigueInd = 0
                pancreatitisInd = 0
                painInd = 0
                kidneyProblemInd = 0
                gastricProblemInd = 0
                skinProblemInd = 0
                visionProblemInd = 0
                mentalProblemInd = 0
                otherProblemsInd = 0

                if set(bifeaturesText)& set(nauseaList):
                    nauseaInd = 1
                else:
                    nauseaInd = 0
                    
                if set(bifeaturesText)& set(weightlossGainlist):
                    weightlossGainInd = 1
                else:
                    weightlossGainInd = 0

                if set(bifeaturesText)& set(hypoglycaemiaList):
                    hypoglycaemiaInd = 1
                else:
                    hypoglycaemiaInd = 0

                if set(bifeaturesText)& set(diarrhoeaList):
                    diarrhoeaInd = 1
                else:
                    diarrhoeaInd = 0

                if set(bifeaturesText)& set(dizzinessList):
                    dizzinessInd = 1
                else:
                    dizzinessInd = 0

                if set(bifeaturesText)& set(breathingIssueslist):
                    breathingIssuesInd = 1
                else:
                    breathingIssuesInd = 0

                if set(bifeaturesText)& set(headacheList):
                    headacheInd = 1
                else:
                    headacheInd = 0

                if set(bifeaturesText)& set(fatigueList):
                    fatigueInd = 1
                else:
                    fatigueInd = 0

                if set(bifeaturesText)& set(pancreatitisList):
                    pancreatitisInd = 1
                else:
                    pancreatitisInd = 0

                if set(bifeaturesText)& set(painList):
                    painInd = 1
                else:
                    painInd = 0


                if set(bifeaturesText)& set(kidneyProblemlist):
                    kidneyProblemInd = 1
                else:
                    kidneyProblemInd = 0

                if set(bifeaturesText)& set(gastricProblemlist):
                    gastricProblemInd = 1
                else:
                    gastricProblemInd = 0

                if set(bifeaturesText)& set(skinProblemlist):
                    skinProblemInd = 1
                else:
                    skinProblemInd = 0

                if set(bifeaturesText)& set(visionProblemlist):
                    visionProblemInd = 1
                else:
                    visionProblemInd = 0

                if set(bifeaturesText)& set(mentalProblemlist):
                    mentalProblemInd = 1
                else:
                    mentalProblemInd = 0

                if set(bifeaturesText)& set(otherProblems):
                    otherProblemsInd = 1
                else:
                    otherProblemsInd = 0

                commentDatarefined.append([post[1],post[2],post[3],post[4],post[5],'comment',
                                        sideeffectProb,sideeffectIndicator,actosInd,glucophageInd,
                                        byettaInd,victozaInd,invokanaInd,avandiaInd,lantusInd,januviaInd,
                                        amarylInd,otherNoInd,nauseaInd,weightlossGainInd,hypoglycaemiaInd,
                                        diarrhoeaInd,dizzinessInd,breathingIssuesInd,headacheInd,fatigueInd,
                                        pancreatitisInd,painInd,kidneyProblemInd,gastricProblemInd,skinProblemInd,
                                        visionProblemInd,mentalProblemInd,otherProblemsInd,post[0]])


        totalDatarefined = postDatarefined + commentDatarefined

        #We are writing each of these text data points to the mysql table
        for point in totalDatarefined:
            cursor.execute(insert_data, point)
    
    connection.commit()
    connection.close()
    print "check now"
    threading.Timer(120, foo).start()        
            
foo()            
            
        
            

           
    
    
        
    
        
    

