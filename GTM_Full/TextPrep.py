# Read JSON File

file_path = "docs/rawDoc.json"
import pandas as pd
jsonObj = pd.read_json(path_or_buf=file_path, lines=True,  orient='values')
#csvData=jsonObj.to_csv("docs/CSV.csv", index=False, sep="|")

# Text Process

import csv
from nltk.corpus import stopwords

from settings.common import word_tf_df
from preprocessing_pipeline.NextGen import NextGen
from preprocessing_pipeline import (Preprocess, RemovePunctuation, Capitalization, RemoveStopWords,
                                    RemoveShortWords, TwitterCleaner, RemoveUrls, Lemmatize)

if __name__ == '__main__':
    dataset_names = ['Prep']
    forbidden_words = []  # list of words to be blacklisted [amp, rt, ...]
    syn_file = None  # synonym file containing line for each set of synonyms: [word], [synonym1], [synonym2], ...
    extra_ngrams = []  # list of $-separated ngrams: [new$york$city, joe$biden, donald$trump, no$new$taxes]

    for j in range(0, len(dataset_names)):
        ds = dataset_names[j]

        stopwords_list = stopwords.words('english')
        stopwords_list.append(['rt', 'amp'])

        pipeline = Preprocess()
        rp = RemovePunctuation(keep_hashtags=False)
        ru = RemoveUrls()
        cap = Capitalization()
        short_words = RemoveShortWords()
        tc = TwitterCleaner()
        rsw = RemoveStopWords(extra_sw=stopwords_list)
        lm = Lemmatize()
        
        pipeline.document_methods = [(tc.remove_deleted_tweets, str(tc),),
                                     (tc.remove_users, str(tc),),
                                     (ru.remove_urls, str(ru),),
                                     (rp.remove_punctuation, str(rp),),
                                     (cap.lowercase, str(cap),),
                                     (tc.remove_rt, str(tc),),
                                     (rsw.remove_stopwords, str(rsw),),
                                     (short_words.remove_short_words, str(short_words),)
                                     ]
        
        ng = NextGen()
        path = 'docs/CSV.csv'.format(ds)


        docsStripFull = [] # list of lists
        dataset=[] # list of list of lists
        with open(path, 'r') as f:
            reader=csv.reader(f, delimiter="|")
            next(reader)
            i=0
            for line in reader:
                print(i)
                doc=[]
                doc.append(line[0]) # ID
                titleAndAbst=line[1]+' '+line[2]
                doc.append([titleAndAbst.strip().split(' ')])
                doc.append(line[4]) # Year
                doc.append(line[5][1:-1]) # Country
                doc.append(line[3])
                docsStripFull.append(doc)

                i += 1
                
            for docList in docsStripFull:
                dataset.append(docList[1])
        
        #full_preprocess takes list of list so dataset is list of list of lists

        with open("docs/processed.csv", "w") as f:
            writer=csv.writer(f)

            writer.writerow(["merged_id","doi","titleAbstr","year","country"])

            for i in range(0,len(dataset)):
                print(i)
                #processed_dataset returns list of lists (1 list inside)
                processed_dataset = ng.full_preprocess(dataset[i], pipeline, ngram_min_freq=10, extra_bigrams=None, extra_ngrams=extra_ngrams)
                
                
                for j, wd in enumerate(processed_dataset[0]):
                    if(lm.lemmatize(wd)!=None):
                        processed_dataset[0][j]=lm.lemmatize(wd)
                titleAbst=format(' '.join(processed_dataset[0]))

                output=[docsStripFull[i][0],docsStripFull[i][4], titleAbst, docsStripFull[i][2],docsStripFull[i][3]]
                writer.writerow(output)