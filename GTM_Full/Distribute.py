import csv
from preprocessing_pipeline import Lemmatize

TOPICS=["FOOD","POLLUTION","PLANT","RENEWABLE",\
    "SPECIES","WATER","ICE","INAF","HEALTH",\
        "ECON","DISASTER","MODEL"]

# LEMMATIZE KEYS
with open("distribution/O_distKeys.csv", "r") as distKeys,\
    open("distribution/X_distKeysLemmatize.csv", "w") as lemm:

            distKey_r=csv.reader(distKeys)
            distKeyLemm_w=csv.writer(lemm)

            lm=Lemmatize()
            
            idx=0
            for line in distKey_r:

                output=[]
                output.append(TOPICS[idx])

                for i,key in enumerate(line):
                    if(lm.lemmatize(key) != None):
                        line[i]=lm.lemmatize(key)
                    if line[i] not in output:
                        output.append(line[i])
                    
                distKeyLemm_w.writerow(output)
                idx += 1

with open("distribution/X_distKeysLemmatize.csv", "r") as distKeys,\
    open("distribution/X_distribution.csv", "w") as dist,\
        open("docs/processed.csv","r") as proc:

    keyReader=csv.reader(distKeys)
    docReader=csv.reader(proc)
    writer=csv.writer(dist)

    MISSED=0

    header=["merged_id","year","country"]

    for topic in TOPICS:
        header.append(topic)
    for topic in keyReader:
        for i in range(1,len(topic)):
            header.append(topic[i])
    
    writer.writerow(header)

    next(docReader)
    for line in docReader:
        output=[line[0], line[2], line[3]] #ID, Year, Country

        lineInput=[]

        distKeys.seek(0)
        for i,topic in enumerate(keyReader):
            topicInput=[]
            for j in range(1,len(topic)):
                if topic[j] in line[1]:
                    topicInput.append(1)
                else:
                    topicInput.append(0)
            
            topicInput.insert(0, sum(topicInput))
            lineInput.append(topicInput)

        for topicInputList in lineInput:
            output.append(topicInputList[0])
        for topicInputList in lineInput:
            for i in range(1, len(topicInputList)):
                output.append(topicInputList[i])
                
        writer.writerow(output)

        
