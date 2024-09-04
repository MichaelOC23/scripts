from transformers import AutoTokenizer, TFBertForTokenClassification #, TFAutoModelForTokenClassification
from transformers import pipeline
import json


tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = TFBertForTokenClassification.from_pretrained("dslim/bert-base-NER")

with open('/Users/michasmi/code/mytech/docker/ListGen/scrapes/moonsail.json', 'r') as f:
    data = json.load(f)



# nlp = pipeline("ner", model=model, tokenizer=tokenizer)
# example = "My name is Wolfgang and I live in Berlin"
# ner_results = nlp(example)


# def print_ner_results(ner_results):
#     for ner_dict in ner_results:
#         ner_dict_str = f"{ner_dict.get('word', 'NO-WORD-VALUE')} ({ner_dict.get('entity', 'NO-ENTITY-VALUE')} | {ner_dict.get('score', 'NO-SCORE-VALUE')})"
#         print(ner_dict_str)

# print_ner_results(ner_results=ner_results)
# pass
# # example = "My name is Wolfgang and I live in Berlin"


tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = TFBertForTokenClassification.from_pretrained("dslim/bert-base-NER")


def get_entities_bert_slim(text_to_analyzie):
    def print_ner_results(ner_results):
        for ner_dict in ner_results:
            ner_dict_str = f"{ner_dict.get('word', 'NO-WORD-VALUE')} ({ner_dict.get('entity', 'NO-ENTITY-VALUE')} | {ner_dict.get('score', 'NO-SCORE-VALUE')})"
            print(ner_dict_str)
    
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    ner_results = nlp(text_to_analyzie)
    print_ner_results(ner_results=ner_results)
    return ner_results

text = "My name is Wolfgang and I live in Berlin"
ner_results = get_entities_bert_slim(text)
pass

    

# print(ner_results)
# with open('ner_results.json', 'w') as f:
#     json.dump'ner_results, f)