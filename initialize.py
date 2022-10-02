from google.cloud import storage
import re
import json
import main

# Configuration for the paraphrase generation
pruning = "On"
config = "c1"
compute_metrics = "On"
pivot_level = "1"
pre_trained = "no"
num_seq = 30

# Initialize cloud bucket
bucket_name = "ppibot-bucket"
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

def download_training_file():
    file = "training.csv"
    blob = bucket.blob(file)
    blob.download_to_filename(file)

def process_training_file():
    with open('training.csv', 'r') as f:
        data = f.read()
    data = data.split('</s>')[0:-1]
    
    tokens = []
    tags = []

    for i in range(len(data)):
        phrase_tokens = []
        phrase_tags = []

        if i == 0:
            phrase = data[i].split('\n')[1:-1]
        else:
            phrase = data[i].split('\n')[2:-1]
        
        for j in range(len(phrase)):
            token, tag = phrase[j].split(';')[0:2]
            phrase_tokens.append(token)
            if tag == 'I':
                if j == 0:
                    phrase_tags.append('O')
                else:
                    previous_tag = phrase_tags[-1]
                    regex =  re.search(r'^[BI]-(.*)',previous_tag)
                    if (regex):
                        previous_tag = regex.group(1)
                    phrase_tags.append('I-' + previous_tag)
            else:
                phrase_tags.append('B-' + tag)

        tokens.append(phrase_tokens)
        tags.append(phrase_tags)
    
    examples = {
        "tokens": tokens,
        "tags": tags
    }

    with open("./examples.json", "w") as f:
        json.dump(examples, f)

    sentences = []
    for phrase in examples["tokens"]:
        sentence = " ".join(phrase)
        sentences.append(sentence)
    
    return sentences

def upload_examples():
    file = "examples.json"
    blob = bucket.blob(file)
    blob.upload_from_filename(file)

def upload_paraphrases():
    file = "paraphrases.json"
    blob = bucket.blob(file)
    blob.upload_from_filename(file)


download_training_file()
sentences = process_training_file()
upload_examples()

paraphrases = main.generate_from_gui(sentences,config,pruning=pruning,pivot_level=pivot_level,pre_trained=pre_trained,num_seq=num_seq,compute_metrics=compute_metrics)

paraphrases.pop("metric_score")
with open("./paraphrases.json", "w") as f:
    json.dump(paraphrases, f)

upload_paraphrases() 