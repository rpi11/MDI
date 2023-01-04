from gdtm.helpers.common import load_flat_dataset

path_to_data = 'docs/processed.csv'
dataset = load_flat_dataset(path_to_data, delimiter=' ')

from gdtm.models import GTM

# Set these paths to the path where you saved the Mallet implementation of each model, plus bin/mallet
tnd_path = 'mallet/mallet-tnd/bin/mallet'
gtm_path = 'mallet/mallet-gtm/bin/mallet'

seed_topics_file = 'seeds/st5.csv'
stIDX=seed_topics_file[6:-4]+"__"

import csv

#top_words_NUM=[5,10,15]
#gtm_k_NUM=[5,10]

#top_words_NUM=[10]
#gtm_k_NUM=[30,35]

top_words_NUM=[15]
gtm_k_NUM=[25]

for i in top_words_NUM:
    for j in gtm_k_NUM:
        # We pass in the paths to the java code along with the data set and whatever parameters we want to set
        model = GTM(dataset=dataset, mallet_tnd_path=tnd_path, mallet_gtm_path=gtm_path, 
        tnd_k=j, gtm_k=j, phi=10, top_words=i, seed_topics_file=seed_topics_file)

        topics = model.get_topics()
        with open("keys_noise_topics/"+stIDX+"k_"+str(j)+"__topW_"+str(i)+"__TOPICS.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(topics)

        noise = model.get_noise_distribution()

        with open("keys_noise_topics/"+stIDX+"k_"+str(j)+"__topW_"+str(i)+"__NOISE.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(noise)


import csv
import os

# assign directory
directory = 'keys_noise_topics'
 
# iterate over files in
# that directory
topics=[]
noise=[]
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    
    if os.path.isfile(f) and "TOPICS" in filename:
        topics.append(filename)
    elif os.path.isfile(f) and "NOISE" in filename:
        noise.append(filename)

for t in topics:

    with open("keys_noise_topics/"+t[:-10]+"KEYS.csv","w") as k, open("keys_noise_topics/"+t, "r") as top, open("keys_noise_topics/"+t[:-10]+"NOISE.csv", "r") as noi:
        reader_top=csv.reader(top)
        reader_noi=csv.reader(noi)
        noise_words=[]
        
        for line in reader_noi:
            noise_words.append(line[0])
        writer=csv.writer(k)
        for line in reader_top:
            topic_filt=[]
            for word in line:
                if word not in noise_words:
                    topic_filt.append(word)
            writer.writerow(sorted(topic_filt))
        