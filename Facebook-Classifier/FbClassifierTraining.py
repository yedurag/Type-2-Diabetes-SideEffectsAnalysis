
#For training this classifier we need pattern, nltk (including the corpus), re and csv modules#

from pattern.vector import Model, Document, BINARY, SVM, kfoldcv, IG, SLP,KNN, NB
from pattern.db import csv
from pattern.en import ngrams
from pattern.vector import stem, PORTER, LEMMA
from nltk.corpus import stopwords
import re
import csv as csv1

#The file 'FbTrainingData.csv' should be in the same directory#

data = csv('FbTrainingData.csv')
data = [[message, int(side_effect_indicator)] for message, side_effect_indicator in data]




#List of nltk stopwords
stop = stopwords.words('english')




#Adding medicine names and obvious names into the stop words
medlist1 = ["diabetes","actos", "pioglitazone hydrochloride", "pioglitazone",  "glustin", "glizone", "pioz", "zactos"]

medlist2 = ["medformin","glucophage", "metformin", "glucophage xr", "metformin hydrochloride", "carbophage sr", "riomet", "fortamet", "glumetza", "obimet", "gluformin", "dianben", "diabex", "diaformin", "siofor","metfogamma", "riomet"]

medlist3 = ["byetta", "bydureon", "exenatide"]

medlist4 = ["victoza", "liraglutide", "saxenda"]

medlist5 = ["invokana", "canagliflozin"]

medlist6 = ["avandia", "rosiglitazone"]

medlist7 = ["insulin glargine",  "lantus", "toujeo", "abasaglar", "basaglar","insulin"]

medlist8 = ["sitagliptin", "janumet", "januvia", "juvisync"]

medlist9 = ["amaryl", "glimepiride", "gleam", "k-glim-1", "glucoryl",  "glimpid", "glimy"]

medlist = medlist1 + medlist2 + medlist3 + medlist4 + medlist5 + medlist6 + medlist7 + medlist8 + medlist9

newmedlist = []

#converting to unicode#
for r in medlist:
    newmedlist.append(unicode(r, "utf-8"))
    
#now stop words include medicine names and common words in English#
stop = stop + newmedlist





#This will be our dataset
refineddata = [[c[0].lower(),c[1]] for c in data if c[0] != "" and c[0] != None]








#Function to convert the text into features(single words, bigrams and trigrams)#
def features(message):
    singlegrams =  [i for i in message.split() if i not in stop]#Removingstopwords
    
    singlegramsrefined = []
    #Stemming the single words
    for k in singlegrams:
        r = stem(k, stemmer=LEMMA)
        singlegramsrefined.append(r)
    newmessage = " ".join(singlegramsrefined) 
    newmessage = re.sub("[^A-Za-z]", " ", newmessage)# Removing numbers
    newmessage = re.sub(r'[^\w]', ' ', newmessage)# Removing stopwords
    singlegrams= [i for i in newmessage.split()]

    singlegramsrefined2 = []
    
    for word in singlegrams:
        singlegramsrefined2.append(word)
        
    bigrams = ngrams(newmessage, n=2)#bigrams
    trigrams = ngrams(newmessage, n=3)#trigrams
    
    totalgrams = singlegramsrefined2 + bigrams + trigrams
    
    totalgrams = tuple(totalgrams)#tuple having single words, bigrams and trigrams
    return totalgrams








refineddata1 = [(features(c[0]),c[1]) for c in refineddata]


#Each datapoint becomes a pattern document here; The type represents the label for each document#
refineddata2 = [Document(message, type=sideeffectindicator) for message, sideeffectindicator in refineddata1]


#Defining the model using the documents; feature weight is Information gain; You can try changing to TF, TFIDF etc#
model = Model(documents=refineddata2, weight=IG)


#Top 500 features selected#
features=model.feature_selection(top=500)

#If medicine names are present they are removed #
refinedfeatures = []
for i in features:
    if i not in medlist:
        refinedfeatures.append(i)
        




#After few rounds of examining the top features the following top features will be removed to make the model more general#
        
avoidList1 = [u'mg',u'release',(u'slow', u'release'),(u'take', u'metformin'),(u'mg', u'twice'),(u'extended', u'release')]

avoidList2 = [u'nauseou',u'glipizide',(u'metformin', u'i'),(u'mg', u'day'),(u'mg', u'twice', u'day'),(u'started', u'mg')]

avoidList3 = [(u'metformin', u'made'),(u'day', u'mg'),(u'med', u'insulin'),(u'mg', u'morning')]

avoidList4 = [(u'twice', u'day', u'mg'),(u'mg', u'x'),(u'taking', u'mg'),u'gliclazide',(u'acid', u'mg'),(u'changing', u'slow'),(u'changing', u'slow', u'release')]

avoidList5 = [(u'extended', u'release', u'form'),(u'first', u'started', u'mg'),(u'fog', u'storm'),(u'fog', u'storm', u'low')]

avoidList6 = [(u'glipizide', u'made'),(u'insulin', u'am'),(u'insulin', u'am', u'tested'),(u'like', u'fog'),(u'like', u'fog', u'storm'),(u'lipoic', u'acid', u'mg')]


avoidList7 = [(u'metformin', u'i', u'horrible'),(u'metformin', u'made', u'sick'),(u'problem', u'take', u'metformin'),(u'slow', u'release', u'one')]

avoidList8 = [(u'take', u'metformin', u'i'),(u'told', u'take', u'metformin'),(u'took', u'med', u'insulin')]

avoidList9 = [(u'x', u'mg', u'tablet'),u'glyberide',u'jentadueto',u'snd',(u'mg', u'time'),(u'mg', u'time', u'day')]


avoidList10 = [u'glyburide',(u'problem', u'metformin'),(u'day', u'glyburide'),(u'day', u'mg', u'twice'),(u'im', u'slow', u'release')]

avoidList11 = [(u'insulin', u'i', u'm'),(u'metformin', u'doctor'),(u'started', u'metformin'),(u'taking', u'mg', u'twice'),u'glimeperide']


avoidList12 = [u'levimir',u'lisinopril',u'metformine']

avoidList = avoidList1 + avoidList2 + avoidList3 + avoidList4

avoidList = avoidList + avoidList5 + avoidList6 + avoidList7 + avoidList8 + avoidList9 + avoidList10 + avoidList11 + avoidList12









#How many features in avoid list
print len(avoidList)



#How many features were there before
print len(refinedfeatures)


cleanFeatures = [i for i in refinedfeatures if i not in avoidList]


#How many features after filtering out avoid list
print len(cleanFeatures)

#model redefines
model = model.filter(features=cleanFeatures)

#This will give k fold cross validation results; Instead of Naive Bayes you can try SVM, SLP, KNN etc

print kfoldcv(NB, model)







#Writing the features and their weights to a csv file

listofFeatures = []

for i in cleanFeatures:
    innerList= [i,model.ig(i)]
    listofFeatures.append(innerList)

f = open("Features.csv", "wb")
writer = csv1.writer(f,delimiter=',')

for item in listofFeatures:
    writer.writerow(item)
f.close()
print "Features written to csv file"
