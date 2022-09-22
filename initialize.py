from google.cloud import storage
#import main

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
    file = "training.json"
    blob = bucket.blob(file)
    blob.download_to_filename(file)

def process_training_file():
    import json
    with open("./training.json", "r") as f:
        data = json.load(f)["measures"]

    tokens = []
    tags = []

    for phrase in data:
        phrase_tokens = []
        phrase_tags = []
        for word in phrase:
            if word["value"] != " ":
                splits = word["value"].split(" ")
                splits = [w for w in splits if w != ""]
                if word["type"] == "Text":
                    for split in splits:
                        phrase_tokens.append(split)
                        phrase_tags.append("O")
                else:
                    tag = word["slot"]
                    tag = "AggFunction" if tag == "AGRCount" or tag == "AGR" else tag
                    tag = "CCI" if tag == "CCIData" else tag
                    tag = "AttributeValue" if tag == "AttributeValueData" else tag
                    for i in range(len(splits)):
                        if i == 0:
                            phrase_tokens.append(splits[i])
                            phrase_tags.append("B-"+tag)
                        else:
                            phrase_tokens.append(splits[i])
                            phrase_tags.append("I-"+tag)
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

def save_examples():
    file = "examples.json"
    blob = bucket.blob(file)
    blob.upload_from_filename(file)

def save_paraphrases(sentences):
    file = "paraphrases.txt"
    blob = bucket.blob(file)
    blob.upload_from_string(sentences)

download_training_file()
sentences = process_training_file()
save_examples()

#paraphrases = main.generate_from_gui(sentences,config,pruning=pruning,pivot_level=pivot_level,pre_trained=pre_trained,num_seq=num_seq,compute_metrics=compute_metrics)
save_paraphrases(paraphrases)