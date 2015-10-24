#Open FDA Engine
#Author Yedurag Babu yzb0005
#Date 10/22/2015
#Most of the basic frameworks and ideas from https://open.fda.gov/drug/event/
#Courtesy to FDA for providing the API end points
#Courtesy to http://opendata.stackexchange.com/ for rectifying various doubts
from datetime import date, timedelta

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


#Function to make urls for custom purposes
#API key given as input parameter to account for the fact that it may be needed to be changed in future
#The base url is set in such a way that always the data will be in specified date limit and on specified medicine
def urlMaker(apiKey,curDate,medName,adverseInd,byDateind,otherMed,adverseEffect,ageGroup,patientSex,patientWeight,medChar):
    
    baseUrl = 'https://api.fda.gov/drug/event.json?api_key='+apiKey+'&search=receivedate:[20040101+TO+'+ curDate+']+AND+patient.drug.medicinalproduct.exact:"'+medName+'"'

    secondaryurl = ""
    #
    if byDateind ==1 and otherMed=="" and adverseEffect=="" and ageGroup=="" and patientSex=="" and patientWeight=="" and medChar=="":
        secondaryurl = baseUrl + "&count=receivedate"
    #  
    if adverseInd ==1:
        secondaryurl = baseUrl +"&count=patient.reaction.reactionmeddrapt.exact&limit=15"
    #
    if byDateind ==1 and otherMed != "":
        secondaryurl = baseUrl + '+AND+patient.drug.medicinalproduct.exact:"'+otherMed+'"'+"&count=receivedate"
    #
    if byDateind ==1 and adverseEffect != "":
        secondaryurl = baseUrl + '+AND+patient.reaction.reactionmeddrapt.exact:"'+adverseEffect+'"'+"&count=receivedate"
    #
    if byDateind ==1 and ageGroup !="":
        secondaryurl = baseUrl + '+AND+patient.patientonsetage:'+ageGroup + '+AND+patient.patientonsetageunit:801.exact'+ "&count=receivedate"

    #
    if byDateind ==1 and patientSex != "":
        secondaryurl = baseUrl + '+AND+patient.patientsex:'+patientSex+"&count=receivedate"

    #   
    if byDateind ==1 and patientWeight!= "":
        secondaryurl = baseUrl + '+AND+patient.patientweight:'+patientWeight+"&count=receivedate"

    #
    if byDateind == 1 and medChar != "":
        secondaryurl = baseUrl + '+AND+patient.drug.drugcharacterization:'+medChar+"&count=receivedate"


    return secondaryurl
        
        
#t = urlMaker(apiKey="yD9W4Mnq3BG68x2qClw4Cu9YNtBOqfLeSGrtXHqj",
                #curDate="20151022",medName="ACTOS",adverseInd=0,byDateind=1,otherMed="",adverseEffect="",ageGroup="",patientSex="",patientWeight="",medChar="2")

#Function to make urls for collecting other data from FAERS API
def otherurlMaker(apiKey,curDate,medName,medInd,outcomeInd,drugcharInd):
    baseUrl = 'https://api.fda.gov/drug/event.json?api_key='+apiKey+'&search=receivedate:[20040101+TO+'+ curDate+']+AND+patient.drug.medicinalproduct.exact:"'+medName+'"'
    secondaryurl =''
    if medInd == 1:
        secondaryurl = baseUrl +"&count=patient.drug.medicinalproduct.exact&limit=20"

    if outcomeInd ==1:
        secondaryurl = baseUrl + "&count=patient.reaction.reactionoutcome"

    


    if drugcharInd ==1:
        secondaryurl = baseUrl + "&count=patient.drug.drugcharacterization"

    return secondaryurl

        

#print otherurlMaker(apiKey="yD9W4Mnq3BG68x2qClw4Cu9YNtBOqfLeSGrtXHqj",
                    #curDate="20151023",medName="ACTOS",medInd=0,outcomeInd=0,drugcharInd=1)    

#Function to convert the response into json
#Source: http://simplebeautifuldata.com/2014/09/09/harvesting-facebook-posts-and-comments-with-python-part-1/

def toJson(urlArg):
    
    webResponse = urllib2.urlopen(urlArg)

    #Converting to readable data
    readData = webResponse.read()

    #Converting to json
    jsonData = json.loads(readData)
    
    return jsonData

#This function processes the JSON data pulled, in different ways in different scenarios; It has some error checking also;
#Maximum care has been taken to avoid errors


def dataCollect(jsonData,termInd,timeInd):
    termOutput = []
    timeOutput = []
    countOutput = []
    
    if termInd ==1:
        if "results" in jsonData.keys():
            if jsonData["results"] != []:
                for i in jsonData["results"]:
                    termOutput.append(i["term"].encode('utf-8'))
                    countOutput.append(i["count"])
    elif timeInd ==1:
        if "results" in jsonData.keys():
            if jsonData["results"] != []:
                for i in jsonData["results"]:
                    timeOutput.append(datetime.datetime.strptime(i["time"],"%Y%m%d").strftime('%Y-%m-%d'))
                    countOutput.append(i["count"])
    if termOutput==[] and timeOutput==[] and countOutput==[]:
        return []
    else:
        return [termOutput,timeOutput,countOutput]

#m = urlMaker(apiKey="yD9W4Mnq3BG68x2qClw4Cu9YNtBOqfLeSGrtXHqj",
                #curDate="20151022",medName="ACTOS",adverseInd=0,byDateind=1,otherMed="",adverseEffect="",ageGroup="",patientSex="",patientWeight="",medChar="2")
#print m
#r = toJson(m)

#v = dataCollect(r,termInd=0,timeInd=1)
#print v[2][2]
#print v[1][2]

#This is the main function where we do all the data pulls and writing to mysql

def foo():
    print(time.ctime())
    #Connection to the local mysql db
    
    connection = dbConnect()

    #cursor to the connection
    cursor = connection.cursor()
    #Deleting old data
    
    cursor.execute("DELETE FROM faers_data")

    insert_data = ("INSERT INTO faers_data "
                       "(medicine,received_date,received_month,received_year,adverse_count,adverse_event1,adverse_event1_count,adverse_event2,adverse_event2_count,adverse_event3,adverse_event3_count,adverse_event4,adverse_event4_count,adverse_event5,adverse_event5_count,adverse_event6,adverse_event6_count,adverse_event7,adverse_event7_count,adverse_event8,adverse_event8_count,adverse_event9,adverse_event9_count,adverse_event10,adverse_event10_count,adverse_event11,adverse_event11_count,adverse_event12,adverse_event12_count,adverse_event13,adverse_event13_count,adverse_event14,adverse_event14_count,adverse_event15,adverse_event15_count,othermed1,othermed1_count,othermed2,othermed2_count,othermed3,othermed3_count,othermed4,othermed4_count,othermed5,othermed5_count,othermed6,othermed6_count,othermed7,othermed7_count,agegroup_count1,agegroup_count2,agegroup_count3,agegroup_count4,agegroup_count5,patientsex_count1,patientsex_count2,patientsex_count3,patientweight_count1,patientweight_count2,patientweight_count3,medchars_count1,medchars_count2,medchars_count3)""VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    
    
    #Initializing all the params needed for fetching the data
    medicineList = ["ACTOS","METFORMIN","BYETTA","VICTOZA","INVOKANA","LANTUS","JANUVIA","AMARYL"]
    apiKey="yD9W4Mnq3BG68x2qClw4Cu9YNtBOqfLeSGrtXHqj"
    curDate = datetime.datetime.now().strftime('%Y%m%d')
    
    initialDate = date(2004, 1, 1)
    todaysDate = date.today()
    deltaDaysbetween = todaysDate - initialDate
    dateRange = [initialDate + timedelta(days=i) for i in range(deltaDaysbetween.days + 1)]
    dateRange = [i.strftime('%Y-%m-%d') for i in dateRange]
    combinedDataset = []

    print "Initializede everything correctly"
    
    #For each medicine, we are fetching the data
    for med in medicineList:

        #####The med loop #######
        listMeddates=[]
        listMedcount=[]
        medUrl = urlMaker(apiKey,curDate,med,adverseInd=0,byDateind=1,otherMed="",
                             adverseEffect="",ageGroup="",patientSex="",patientWeight="",medChar="")
        print medUrl
        medData = toJson(medUrl)
        medData = dataCollect(medData,termInd=0,timeInd=1)
        
        if medData != []:
            listMeddates = medData[1] #Storing the date data in a list for writing to mysql db
            listMedcount= medData[2]#Storing the count data in a list for writing to mysql db
        
        time.sleep(5)#We need to give 10 seconds break to make sure that we dont go over the 200 requests per minute


        print "Got medicine data"



        #####Top 15 adverse event loop#####
        #we are getting the top 15 adverse events for the medicine
        listAdverseevents = []
        listcountAdverseevents =[]
        adverseUrl = urlMaker(apiKey,curDate,med,adverseInd=1,byDateind=0,
                              otherMed="",adverseEffect="",ageGroup="",patientSex="",patientWeight="",medChar="")
        adverseData = toJson(adverseUrl)
        adverseData = dataCollect(adverseData,termInd=1,timeInd=0)
        if adverseData != []:
            listAdverseevents = adverseData[0] #Storing the term data in a list for writing to mysql db
            listcountAdverseevents = adverseData[2]#Storing the count data in a list for writing to mysql db

        time.sleep(5)#We need to give 10 seconds break to make sure that we dont go over the 200 requests per minute
        
        adverseEventdatelist = []
        adverseEventcountlist = []#Two lists to collect each adverse event counts and dates

        if listAdverseevents != []:
            for adverseEvent in listAdverseevents:#for each adverse event for the medicine we are collecting date wise distributions
                adverseEvent = adverseEvent.replace (" ", "+")#Need to replace space with + as per "https://open.fda.gov/api/reference/#query-syntax"
                listAdversedate = []
                listAdversecount = []
                
                adverseUrl2 = urlMaker(apiKey,curDate,med,adverseInd=0,byDateind=1,otherMed="",
                             adverseEffect=adverseEvent,ageGroup="",patientSex="",patientWeight="",medChar="")

                adverseData2 = toJson(adverseUrl2)
                adverseData2 = dataCollect(adverseData2,termInd=0,timeInd=1)
                if adverseData2 != []:
                    listAdversedate = adverseData2[1]
                    listAdversecount = adverseData2[2]
                adverseEventdatelist.append({adverseEvent:listAdversedate})#Writing the dates to the empty list defined above
                adverseEventcountlist.append({adverseEvent:listAdversecount})#Writing the counts to the empty list defined above
                time.sleep(5)
            time.sleep(15)#We need to give 10 seconds break to make sure that we dont go over the 200 requests per minute



        print "Got adverse event data"


        ###Other medicines loop#####
        medicineList1 = ["ACTOS","METFORMIN","BYETTA","VICTOZA","INVOKANA","LANTUS","JANUVIA","AMARYL"]

        otherMeddatelist = []
        otherMedcountlist = []#Two lists to collect each other medicine event counts and dates
        
        for i in medicineList1:
            if i != med:
                listotherMeddate=[]
                listotherMedcount=[]
                otherMedurl = urlMaker(apiKey,curDate,med,adverseInd=0,byDateind=1,otherMed=i,
                             adverseEffect="",ageGroup="",patientSex="",patientWeight="",medChar="")
                

                otherMedData = toJson(otherMedurl)
                
                otherMedData = dataCollect(otherMedData,termInd=0,timeInd=1)
                if otherMedData != []:
                    listotherMeddate = otherMedData[1]
                    listotherMedcount = otherMedData[2]
                otherMeddatelist.append({i:listotherMeddate})
                otherMedcountlist.append({i:listotherMedcount})
                time.sleep(5)

        time.sleep(5)#We need to give 10 seconds break to make sure that we dont go over the 200 requests per minute



        print "Got other medcine data"



        ####Age group Loop####

        listofAgegroups = ["[0+TO+20]","[20.1+TO+40]","[40.1+TO+60]","[60.1+TO+80]","[80.1+TO+1000]"]

        ageGroupdatelist = []
        ageGroupcountlist = []
        for ageGroups in listofAgegroups:
            listageGroupdate=[]
            listageGroupcount=[]
            
            ageGroupurl = urlMaker(apiKey,curDate,med,adverseInd=0,byDateind=1,otherMed="",
                             adverseEffect="",ageGroup=ageGroups,patientSex="",patientWeight="",medChar="")
            
            ageGroupData = toJson(ageGroupurl)
                
            ageGroupData = dataCollect(ageGroupData,termInd=0,timeInd=1)
            if ageGroupData != []:
                listageGroupdate = ageGroupData[1]
                listageGroupcount = ageGroupData[2]

            ageGroupdatelist.append({ageGroups:listageGroupdate})
            ageGroupcountlist.append({ageGroups:listageGroupcount})
            time.sleep(5)

        time.sleep(15)#We need to give 10 seconds break to make sure that we dont go over the 200 requests per minute
            
        print "Got age group data"



        ####Patient sex loop #####


        listPatientsex = ["0","1","2"]
        patientSexdatelist = []
        patientSexcountlist = []

        for patientSexs in listPatientsex:
            listpatientSexdate=[]
            listpatientSexcount=[]

            patientSexurl = urlMaker(apiKey,curDate,med,adverseInd=0,byDateind=1,otherMed="",
                             adverseEffect="",ageGroup="",patientSex=patientSexs,patientWeight="",medChar="")

            patientSexData = toJson(patientSexurl)

            patientSexData = dataCollect(patientSexData,termInd=0,timeInd=1)


            if patientSexData !=[]:

                listpatientSexdate = patientSexData[1]
                listpatientSexcount= patientSexData[2]

            patientSexdatelist.append({patientSexs:listpatientSexdate})
            patientSexcountlist.append({patientSexs:listpatientSexcount})
            time.sleep(5)

        time.sleep(15)#We need to give 10 seconds break to make sure that we dont go over the 200 requests per minute

        print "Got patient sex data"


        ####Patient weight loop ####

        listpatientweights = ["[0+TO+50]","[50.1+TO+80]","[80.1+TO+1000]"]

        patientWeightdatelist = []
        patientWeightcountlist = []

        for patientWeights in listpatientweights:
            listpatientWeightdate=[]
            listpatientWeightcount=[]

            patientWeighturl = urlMaker(apiKey,curDate,med,adverseInd=0,byDateind=1,otherMed="",
                             adverseEffect="",ageGroup="",patientSex="",patientWeight=patientWeights,medChar="")

            patientWeightData = toJson(patientWeighturl)

            patientWeightData = dataCollect(patientWeightData,termInd=0,timeInd=1)

            if patientWeightData !=[]:
                listpatientWeightdate = patientWeightData[1]
                listpatientWeightcount = patientWeightData[2]

            patientWeightdatelist.append({patientWeights:listpatientWeightdate})

            patientWeightcountlist.append({patientWeights:listpatientWeightcount})

            time.sleep(5)

        time.sleep(15)#We need to give 10 seconds break to make sure that we dont go over the 200 requests per minute

        print "Got weight data"

        ####Med Char loop ####

        listMedChars = ["1","2","3"]

        medCharsdatelist = []
        medCharscountlist = []

        for medChars in listMedChars:
            listmedCharsdate=[]
            listmedCharscount=[]

            medCharsurl = urlMaker(apiKey,curDate,med,adverseInd=0,byDateind=1,otherMed="",
                             adverseEffect="",ageGroup="",patientSex="",patientWeight="",medChar=medChars)

            medCharsData = toJson(medCharsurl)

            medCharsData = dataCollect(medCharsData,termInd=0,timeInd=1)

            if medCharsData !=[]:
                listmedCharsdate = medCharsData[1]
                listmedCharscount = medCharsData[2]

            medCharsdatelist.append({medChars:listmedCharsdate})

            medCharscountlist.append({medChars:listmedCharscount})

            time.sleep(5)

        time.sleep(15)#We need to give 10 seconds break to make sure that we dont go over the 200 requests per minute

        print "Got med char data"

        #Finally we combine everything into a single array
        
        

        for datestd in dateRange:

            #for i in range(len(listMeddates)):
            if datestd in listMeddates:
                indexmatch = listMeddates.index(datestd)
                Medcount = listMedcount[indexmatch]
            
            else:
                Medcount = 0
            
            
            adverseEvent1=listAdverseevents[0]
            adverseEvent1 = adverseEvent1.replace (" ", "+")
            adverseEvent2=listAdverseevents[1]
            adverseEvent2 = adverseEvent2.replace (" ", "+")
            
            adverseEvent3=listAdverseevents[2]
            adverseEvent3 = adverseEvent3.replace (" ", "+")
            adverseEvent4=listAdverseevents[3]
            adverseEvent4 = adverseEvent4.replace (" ", "+")
            adverseEvent5=listAdverseevents[4]
            adverseEvent5 = adverseEvent5.replace (" ", "+")
            adverseEvent6=listAdverseevents[5]
            adverseEvent6 = adverseEvent6.replace (" ", "+")
            adverseEvent7=listAdverseevents[6]
            adverseEvent7 = adverseEvent7.replace (" ", "+")
            adverseEvent8=listAdverseevents[7]
            adverseEvent8 = adverseEvent8.replace (" ", "+")
            adverseEvent9=listAdverseevents[8]
            adverseEvent9 = adverseEvent9.replace (" ", "+")
            adverseEvent10=listAdverseevents[9]
            adverseEvent10 = adverseEvent10.replace (" ", "+")
            adverseEvent11=listAdverseevents[10]
            adverseEvent11 = adverseEvent11.replace (" ", "+")
            adverseEvent12=listAdverseevents[11]
            adverseEvent12 = adverseEvent12.replace (" ", "+")
            adverseEvent13=listAdverseevents[12]
            adverseEvent13 = adverseEvent13.replace (" ", "+")
            adverseEvent14=listAdverseevents[13]
            adverseEvent14 = adverseEvent14.replace (" ", "+")
            adverseEvent15=listAdverseevents[14]
            adverseEvent15 = adverseEvent15.replace (" ", "+")

            adverseEvent1count = 0
            adverseEvent2count = 0
            adverseEvent3count = 0
            adverseEvent4count = 0
            adverseEvent5count = 0
            adverseEvent6count = 0
            adverseEvent7count = 0
            adverseEvent8count = 0
            adverseEvent9count = 0
            adverseEvent10count = 0
            adverseEvent11count = 0
            adverseEvent12count = 0
            adverseEvent13count = 0
            adverseEvent14count = 0
            adverseEvent15count = 0

 
            adverseEvent1datelist = []
            adverseEvent1countlist = []
            for k in adverseEventdatelist:

                if adverseEvent1 in k.keys():
                    
                    
                    adverseEvent1datelist = k[adverseEvent1]

            for k in adverseEventcountlist:
                if adverseEvent1 in k.keys():
                    adverseEvent1countlist = k[adverseEvent1]
            
            
            
            
            if datestd in adverseEvent1datelist:
                imatch = adverseEvent1datelist.index(datestd)
                adverseEvent1count = adverseEvent1countlist[imatch]
                        
                        
            else:
                adverseEvent1count = 0

            
                        
            
            adverseEvent2datelist = []
            adverseEvent2countlist = []
            for k in adverseEventdatelist:
                if adverseEvent2 in k.keys():
                    adverseEvent2datelist = k[adverseEvent2]

            for k in adverseEventcountlist:
                if adverseEvent2 in k.keys():
                    adverseEvent2countlist = k[adverseEvent2]
            
            if datestd in adverseEvent2datelist:
                jmatch = adverseEvent2datelist.index(datestd)
                adverseEvent2count = adverseEvent2countlist[jmatch]
                        
            else:
                adverseEvent2count = 0
                        

            adverseEvent3datelist = []
            adverseEvent3countlist = []
            for k in adverseEventdatelist:
                if adverseEvent3 in k.keys():
                    adverseEvent3datelist = k[adverseEvent3]

            for k in adverseEventcountlist:
                if adverseEvent3 in k.keys():
                    adverseEvent3countlist = k[adverseEvent3]

            if datestd in adverseEvent3datelist:
                kmatch = adverseEvent3datelist.index(datestd)
                adverseEvent3count = adverseEvent3countlist[kmatch]
                        
            else:
                adverseEvent3count = 0
                        

            adverseEvent4datelist = []
            adverseEvent4countlist = []
            for k in adverseEventdatelist:
                if adverseEvent4 in k.keys():
                    adverseEvent4datelist = k[adverseEvent4]

            for k in adverseEventcountlist:
                if adverseEvent4 in k.keys():
                    adverseEvent4countlist = k[adverseEvent4]
                    
            
            if datestd in adverseEvent4datelist:
                lmatch = adverseEvent4datelist.index(datestd)
                adverseEvent4count = adverseEvent4countlist[lmatch]
                        
            else:
                adverseEvent4count = 0
                        

            adverseEvent5datelist = []
            adverseEvent5countlist = []
            for k in adverseEventdatelist:
                if adverseEvent5 in k.keys():
                    adverseEvent5datelist = k[adverseEvent5]

            for k in adverseEventcountlist:
                if adverseEvent5 in k.keys():
                    adverseEvent5countlist = k[adverseEvent5]
                    

            if datestd in adverseEvent5datelist:
                mmatch = adverseEvent5datelist.index(datestd)
                adverseEvent5count = adverseEvent5countlist[mmatch]
                        
            else:
                adverseEvent5count = 0
                        

            adverseEvent6datelist = []
            adverseEvent6countlist = []
            for k in adverseEventdatelist:
                if adverseEvent6 in k.keys():
                    adverseEvent6datelist = k[adverseEvent6]

            for k in adverseEventcountlist:
                if adverseEvent6 in k.keys():
                    adverseEvent6countlist = k[adverseEvent6]
                    
  
            if datestd in adverseEvent6datelist:
                m = adverseEvent6datelist.index(datestd)
                adverseEvent6count = adverseEvent6countlist[m]
                       
            else:
                adverseEvent6count = 0
                        



            adverseEvent7datelist = []
            adverseEvent7countlist = []
            for k in adverseEventdatelist:
                if adverseEvent7 in k.keys():
                    adverseEvent7datelist = k[adverseEvent7]

            for k in adverseEventcountlist:
                if adverseEvent7 in k.keys():
                    adverseEvent7countlist = k[adverseEvent7]
                    
 
            if datestd in adverseEvent7datelist:
                m = adverseEvent7datelist.index(datestd)
                adverseEvent7count = adverseEvent7countlist[m]
                        
            else:
                adverseEvent7count = 0
                        

            adverseEvent8datelist = []
            adverseEvent8countlist = []
            for k in adverseEventdatelist:
                if adverseEvent8 in k.keys():
                    adverseEvent8datelist = k[adverseEvent8]

            for k in adverseEventcountlist:
                if adverseEvent8 in k.keys():
                    adverseEvent8countlist = k[adverseEvent8]
                    
            if datestd in adverseEvent8datelist:
                m = adverseEvent8datelist.index(datestd)
                adverseEvent8count = adverseEvent8countlist[m]
                        
            else:
                adverseEvent8count = 0
                        


            adverseEvent9datelist = []
            adverseEvent9countlist = []
            for k in adverseEventdatelist:
                if adverseEvent9 in k.keys():
                    adverseEvent9datelist = k[adverseEvent9]

            for k in adverseEventcountlist:
                if adverseEvent9 in k.keys():
                    adverseEvent9countlist = k[adverseEvent9]
                    
            if datestd in adverseEvent9datelist:
                m = adverseEvent9datelist.index(datestd)
                adverseEvent9count = adverseEvent9countlist[m]
                        
            else:
                adverseEvent9count = 0
                        



            adverseEvent10datelist = []
            adverseEvent10countlist = []
            for k in adverseEventdatelist:
                if adverseEvent10 in k.keys():
                    adverseEvent10datelist = k[adverseEvent10]

            for k in adverseEventcountlist:
                if adverseEvent10 in k.keys():
                    adverseEvent10countlist = k[adverseEvent10]
                    
            if datestd in adverseEvent10datelist:
                m = adverseEvent10datelist.index(datestd)
                adverseEvent10count = adverseEvent10countlist[m]
                        
            else:
                adverseEvent10count = 0
                        
                        


            adverseEvent11datelist = []
            adverseEvent11countlist = []
            for k in adverseEventdatelist:
                if adverseEvent11 in k.keys():
                    adverseEvent11datelist = k[adverseEvent11]

            for k in adverseEventcountlist:
                if adverseEvent11 in k.keys():
                    adverseEvent11countlist = k[adverseEvent11]
                    
            if datestd in adverseEvent11datelist:
                m = adverseEvent11datelist.index(datestd)
                adverseEvent11count = adverseEvent11countlist[m]
                        
            else:
                adverseEvent11count = 0
                        
                        


            adverseEvent12datelist = []
            adverseEvent12countlist = []
            for k in adverseEventdatelist:
                if adverseEvent12 in k.keys():
                    adverseEvent12datelist = k[adverseEvent12]

            for k in adverseEventcountlist:
                if adverseEvent12 in k.keys():
                    adverseEvent12countlist = k[adverseEvent12]
                    
            if datestd in adverseEvent12datelist:
                m = adverseEvent12datelist.index(datestd)
                adverseEvent12count = adverseEvent12countlist[m]
                        
            else:
                adverseEvent12count = 0
                        
                        


            adverseEvent13datelist = []
            adverseEvent13countlist = []
            for k in adverseEventdatelist:
                if adverseEvent13 in k.keys():
                    adverseEvent13datelist = k[adverseEvent13]

            for k in adverseEventcountlist:
                if adverseEvent13 in k.keys():
                    adverseEvent13countlist = k[adverseEvent13]
                    
            if datestd in adverseEvent13datelist:
                m = adverseEvent13datelist.index(datestd)
                adverseEvent13count = adverseEvent13countlist[m]
                        
            else:
                adverseEvent13count = 0
                        
                        



            adverseEvent14datelist = []
            adverseEvent14countlist = []
            for k in adverseEventdatelist:
                if adverseEvent14 in k.keys():
                    adverseEvent14datelist = k[adverseEvent14]

            for k in adverseEventcountlist:
                if adverseEvent14 in k.keys():
                    adverseEvent14countlist = k[adverseEvent14]
                    
            if datestd in adverseEvent14datelist:
                m = adverseEvent14datelist.index(datestd)
                adverseEvent14count = adverseEvent14countlist[m]
                        
            else:
                adverseEvent14count = 0
                        
                        





            adverseEvent15datelist = []
            adverseEvent15countlist = []
            for k in adverseEventdatelist:
                if adverseEvent15 in k.keys():
                    adverseEvent15datelist = k[adverseEvent15]

            for k in adverseEventcountlist:
                if adverseEvent15 in k.keys():
                    adverseEvent15countlist = k[adverseEvent15]
                    
            if datestd in adverseEvent15datelist:
                m = adverseEvent15datelist.index(datestd)
                adverseEvent15count = adverseEvent15countlist[m]
                        
            else:
                adverseEvent15count = 0
                        
                        


            #print "Dating for adverse events done"
            
            otherMed1count = 0
            otherMed2count = 0
            otherMed3count = 0
            otherMed4count = 0
            otherMed5count = 0
            otherMed6count = 0
            otherMed7count = 0
            listintermediateotherMed = ["ACTOS","METFORMIN","BYETTA","VICTOZA","INVOKANA","LANTUS","JANUVIA","AMARYL"]
            listintermediateotherMed = [ i for i in listintermediateotherMed if i != med]
            
            otherMedicine1 = listintermediateotherMed[0]
            otherMedicine2 = listintermediateotherMed[1]
            otherMedicine3 = listintermediateotherMed[2]
            otherMedicine4 = listintermediateotherMed[3]    
            otherMedicine5 = listintermediateotherMed[4]
            otherMedicine6 = listintermediateotherMed[5]
            otherMedicine7 = listintermediateotherMed[6]


            otherMedicine1datelist = []
            otherMedicine1countlist = []
            
            for f in otherMeddatelist:
                if otherMedicine1 in f.keys():
                    otherMedicine1datelist = f[otherMedicine1]

            for f in otherMedcountlist:
                if otherMedicine1 in f.keys():
                    otherMedicine1countlist = f[otherMedicine1]

            if datestd in otherMedicine1datelist:
                m = otherMedicine1datelist.index(datestd)
                otherMed1count = otherMedicine1countlist[m]
                        
            else:
                otherMed1count = 0
                        


            otherMedicine2datelist = []
            otherMedicine2countlist = []
            
            for f in otherMeddatelist:
                if otherMedicine2 in f.keys():
                    otherMedicine2datelist = f[otherMedicine2]

            for f in otherMedcountlist:
                if otherMedicine2 in f.keys():
                    otherMedicine2countlist = f[otherMedicine2]

            if datestd in otherMedicine2datelist:
                m = otherMedicine2datelist.index(datestd)
                otherMed2count = otherMedicine2countlist[m]
                        
            else:
                otherMed2count = 0
                        


            otherMedicine3datelist = []
            otherMedicine3countlist = []
            
            for f in otherMeddatelist:
                if otherMedicine3 in f.keys():
                    otherMedicine3datelist = f[otherMedicine3]

            for f in otherMedcountlist:
                if otherMedicine3 in f.keys():
                    otherMedicine3countlist = f[otherMedicine3]

            if datestd in otherMedicine3datelist:
                m = otherMedicine3datelist.index(datestd)
                otherMed3count = otherMedicine3countlist[m]
                        
            else:
                otherMed3count = 0
                        


            otherMedicine4datelist = []
            otherMedicine4countlist = []
            
            for f in otherMeddatelist:
                if otherMedicine4 in f.keys():
                    otherMedicine4datelist = f[otherMedicine4]

            for f in otherMedcountlist:
                if otherMedicine4 in f.keys():
                    otherMedicine4countlist = f[otherMedicine4]

            if datestd in otherMedicine4datelist:
                m = otherMedicine4datelist.index(datestd)
                otherMed4count = otherMedicine4countlist[m]
                        
            else:
                otherMed4count = 0
                        


            otherMedicine5datelist = []
            otherMedicine5countlist = []
            
            for f in otherMeddatelist:
                if otherMedicine5 in f.keys():
                    otherMedicine5datelist = f[otherMedicine5]

            for f in otherMedcountlist:
                if otherMedicine5 in f.keys():
                    otherMedicine5countlist = f[otherMedicine5]

            if datestd in otherMedicine5datelist:
                m = otherMedicine5datelist.index(datestd)
                otherMed5count = otherMedicine5countlist[m]
                        
            else:
                otherMed5count = 0
                        


            otherMedicine6datelist = []
            otherMedicine6countlist = []
            
            for f in otherMeddatelist:
                if otherMedicine6 in f.keys():
                    otherMedicine6datelist = f[otherMedicine6]

            for f in otherMedcountlist:
                if otherMedicine6 in f.keys():
                    otherMedicine6countlist = f[otherMedicine6]

            if datestd in otherMedicine6datelist:
                m = otherMedicine6datelist.index(datestd)
                otherMed6count = otherMedicine6countlist[m]
                        
            else:
                otherMed6count = 0
                        


            otherMedicine7datelist = []
            otherMedicine7countlist = []
            
            for f in otherMeddatelist:
                if otherMedicine7 in f.keys():
                    otherMedicine7datelist = f[otherMedicine7]

            for f in otherMedcountlist:
                if otherMedicine7 in f.keys():
                    otherMedicine7countlist = f[otherMedicine7]

            if datestd in otherMedicine7datelist:
                m = otherMedicine7datelist.index(datestd)
                otherMed7count = otherMedicine7countlist[m]
                        
            else:
                otherMed7count = 0
                        

            #print "Dating for other meds done"
            
            ageGroupcount1 = 0
            ageGroupcount2 = 0
            ageGroupcount3 = 0
            ageGroupcount4 = 0
            ageGroupcount5 = 0


            ageGroup1datelist = []
            ageGroup1countlist = []

            for f in ageGroupdatelist:
                if "[0+TO+20]" in f.keys():
                    ageGroup1datelist = f["[0+TO+20]"]

            for f in ageGroupcountlist:
                if "[0+TO+20]" in f.keys():
                    ageGroup1countlist = f["[0+TO+20]"]


            if datestd in ageGroup1datelist:
                m = ageGroup1datelist.index(datestd)
                ageGroupcount1 = ageGroup1countlist[m]
                        
            else:
                ageGroupcount1 = 0
                        


            ageGroup2datelist = []
            ageGroup2countlist = []

            for f in ageGroupdatelist:
                if "[20.1+TO+40]" in f.keys():
                    ageGroup2datelist = f["[20.1+TO+40]"]

            for f in ageGroupcountlist:
                if "[20.1+TO+40]" in f.keys():
                    ageGroup2countlist = f["[20.1+TO+40]"]

            if datestd in ageGroup2datelist:
                m = ageGroup2datelist.index(datestd)
                ageGroupcount2 = ageGroup2countlist[m]
                        
            else:
                ageGroupcount2 = 0
                        


            ageGroup3datelist = []
            ageGroup3countlist = []

            for f in ageGroupdatelist:
                if "[40.1+TO+60]" in f.keys():
                    #print "matched age group"
                    ageGroup3datelist = f["[40.1+TO+60]"]

            for f in ageGroupcountlist:
                if "[40.1+TO+60]" in f.keys():
                    ageGroup3countlist = f["[40.1+TO+60]"]

            if datestd in ageGroup3datelist:
                m = ageGroup3datelist.index(datestd)
                ageGroupcount3 = ageGroup3countlist[m]
                        
            else:
                ageGroupcount3 = 0
                        


            ageGroup4datelist = []
            ageGroup4countlist = []

            for f in ageGroupdatelist:
                if "[60.1+TO+80]" in f.keys():
                    ageGroup4datelist = f["[60.1+TO+80]"]

            for f in ageGroupcountlist:
                if "[60.1+TO+80]" in f.keys():
                    ageGroup4countlist = f["[60.1+TO+80]"]

            if datestd in ageGroup4datelist:
                m = ageGroup4datelist.index(datestd)
                ageGroupcount4 = ageGroup4countlist[m]
                        
            else:
                ageGroupcount4 = 0
                        


            ageGroup5datelist = []
            ageGroup5countlist = []

            for f in ageGroupdatelist:
                if "[80.1+TO+1000]" in f.keys():
                    ageGroup5datelist = f["[80.1+TO+1000]"]

            for f in ageGroupcountlist:
                if "[80.1+TO+1000]" in f.keys():
                    ageGroup5countlist = f["[80.1+TO+1000]"]

            if datestd in ageGroup5datelist:
                m = ageGroup5datelist.index(datestd)
                ageGroupcount5 = ageGroup5countlist[m]
                        
            else:
                ageGroupcount5 = 0
                        



            #print "Dating for age group done"
            
            patientSexcount1 = 0
            patientSexcount2 = 0
            patientSexcount3 = 0


            patientSex1datelist = []
            patientSex1countlist = []

            for f in patientSexdatelist:
                if "0" in f.keys():
                    patientSex1datelist = f["0"]

            for f in patientSexcountlist:
                if "0" in f.keys():
                    patientSex1countlist = f["0"]


            if datestd in patientSex1datelist:
                m = patientSex1datelist.index(datestd)
                patientSexcount1 = patientSex1countlist[m]
                        
            else:
                patientSexcount1 = 0
                        

            patientSex2datelist = []
            patientSex2countlist = []

            for f in patientSexdatelist:
                if "1" in f.keys():
                    patientSex2datelist = f["1"]

            for f in patientSexcountlist:
                if "1" in f.keys():
                    patientSex2countlist = f["1"]

            if datestd in patientSex2datelist:
                m = patientSex2datelist.index(datestd)
                patientSexcount2 = patientSex2countlist[m]
                        
            else:
                patientSexcount2 = 0
                        
        
            patientSex3datelist = []
            patientSex3countlist = []

            for f in patientSexdatelist:
                if "2" in f.keys():
                    patientSex3datelist = f["2"]

            for f in patientSexcountlist:
                if "2" in f.keys():
                    patientSex3countlist = f["2"]

            if datestd in patientSex3datelist:
                m = patientSex3datelist.index(datestd)
                patientSexcount3 = patientSex3countlist[m]
                        
            else:
                patientSexcount3 = 0
                        
        



            #print "Dating for sex done"


            patientWeightgroupcount1 = 0
            patientWeightgroupcount2 = 0
            patientWeightgroupcount3 = 0

            patientWeightgroup1datelist = []
            patientWeightgroup1countlist = []

            for f in patientWeightdatelist:
                if "[0+TO+50]" in f.keys():
                    patientWeightgroup1datelist = f["[0+TO+50]"]

            for f in patientWeightcountlist:
                if "[0+TO+50]" in f.keys():
                    patientWeightgroup1countlist = f["[0+TO+50]"]


            if datestd in patientWeightgroup1datelist:
                m = patientWeightgroup1datelist.index(datestd)
                patientWeightgroupcount1 = patientWeightgroup1countlist[m]
                        
            else:
                patientWeightgroupcount1 = 0
                        

            patientWeightgroup2datelist = []
            patientWeightgroup2countlist = []

            for f in patientWeightdatelist:
                if "[50.1+TO+80]" in f.keys():
                    patientWeightgroup2datelist = f["[50.1+TO+80]"]

            for f in patientWeightcountlist:
                if "[50.1+TO+80]" in f.keys():
                    patientWeightgroup2countlist = f["[50.1+TO+80]"]

            if datestd in patientWeightgroup2datelist:
                m = patientWeightgroup2datelist.index(datestd)
                patientWeightgroupcount2 = patientWeightgroup2countlist[m]
                        
            else:
                patientWeightgroupcount2 = 0
                        


            patientWeightgroup3datelist = []
            patientWeightgroup3countlist = []

            for f in patientWeightdatelist:
                if "[80.1+TO+1000]" in f.keys():
                    patientWeightgroup3datelist = f["[80.1+TO+1000]"]

            for f in patientWeightcountlist:
                if "[80.1+TO+1000]" in f.keys():
                    patientWeightgroup3countlist = f["[80.1+TO+1000]"]

            if datestd in patientWeightgroup3datelist:
                m = patientWeightgroup3datelist.index(datestd)
                patientWeightgroupcount3 = patientWeightgroup3countlist[m]
                        
            else:
                patientWeightgroupcount3 = 0
                        

            

            #print "Dating for weight done"

            medCharscount1 = 0  
            medCharscount2 = 0
            medCharscount3 = 0 
            
            medChars1datelist = []
            medChars1countlist = []

            for f in medCharsdatelist:
                if "1" in f.keys():
                    medChars1datelist = f["1"]

            for f in medCharscountlist:
                if "1" in f.keys():
                    medChars1countlist = f["1"]


            if datestd in medChars1datelist:
                m = medChars1datelist.index(datestd)
                medCharscount1 = medChars1countlist[m]
                        
            else:
                medCharscount1 = 0
                        

            medChars2datelist = []
            medChars2countlist = []

            for f in medCharsdatelist:
                if "2" in f.keys():
                    medChars2datelist = f["2"]

            for f in medCharscountlist:
                if "2" in f.keys():
                    medChars2countlist = f["2"]

            if datestd in medChars2datelist:
                m = medChars2datelist.index(datestd)
                medCharscount2 = medChars2countlist[m]
                        
            else:
                medCharscount2 = 0
                        

            medChars3datelist = []
            medChars3countlist = []

            for f in medCharsdatelist:
                if "3" in f.keys():
                    medChars3datelist = f["3"]

            for f in medCharscountlist:
                if "3" in f.keys():
                    medChars3countlist = f["3"]
                    
            
            if datestd in medChars3datelist:
                m = medChars3datelist.index(datestd)
                medCharscount3 = medChars3countlist[m]
                        
            else:
                medCharscount3 = 0
                        
            #print "Dating for med chars done"

            
            
            
            combinedDataset.append([med,datestd,datestd[:7],datestd[:4],Medcount,adverseEvent1,adverseEvent1count,
                                    adverseEvent2,adverseEvent2count,adverseEvent3,adverseEvent3count,
                                    adverseEvent4,adverseEvent4count,adverseEvent5,adverseEvent5count,
                                    adverseEvent6,adverseEvent6count,adverseEvent7,adverseEvent7count,
                                    adverseEvent8,adverseEvent8count,adverseEvent9,adverseEvent9count,
                                    adverseEvent10,adverseEvent10count,adverseEvent11,adverseEvent11count,
                                    adverseEvent12,adverseEvent12count,adverseEvent13,adverseEvent13count,
                                    adverseEvent14,adverseEvent14count,adverseEvent15,adverseEvent15count,
                                    otherMedicine1,otherMed1count,otherMedicine2,otherMed2count,otherMedicine3,otherMed3count,
                                    otherMedicine4,otherMed4count,otherMedicine5,otherMed5count,otherMedicine6,otherMed6count,
                                    otherMedicine7,otherMed7count,ageGroupcount1,ageGroupcount2,ageGroupcount3,ageGroupcount4,
                                    ageGroupcount5,patientSexcount1,patientSexcount2,patientSexcount3,patientWeightgroupcount1,
                                    patientWeightgroupcount2,patientWeightgroupcount3,medCharscount1,medCharscount2,medCharscount3])
            

    for point in combinedDataset:
        if point != []:
            cursor.execute(insert_data, point)       
    connection.commit()
    connection.close()
    print "check now"
    threading.Timer(2000, foo).start()     


foo()
               

        
            
            

                
            
            
            
            

        

        


          
            
            

        
            
                
        
        
        
            
            



            
            
            
        

    
   



