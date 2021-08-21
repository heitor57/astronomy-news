import utils
from tqdm import tqdm

news = utils.start_db()

publications = news.publications.find()

def process(pub):
    data = dict()
    data['keywords_names_n'] = ' '.join(pub['keywords_names'])
    data['keywords_scores_n'] = ' '.join(map(str,pub['keywords_scores']))
    data['keywords_names_t1'] = pub['keywords_names'][0]
    data['keywords_scores_t1'] = pub['keywords_scores'][0]
    return data
    
for pub in tqdm(publications):
    if len(pub['keywords_names'])>0:
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
