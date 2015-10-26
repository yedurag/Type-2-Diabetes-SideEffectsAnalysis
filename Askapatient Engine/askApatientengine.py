#Askapatient text analytics engine
#Author Yedurag Babu yzb0005
#Date 10/26/2015


from pattern.vector import MULTINOMIAL,MAJORITY,Model, Document, BINARY, SVM, kfoldcv, IG, SLP,KNN, NB, TFIDF
from pattern.db import csv
from pattern.en import ngrams
from pattern.vector import stem, PORTER, LEMMA
from nltk.corpus import stopwords
import re
import csv as csv1
import collections
import datetime
import threading
import mysql.connector

#Function to connect to the mysql database

def dbConnect():
    connection = mysql.connector.connect(user='root',host = 'localhost',database='facebookdata',use_unicode=True)
    return connection



#Function to get data from csv dataset


def csvGrab(fileName):
    data = csv(fileName)

    data = [[d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[9],d[10]] for d in data]


    data = [data[i] for i in range(1,len(data))]

    data = [[d[0],d[1],d[2],d[3],d[4],d[5],d[6],datetime.datetime.strptime(d[7],"%m/%d/%Y").strftime('%Y-%m-%d'),d[8]] for d in data]


    return data


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
    avoidList1 = ["actos", "pioglitazone hydrochloride", "pioglitazone",  "glustin", "glizone", "pioz", "zactos"]

    avoidList2 = ["medformin","metfornin","metforin","glucophage", "metformin",
                  "glucophage xr", "metformin hydrochloride","carbophage sr", "riomet",
                  "fortamet", "glumetza", "obimet", "gluformin", "dianben", "diabex", "diaformin", "siofor","metfogamma",
                  "riomet","diformin","metformi","metphormin","metaforming","metfirman","metoformin","metfomin"]

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

#Function to normalize duration of drug consumption
def timeIntervalconversion(timeLength,quantity):
    durationDays = 0
    if quantity != "" and timeLength != "":
        durRatio = 1
        if timeLength=="m":
            durRatio = 4.34812
        elif timeLength == "y":
            durRatio = 52.1775

        elif timeLength == "d":
            durRatio = 0.142857

        else:
            durRatio = 1.000

    
        durationDays = durRatio * float(quantity)
        
    else:
        durationDays = 0
        
    return durationDays
        
#Function to bin age

def binAge(age):
    ageBin = ""
    if age !="":
        if float(age) <= 20.000:
            ageBin = "Less than 20"

        elif float(age) > 20.000 and float(age) <= 40.000:

            ageBin = "20 to 40"

        elif float(age) > 40.000 and float(age) <= 60.000:

            ageBin = "40 to 60"

        elif float(age) > 60.000 and float(age) <= 80.000:

            ageBin = "60 to 80"

        elif float(age) > 80.000:
            ageBin = "Greater than 80"

    else:
        ageBin = "Unknown"

    return ageBin


#Function to format gender

def formatGender(gender):
    formattedGender = ""

    if gender != "":

        if gender == "F":

            formattedGender = "Female"

        elif gender == "M":

            formattedGender = "Male"

    else:
        formattedGender = "Unknown"

    return formattedGender

#Main Function which does all the work
def foo():
    #Initializing everything
    connection = dbConnect()

    #cursor to the connection
    cursor = connection.cursor()

    #Deleting old data
    
    cursor.execute("DELETE FROM askapatient_maintable")

    
    datatoModel = csvGrab('AskapatientDataset.csv')

    
    insert_data = ("INSERT INTO askapatient_maintable "
                       "(rating, side_effects, comments, gender, age, age_bin, duration_days, date_entered, drug_name, nausea, weightlossgain, hypoglycaemia, diarrhoea, dizziness, breathingissues, headache, fatigue, pancreatitis, pain, kidneyproblems, gastricdiscomfort, skinproblems, visionproblems, mentalproblems, oedema, heartproblems, others)"
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                       

    datatoModel = [[int(d[0]),d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8]] for d in datatoModel]

    combinedDataset = []
    
    for review in datatoModel:

        

        if review[1] != "" and review[1] != None:
            countNausea = 0
            countWeightlossgain = 0
            countHypoglycaemia = 0
            countDiarrhoea = 0
            countDizziness = 0
            countBreathingissues = 0
            countHeadache = 0
            countFatigue = 0
            countPancreatitis = 0
            countPain = 0
            countKidneyproblems = 0
            countGastricdiscomfort = 0
            countSkinproblems = 0
            countVisionproblems = 0
            countMentalproblems = 0
            countOedema = 0
            countHeartproblems = 0
            countOthers = 0
            reviewSideeffect = review[1].lower()

            featuresReview = featureExtractor(reviewSideeffect,countgrams=2)

            listNausea = [(u'appetite', u'nausea'), 
                            (u'bit', u'nausea'), 
                            (u'brief', u'nausea'), 
                            (u'cramping', u'nausea'), 
                            (u'debilitating', u'nausea'), 
                            (u'diarrhea', u'naseau'), 
                            (u'diarrhoea', u'nausea'), 
                            (u'experience', u'nausea'), 
                            (u'far', u'nausea'), 
                            (u'flatulence', u'nausea'), 
                            (u'heartburn', u'nausea'), 
                            (u'initially', u'nausea'), 
                            (u'little', u'nausea'), 
                            (u'mild', u'nausea'), 
                            (u'naseau', u'much'), 
                            (u'nausea', u'acid'), 
                            (u'nausea', u'almost'), 
                            (u'nausea', u'also'), 
                            (u'nausea', u'bad'), 
                            (u'nausea', u'beginning'), 
                            (u'nausea', u'bruising'), 
                            (u'nausea', u'chills'), 
                            (u'nausea', u'constipation'), 
                            (u'nausea', u'don'), 
                            (u'nausea', u'extremely'), 
                            (u'nausea', u'first'), 
                            (u'nausea', u'gas'), 
                            (u'nausea', u'heartburn'), 
                            (u'nausea', u'horrible'), 
                            (u'nausea', u'hour'), 
                            (u'nausea', u'i'), 
                            (u'nausea', u'lack'), 
                            (u'nausea', u'light'), 
                            (u'nausea', u'like'), 
                            (u'nausea', u'los'), 
                            (u'nausea', u'much'), 
                            (u'nausea', u'muscle'), 
                            (u'nausea', u'nothing'), 
                            (u'nausea', u'occasional'), 
                            (u'nausea', u'period'), 
                            (u'nausea', u'really'), 
                            (u'nausea', u'side'), 
                            (u'nausea', u'st'), 
                            (u'nausea', u'tiredness'), 
                            (u'nausea', u'weight'), 
                            (u'nausea', u'went'), 
                            (u'pain', u'nausea'), 
                            (u'sickness', u'nausea'), 
                            (u'slight', u'nausea'), 
                            (u'started', u'nausea'), 
                            (u'stool', u'nausea'), 
                            (u'symptoms', u'nausea'), 
                            (u'take', u'nausea'), 
                            (u'throw', u'up'), 
                            (u'vomit', u'diarrhea'), 
                            (u'vomiting', u'anyone'), 
                            (u'vomiting', u'appetite'), 
                            (u'vomiting', u'chills'), 
                            (u'vomiting', u'dizzines'), 
                            (u'vomiting', u'extreme'), 
                            (u'vomiting', u'fatigue'), 
                            (u'vomiting', u'first'), 
                            (u'vomiting', u'stop'), 
                            (u'week', u'nausea'),"naseau", 
                            "nause", 
                            "nausea", 
                            "nauseou", 
                            "nauseous", 
                            "nausua", 
                            "vomited"]


            listWeightlossgain = [(u'accelerating', u'weight'), 
                                    (u'affect', u'weight'), 
                                    (u'ankle', u'weight'), 
                                    (u'appetite', u'weight'), 
                                    (u'approx', u'lbs'), 
                                    (u'attributed', u'weight'), 
                                    (u'away', u'weight'), 
                                    (u'before', u'weight'), 
                                    (u'change', u'weight'), 
                                    (u'excessive', u'weight'), 
                                    (u'experienced', u'weight'), 
                                    (u'fast', u'weight'), 
                                    (u'gain', u'almost'), 
                                    (u'gain', u'approx'), 
                                    (u'gain', u'also'), 
                                    (u'gain', u'lb'), 
                                    (u'gain', u'lbs'), 
                                    (u'gained', u'lb'), 
                                    (u'gained', u'lbs'), 
                                    (u'gained', u'lot'), 
                                    (u'gained', u'pound'), 
                                    (u'gained', u'pounds'), 
                                    (u'gaining', u'weight'), 
                                    (u'feet', u'weight'), 
                                    (u'great', u'lost'), 
                                    (u'huge', u'weight'), 
                                    (u'hunger', u'weight'), 
                                    (u'i', u'lost'), 
                                    (u'it', u'weight'), 
                                    (u'lb', u'days'), 
                                    (u'lb', u'drug'), 
                                    (u'lb', u'last'), 
                                    (u'lb', u'lb'), 
                                    (u'lb', u'month'), 
                                    (u'lb', u'months'), 
                                    (u'lb', u'one'), 
                                    (u'lb', u'past'), 
                                    (u'lb', u'put'), 
                                    (u'lb', u'weeks'), 
                                    (u'lb', u'weight'), 
                                    (u'lb', u'year'), 
                                    (u'loose', u'weight'), 
                                    (u'los', u'weight'), 
                                    (u'lost', u'ib'), 
                                    (u'lost', u'kg'), 
                                    (u'lost', u'pound'), 
                                    (u'lost', u'pounds'), 
                                    (u'lost', u'weight'), 
                                    (u'month', u'weight'), 
                                    (u'much', u'weight'), 
                                    (u'nausea', u'weight'), 
                                    (u'pain', u'weight'), 
                                    (u'pound', u'days'), 
                                    (u'pound', u'gained'), 
                                    (u'pound', u'month'), 
                                    (u'pound', u'one'), 
                                    (u'pound', u'three'), 
                                    (u'pound', u'two'), 
                                    (u'pound', u'weight'), 
                                    (u'pound', u'within'), 
                                    (u'problem', u'weight'), 
                                    (u'rapid', u'weight'), 
                                    (u'severe', u'weight'), 
                                    (u'significant', u'weight'), 
                                    (u'steady', u'weight'), 
                                    (u'unexplained', u'weight'), 
                                    (u'weighed', u'lb'), 
                                    (u'weight', u'also'), 
                                    (u'weight', u'despite'), 
                                    (u'weight', u'gain'), 
                                    (u'weight', u'gained'), 
                                    (u'weight', u'going'), 
                                    (u'weight', u'les'), 
                                    (u'weight', u'los'), 
                                    (u'weight', u'loss'), 
                                    (u'weight', u'past'), 
                                    (u'weight', u'started'), 
                                    (u'weight', u'taking'), 
                                    (u'weight', u'went'), "weight", 
                                    "weightgain", 
                                    "weights"]

            listHypoglycaemia = [(u'glucose', u'level'), 
                                    (u'glucose', u'levels'), 
                                    "hypo", 
                                    "hypoglycaemium"]

            listDiarrhoea = [(u'bit', u'diarrhea'), 
                                (u'bout', u'diarhea'), 
                                (u'bout', u'diarrhea'), 
                                (u'diarrea', u'first'), 
                                (u'diarrhea', u'bloating'), 
                                (u'diarrhea', u'constipation'), 
                                (u'diarrhea', u'cramp'), 
                                (u'diarrhea', u'day'), 
                                (u'diarrhea', u'days'), 
                                (u'diarrhea', u'diarrhea'), 
                                (u'diarrhea', u'eating'), 
                                (u'diarrhea', u'extreme'), 
                                (u'diarrhea', u'fatigue'), 
                                (u'diarrhea', u'first'), 
                                (u'diarrhea', u'gas'), 
                                (u'diarrhea', u'horrible'), 
                                (u'diarrhea', u'i'), 
                                (u'diarrhea', u'les'), 
                                (u'diarrhea', u'loose'), 
                                (u'diarrhea', u'naseau'), 
                                (u'diarrhea', u'on'), 
                                (u'diarrhea', u'sometime'), 
                                (u'diarrhea', u'st'), 
                                (u'diarrhea', u'stomach'), 
                                (u'diarrhea', u'upset'), 
                                (u'diarrhea', u'went'), 
                                (u'diarrhoea', u'nausea'), 
                                (u'experienced', u'diarrhea'), 
                                (u'fatigue', u'diarrhea'), 
                                (u'gas', u'diarrhea'), 
                                (u'gas', u'loose'), 
                                (u'headache', u'diarrhea'), 
                                (u'initially', u'diarrhea'), 
                                (u'little', u'diarrhea'), 
                                (u'loose', u'stool'), 
                                (u'loose', u'stools'), 
                                (u'loss', u'diarrhea'), 
                                (u'lot', u'pooping'), 
                                (u'major', u'diarrhea'), 
                                (u'occasional', u'diarrhea'), 
                                (u'one', u'immodium'), 
                                (u'pain', u'diarrhea'), 
                                (u'restroom', u'often'), 
                                (u'severe', u'diarrhea'), 
                                (u'stomach', u'diarrhea'), 
                                (u'stomach', u'loose'), 
                                (u'stool', u'felt'), 
                                (u'stool', u'first'), 
                                (u'stool', u'nausea'), 
                                (u'stool', u'st'), 
                                (u'stools', u'gi'), 
                                (u'terrible', u'diarrhoea'), 
                                (u'use', u'bathroom'), 
                                (u'vomit', u'diarrhea'), 
                                (u'went', u'bathroom'),"diareah", 
                                "diarhea", 
                                "diarrea", 
                                "diarreha", 
                                "diarrhea", 
                                "diarrhoea", 
                                "immodium", 
                                "pooping", 
                                "restroom", 
                                "stool", 
                                "stools", 
                                "toilet", "watery"]

            listDizziness = [(u'dizziness', u'los'), 
                                (u'get', u'dizzy'), 
                                (u'vomiting', u'dizzines'), "dizzyness", "fainting"]


            listBreathingissues = [(u'breath', u'chest'), 
                                    (u'breath', u'flu'), 
                                    (u'breath', u'lethargy'), 
                                    (u'breath', u'los'), 
                                    (u'breath', u'severe'), 
                                    (u'breath', u'tired'), 
                                    (u'crushing', u'chest'), 
                                    (u'difficulty', u'breathing'), 
                                    (u'feeling', u'chest'), 
                                    (u'feeling', u'cold'), 
                                    (u'felt', u'shortnes'), 
                                    (u'severe', u'shortnes'), 
                                    (u'short', u'breath'), 
                                    (u'shortnes', u'breath'), 
                                    (u'stuffy', u'nose'), 
                                    (u'trouble', u'breathing'), "asthma",
                                    "breath", 
                                    "breathe", 
                                    "breathing", 
                                    "cough", "lung"]

            listHeadache = [(u'appetite', u'headache'), 
                                    (u'head', u'ach'), 
                                    (u'head', u'slight'), 
                                    (u'headache', u'bad'), 
                                    (u'headache', u'diarrhea'), 
                                    (u'headache', u'evening'), 
                                    (u'headache', u'extreme'), 
                                    (u'headache', u'first'), 
                                    (u'headaches', u'extreme'), 
                                    (u'headaches', u'fatigue'), 
                                    (u'headaches', u'muscle'), 
                                    (u'light', u'headache'), 
                                    (u'mild', u'headache'), 
                                    (u'mild', u'headaches'), 
                                    (u'problems', u'headaches'), 
                                    (u'slight', u'headache'), 
                                    (u'sugar', u'headache'), 
                                    "head", "headache"]

            listFatigue = [(u'breath', u'lethargy'), 
                                    (u'breath', u'tired'), 
                                    (u'chills', u'fatigue'), 
                                    (u'chronic', u'fatigue'), 
                                    (u'diarrhea', u'fatigue'), 
                                    (u'energy', u'los'), 
                                    (u'energy', u'loss'), 
                                    (u'energy', u'tired'), 
                                    (u'extreme', u'fatigue'), 
                                    (u'extreme', u'tiredness'), 
                                    (u'extreme', u'weakness'), 
                                    (u'fatigue', u'constant'), 
                                    (u'fatigue', u'diarrhea'), 
                                    (u'fatigue', u'los'), 
                                    (u'fatigue', u'muscle'), 
                                    (u'fatigue', u'sore'), 
                                    (u'fatigue', u'tooth'), 
                                    (u'feel', u'sick'), 
                                    (u'feel', u'weird'), 
                                    (u'feeling', u'tired'), 
                                    (u'feeling', u'weak'), 
                                    (u'feet', u'tired'), 
                                    (u'general', u'weaknes'), 
                                    (u'headaches', u'fatigue'), 
                                    (u'lack', u'energy'), 
                                    (u'lethargy', u'joint'), 
                                    (u'lethargy', u'stopped'), 
                                    (u'little', u'tired'), 
                                    (u'muscle', u'weakness'), 
                                    (u'nausea', u'tiredness'), 
                                    (u'pain', u'weakness'), 
                                    (u'sluggishness', u'heavy'), 
                                    (u'stomach', u'weak'), 
                                    (u'swelling', u'lethargy'), 
                                    (u'vomiting', u'fatigue'), 
                                    (u'weaknes', u'legs'), "exertion", 
                                    "exhausted", 
                                    "fatigue", 
                                    "lethargic", 
                                    "lethargy", 
                                    "sleep", 
                                    "sleepines", 
                                    "sleepy", 
                                    "sluggishness", "weakness"]

            listPancreatitis=["pancreatitis","pancreas","pancreatic"]

            listPain = [(u'ach', u'pains'), 
                                (u'ache', u'feeling'), 
                                (u'ache', u'increased'), 
                                (u'ankle', u'pain'), 
                                (u'back', u'pain'), 
                                (u'ear', u'pain'), 
                                (u'extreme', u'pain'), 
                                (u'finger', u'pain'), 
                                (u'gain', u'painful'), 
                                (u'general', u'malaise'), 
                                (u'hurt', u'bad'), 
                                (u'hurt', u'lot'), 
                                (u'hurt', u'time'), 
                                (u'joint', u'pain'), 
                                (u'knee', u'pain'), 
                                (u'leg', u'ache'), 
                                (u'leg', u'pain'), 
                                (u'month', u'pain'), 
                                (u'muscle', u'ach'), 
                                (u'muscle', u'aches'), 
                                (u'muscle', u'pain'), 
                                (u'muscle', u'pains'), 
                                (u'muscle', u'spasms'), 
                                (u'pain', u'ankles'), 
                                (u'pain', u'back'), 
                                (u'pain', u'came'), 
                                (u'pain', u'constant'), 
                                (u'pain', u'day'), 
                                (u'pain', u'diarrhea'), 
                                (u'pain', u'extreme'), 
                                (u'pain', u'felt'), 
                                (u'pain', u'followed'), 
                                (u'pain', u'ga'), 
                                (u'pain', u'groin'), 
                                (u'pain', u'heavines'), 
                                (u'pain', u'kidney'), 
                                (u'pain', u'knee'), 
                                (u'pain', u'left'), 
                                (u'pain', u'legs'), 
                                (u'pain', u'made'), 
                                (u'pain', u'muscle'), 
                                (u'pain', u'nausea'), 
                                (u'pain', u'over'), 
                                (u'pain', u'pain'), 
                                (u'pain', u'relieved'), 
                                (u'pain', u'severe'), 
                                (u'pain', u'sore'), 
                                (u'pain', u'started'), 
                                (u'pain', u'stopped'), 
                                (u'pain', u'swelling'), 
                                (u'pain', u'upper'), 
                                (u'pain', u'water'), 
                                (u'pain', u'weakness'), 
                                (u'pain', u'weight'), 
                                (u'pain', u'went'), 
                                (u'painful', u'foot'), 
                                (u'painful', u'joints'), 
                                (u'painful', u'swollen'), 
                                (u'palpitations', u'pain'), 
                                (u'severe', u'pain'), 
                                (u'shoulder', u'pain'), 
                                (u'started', u'hurting'), 
                                (u'stomach', u'ache'), 
                                (u'tingling', u'pain'), 
                                (u'tooth', u'pain'), "ach", "ached", 
                                "aches", 
                                "aching", 
                                "achy", "malaise", "pain", "painful"]

            listKidneyproblems = [(u'pain', u'kidney'),"kidney","renal"]

            listGastricdiscomfort = [(u'abdominal', u'bloating'), 
                                        (u'acid', u'reflux'), 
                                        (u'acid', u'stomach'), 
                                        (u'appetite', u'headache'), 
                                        (u'appetite', u'however'), 
                                        (u'appetite', u'little'), 
                                        (u'appetite', u'lost'), 
                                        (u'appetite', u'lower'), 
                                        (u'appetite', u'nausea'), 
                                        (u'appetite', u'sugar'), 
                                        (u'appetite', u'weight'), 
                                        (u'arm', u'stomach'), 
                                        (u'bad', u'cramping'), 
                                        (u'bad', u'cramps'), 
                                        (u'bad', u'stomach'), 
                                        (u'bathroom', u'time'), 
                                        (u'bloated', u'stomach'), 
                                        (u'bloating', u'belly'), 
                                        (u'bloating', u'loose'), 
                                        (u'bloating', u'mild'), 
                                        (u'bloating', u'severe'), 
                                        (u'constant', u'hunger'), 
                                        (u'constant', u'nausea'), 
                                        (u'constantly', u'hungry'), 
                                        (u'constipated', u'time'), 
                                        (u'constipation', u'hair'), 
                                        (u'cramping', u'gas'), 
                                        (u'cramping', u'loose'), 
                                        (u'cramping', u'los'), 
                                        (u'cramping', u'nausea'), 
                                        (u'cramps', u'stomach'), 
                                        (u'day', u'stomach'), 
                                        (u'decrease', u'hunger'), 
                                        (u'decreased', u'appetite'), 
                                        (u'diarrhea', u'bloating'), 
                                        (u'diarrhea', u'constipation'), 
                                        (u'diarrhea', u'cramp'), 
                                        (u'diarrhea', u'gas'), 
                                        (u'diarrhea', u'stomach'), 
                                        (u'difficulty', u'swallowing'), 
                                        (u'egg', u'burp'), 
                                        (u'excessive', u'gas'), 
                                        (u'experienced', u'stomach'), 
                                        (u'feel', u'hungry'), 
                                        (u'flatulence', u'nausea'), 
                                        (u'ga', u'pain'), 
                                        (u'gain', u'cramping'), 
                                        (u'gas', u'bloating'), 
                                        (u'gas', u'diarrhea'), 
                                        (u'gas', u'loose'), 
                                        (u'gastro', u'intestinal'), 
                                        (u'gi', u'symptom'), 
                                        (u'gi', u'tract'), 
                                        (u'gi', u'upset'), 
                                        (u'gurgling', u'stomach'), 
                                        (u'gurgly', u'stomach'), 
                                        (u'heart', u'burn'), 
                                        (u'heartburn', u'almost'), 
                                        (u'heartburn', u'nausea'), 
                                        (u'hunger', u'muscle'), 
                                        (u'hunger', u'weight'), 
                                        (u'hungry', u'all'), 
                                        (u'hungry', u'sure'), 
                                        (u'increased', u'hunger'), 
                                        (u'les', u'appetite'), 
                                        (u'les', u'hungry'), 
                                        (u'little', u'tummy'), 
                                        (u'loose', u'bowel'), 
                                        (u'loose', u'bowels'), 
                                        (u'loose', u'stool'), 
                                        (u'loose', u'stools'), 
                                        (u'los', u'appetite'), 
                                        (u'los', u'appietite'), 
                                        (u'loss', u'appetite'), 
                                        (u'mild', u'constipation'), 
                                        (u'mild', u'stomach'), 
                                        (u'mouth', u'sore'), 
                                        (u'nausea', u'acid'), 
                                        (u'nausea', u'constipation'), 
                                        (u'nausea', u'gas'), 
                                        (u'nausea', u'heartburn'), 
                                        (u'pain', u'ga'), 
                                        (u'side', u'stomach'), 
                                        (u'slight', u'burning'), 
                                        (u'slight', u'constipation'), 
                                        (u'slight', u'stomach'), 
                                        (u'sore', u'tongue'), 
                                        (u'stomach', u'ache'), 
                                        (u'stomach', u'cramp'), 
                                        (u'stomach', u'diarrhea'), 
                                        (u'stomach', u'gas'), 
                                        (u'stomach', u'gurgling'), 
                                        (u'stomach', u'loose'), 
                                        (u'stomach', u'los'), 
                                        (u'stomach', u'mild'), 
                                        (u'stomach', u'problem'), 
                                        (u'stomach', u'time'), 
                                        (u'stomach', u'upset'), 
                                        (u'stomach', u'weak'), 
                                        (u'swelling', u'stomach'), 
                                        (u'upset', u'tummy'), 
                                        (u'vomiting', u'appetite'), 
                                        (u'week', u'stomach'), 
                                        "abdoman", 
                                        "abdomen", 
                                        "acid", 
                                        "acidity", 
                                        "appetite", 
                                        "appietite", 
                                        "belching", 
                                        "belly", 
                                        "bowels", 
                                        "colon", 
                                        "constipated", 
                                        "constipation", 
                                        "digest", 
                                        "digestion", 
                                        "gas", 
                                        "gassy", 
                                        "gastro", 
                                        "gi", 
                                        "gurgling", 
                                        "gurgly", 
                                        "heartburn", 
                                        "hiccup", 
                                        "hunger", 
                                        "swallowing"]

            listSkinproblems = [(u'bad', u'rash'), 
                                    (u'rash', u'leg'), 
                                    (u'rash', u'legs'), 
                                    "infection", 
                                    "infections", 
                                    "inflamed", 
                                    "irritation", 
                                    "itches", 
                                    "rash", 
                                    "skin"]


            listVisionproblems = [(u'vision', u'problem'), 
                                    "blurred", 
                                    "eye", 
                                    "eyesight", 
                                    "vision","eyes"]



            listMentalproblems = [(u'anxiety', u'attacks'), 
                                    (u'anxiety', u'feeling'), 
                                    (u'mood', u'swings'), 
                                    (u'panic', u'attacks'), 
                                    (u'stres', u'test'), 
                                    "anxiety", 
                                    "depressed", 
                                    "depression", 
                                    "depressive", 
                                    "emotional", 
                                    "fear", 
                                    "frustrated", 
                                    "mood", 
                                    "nervousness", 
                                    "nightmare", 
                                    "nightmares", 
                                    "panic", 
                                    "stres", 
                                    "swings"]

            listOedema = [(u'anemia', u'edema'), 
                            (u'ankle', u'swelled'), 
                            (u'ankle', u'swelling'), 
                            (u'ankle', u'swollen'), 
                            (u'edema', u'feet'), 
                            (u'edema', u'foot'), 
                            (u'edema', u'leg'), 
                            (u'edema', u'swelling'), 
                            (u'extreme', u'swelling'), 
                            (u'feet', u'heavines'), 
                            (u'foot', u'swell'), 
                            (u'foot', u'swelling'), 
                            (u'gain', u'swelling'), 
                            (u'horrible', u'swelling'), 
                            (u'leg', u'swelling'), 
                            (u'occasional', u'swelling'), 
                            (u'pain', u'swelling'), 
                            (u'painful', u'swollen'), 
                            (u'severe', u'edema'), 
                            (u'severe', u'swelling'), 
                            (u'swelling', u'ankles'), 
                            (u'swelling', u'edema'), 
                            (u'swelling', u'everywhere'), 
                            (u'swelling', u'feet'), 
                            (u'swelling', u'foot'), 
                            (u'swelling', u'left'), 
                            (u'swelling', u'leg'), 
                            (u'swelling', u'legs'), 
                            (u'swelling', u'lethargy'), 
                            (u'swelling', u'night'), 
                            (u'swelling', u'stomach'), 
                            (u'swelling', u'tightnes'), 
                            (u'swelling', u'went'), 
                            (u'swollen', u'ankle'), 
                            (u'swollen', u'ankles'), 
                            (u'swollen', u'legs'), 
                            "edema", 
                            "inflamed", 
                            "swelled", 
                            "swelling", 
                            "swollen"]


            listHeartproblems = [(u'congestive', u'heart'), 
                                    (u'enlarged', u'heart'), 
                                    (u'fast', u'heartbeat'), 
                                    (u'heart', u'attack'), 
                                    (u'heart', u'beat'), 
                                    (u'heart', u'failure'), 
                                    (u'heart', u'flutters'), 
                                    (u'heart', u'palpitations'), 
                                    (u'heart', u'racing'), 
                                    (u'heart', u'rate'), 
                                    (u'irregular', u'heart'), 
                                    (u'palpitations', u'pain'), 
                                    (u'retention', u'heart'), 
                                    "heart", 
                                    "heartbeat", 
                                    "palpitation", 
                                    "palpitations", 
                                    "tachycardium", "chest","ribs","rib",
                                    (u'tightnes', u'chest'), 
                                    (u'chest', u'pain'), 
                                    (u'chest', u'discomfort')]

            

            if set(listNausea)& set(featuresReview):
                countNausea = 1

            else:

                countNausea = 0

            if set(listWeightlossgain)& set(featuresReview):
                countWeightlossgain = 1

            else:
                countWeightlossgain = 0

            if set(listHypoglycaemia)& set(featuresReview):
                countHypoglycaemia = 1
            else:
                countHypoglycaemia = 0

            if set(listDiarrhoea)& set(featuresReview):
                countDiarrhoea = 1
            else:
                countDiarrhoea = 0

            if set(listDizziness)& set(featuresReview):
                countDizziness = 1
            else:
                countDizziness = 0
                
            if set(listBreathingissues)& set(featuresReview):
                countBreathingissues = 1
            else:
                countBreathingissues = 0

            if set(listHeadache)& set(featuresReview):
                countHeadache = 1
            else:
                countHeadache = 0

            if set(listFatigue)& set(featuresReview):
                countFatigue = 1
            else:
                countFatigue = 0

            if set(listPancreatitis)& set(featuresReview):
                countPancreatitis = 1
            else:
                countPancreatitis = 0

            if set(listPain)& set(featuresReview):
                countPain = 1
            else:
                countPain = 0

            if set(listKidneyproblems)& set(featuresReview):
                countKidneyproblems = 1
            else:
                countKidneyproblems = 0

            

            if set(listGastricdiscomfort)& set(featuresReview):
                countGastricdiscomfort = 1
            else:
                countGastricdiscomfort = 0

            if set(listSkinproblems)& set(featuresReview):
                countSkinproblems = 1
            else:
                countSkinproblems = 0

            if set(listVisionproblems)& set(featuresReview):
                countVisionproblems = 1
            else:
                countVisionproblems = 0


            if set(listMentalproblems)& set(featuresReview):
                countMentalproblems = 1
            else:
                countMentalproblems = 0


            if set(listOedema)& set(featuresReview):
                countOedema = 1
            else:
                countOedema = 0

            if set(listHeartproblems)& set(featuresReview):
                countHeartproblems = 1
            else:
                countHeartproblems = 0

            allCounts  =[countNausea,countWeightlossgain,countHypoglycaemia,countDiarrhoea,countDizziness,countBreathingissues,countHeadache,
                        countFatigue,
                            countPancreatitis,
                            countPain,
                            countKidneyproblems,
                            countGastricdiscomfort,
                            countSkinproblems,
                            countVisionproblems,
                            countMentalproblems,
                            countOedema,
                            countHeartproblems]

            if allCounts == [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]:
                countOthers = 1

            else:

                countOthers = 0

            #Rating,Sideffects, Comments, gender,age,timelength, quantity, date,name

            combinedDataset.append([review[0],review[1],review[2],formatGender(review[3]),str(review[4]),binAge(review[4]),
                                    timeIntervalconversion(review[5],review[6]),review[7],review[8],countNausea,countWeightlossgain,
                                    countHypoglycaemia,countDiarrhoea,countDizziness,countBreathingissues,countHeadache,
                                    countFatigue,
                                    countPancreatitis,
                                    countPain,
                                    countKidneyproblems,
                                    countGastricdiscomfort,
                                    countSkinproblems,
                                    countVisionproblems,
                                    countMentalproblems,
                                    countOedema,
                                    countHeartproblems,countOthers])
        else:
            combinedDataset.append([review[0],"No side effect reported",review[2],formatGender(review[3]),str(review[4]),binAge(review[4]),
                                    timeIntervalconversion(review[5],review[6]),review[7],review[8],0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

    for point in combinedDataset:
        if point != []:
            cursor.execute(insert_data, point) 
    connection.commit()
    connection.close()
    print "check now"
    threading.Timer(20, foo).start()  
                                   
            
foo()

            

                


            


            

            
                
                

                

            
                












            




    
    
        

            
            
    
        

        
            
            
        
    
        
    
    
    
