import json
import pandas as pd
import csv

def compile(file):
    with open(file, "r") as f, open("textCompile.csv", "w") as out:
        lines=f.readlines()
        writer=csv.writer(out, delimiter="|")
        text={}
        i=3
        while i<len(lines):
            print(i)

            line=lines[i][22:-3]
            if line not in text:

                text[line]=1

                id = lines[i-1][21:-3]
                doi = lines[i-2][5:-5]
                writer.writerow([doi,id,line])
            i += 6

def misinfo(File, Misinfo, Output):

    output={}

    with open(File, "r") as text, open(Misinfo, "r") as mis, open(Output, "w") as out:
        txt=csv.reader(text, delimiter="|")
        words=mis.readlines()
        writer=csv.writer(out)

        for i in range(0,len(words)):
            words[i]=words[i][:-1].lower()
            output[words[i]]={}


        for line in txt:
            for word in words:
                if word in line[2].lower():
                    output[word][line[0]]=[line[1],line[2]]
        json.dump(output, out, indent=4)

if __name__ == "__main__":
    file_path = "test_collected_tweet.txt"
    misinfo_path="misinfoPhrases.txt"
    compiled_path="textCompile.csv"
    filter_path="textFilter.csv"
    #compile(file_path)
    misinfo(compiled_path, misinfo_path, filter_path)