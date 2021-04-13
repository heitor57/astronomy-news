import pymongo
# import yake
from rake_nltk import Rake
import time
import utils
from keybert import KeyBERT
from nltk.tokenize import word_tokenize
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
num_tasks = 3
domain = open('astronomy_domain.txt').read().split('\n')

news = utils.start_db()

publications = news.publications.find({'keywords':{"$exists":False}}).sort("url",pymongo.DESCENDING)
# publications = news.publications.find({'keywords':{"$exists":False}}).sort("url",pymongo.DESCENDING)
wpm_read_human_mean = 225
model = KeyBERT('distilbert-base-nli-mean-tokens')
auto_abstractor = AutoAbstractor()
# Set tokenizer.
auto_abstractor.tokenizable_doc = SimpleTokenizer()
# Set delimiter for making a list of sentence.
auto_abstractor.delimiter_list = [".", "\n"]
# Object of abstracting and filtering document.
abstractable_doc = TopNRankAbstractor()

# def process(pub, model,auto_abstractor,abstractable_doc):
def process(pub):
    data = dict()
    text = '.\n'.join([pub['title'],pub['description'],pub['body']])
    # rake_nltk_var = Rake(min_length=1, max_length=1)
    # rake_nltk_var.extract_keywords_from_text(text)
    # keyword_extracted = rake_nltk_var.get_ranked_phrases()
    # print(keyword_extracted)
    keywords = model.extract_keywords(text,keyphrase_ngram_range=(1, 1), top_n=20)
    keywords = [i for i in keywords if i[0] in domain]
    keywords_names = [i[0] for i in keywords]
    keywords_scores = [i[1] for i in keywords]
    # data['keywords'] = keywords
    data['keywords_names'] = keywords_names
    data['keywords_scores'] = keywords_scores
    data['keywords'] = keywords
    # data['topic'] = 
    # print(data)
    tokens = word_tokenize(text)
    words = [word for word in tokens if word.isalpha()]
    data['words_num'] = len(words)
    data['read_time'] = len(words)/wpm_read_human_mean
    result_dict = auto_abstractor.summarize(text, abstractable_doc)
    data['resumes'] = result_dict['summarize_result'][:5]
    # print(pub['url'])
    return data
    
for pub in tqdm(publications):
    data = process(pub)
    news.publications.update_one({'url':pub['url']},{"$set":data})

    # futures.add(future)

        # if len(futures) >= num_tasks:
# with ProcessPoolExecutor() as executor:
    # futures = set()
    # for pub in tqdm(publications):
        # # future = executor.submit(process,pub,model,auto_abstractor,abstractable_doc)
        # future = executor.submit(process,pub)

        # futures.add(future)

        # if len(futures) >= num_tasks:
            # completed, futures = wait(futures, return_when=FIRST_COMPLETED)
            # for f in completed:
                # news.publications.update_one({'url':f.result()[0]},{"$set":f.result()[1]})

    # for f in futures:
        # news.publications.update_one({'url':f.result()[0]},{"$set":f.result()[1]})
        # f.result()
        # print(data)
        # break
    # i = 0
    # for future in tqdm(futures):
        # print(i+=1)
