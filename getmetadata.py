import json
import os, os.path
from time import sleep
from urllib2 import urlopen
from urllib import quote_plus

def metadata(id, sleep_time=1):
    solr ="http://chinkapin.pti.indiana.edu:9994/solr/meta/select/?q=id:%s" % id
    solr += "&wt=json" ## retrieve JSON results
    # TODO: exception handling
    if sleep_time:
        sleep(sleep_time) ## JUST TO MAKE SURE WE ARE THROTTLED
    try:
        data = json.load(urlopen(solr))
        print id
        return data['response']['docs'][0]
    except ValueError :
        print "No result found for " + id 
        return dict()

def listsubdirs(path):
    return [p for p in os.listdir(path) 
        if os.path.isdir(os.path.join(path, p))]

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("corpus_path", help="Path to Corpus")
    args = parser.parse_args()

    print os.listdir(args.corpus_path)
    print listsubdirs(args.corpus_path)
    data = [(id.strip(), metadata(id.strip())) 
                for id in listsubdirs(args.corpus_path)]
    data = dict(data)

    metadata_file = os.path.join(args.corpus_path, '../metadata.json')
    with open(metadata_file,'wb') as outfile:
        json.dump(data, outfile)
    
