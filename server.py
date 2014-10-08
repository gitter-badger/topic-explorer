import csv
from datetime import datetime, timedelta
from HTMLParser import HTMLParser
import json
import re
from StringIO import StringIO

from vsm.corpus import Corpus
from vsm.model.beaglecomposite import BeagleComposite
from vsm.viewer.beagleviewer import BeagleViewer
from vsm.model.ldacgsmulti import LdaCgsMulti as LCM
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer as LDAViewer
from vsm.extensions.htrc import htrc_label_fn_1315

from bottle import request, response, route, run, static_file

path ='/var/inphosemantics/data/20130101/htrc-anthropomorphism-1315/vsm-data/hathi-1315-nltk-freq3'
lda_c = Corpus.load(path + '.npz')
lda_m = None
lda_v = None
def load_model(k):
    global lda_m, lda_v
    lda_m = LCM.load(path + '-LDA-K%d-500.npz' % k)
    lda_v = LDAViewer(lda_c, lda_m)

def _cache_date(days=1):
    time = datetime.now() + timedelta(days=days)
    return time.strftime("%a, %d %b %Y %I:%M:%S GMT")

@route('/doc_topics/<doc_id>')
def doc_topic_csv(doc_id):
    response.content_type = 'text/csv; charset=UTF8'

    data = lda_v.doc_topics(doc_id)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['topic','prob'])
    writer.writerows([(t, "%6f" % p) for t,p in data])

    return output.getvalue()

@route('/docs/<doc_id>')
def doc_csv(doc_id, threshold=0.2):
    response.content_type = 'text/csv; charset=UTF8'

    data = lda_v.sim_doc_doc(doc_id)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['doc','prob'])
    writer.writerows([(d, "%6f" % p) for d,p in data if p > threshold and d != 'sample.txt'])

    return output.getvalue()

@route('/topics/<topic_no>.json')
def topic_json(topic_no, N=40):
    response.content_type = 'application/json; charset=UTF8'
    try:
        N = int(request.query.n)
    except:
        pass

    if N > 0:
        data = lda_v.dist_top_doc([int(topic_no)])[:N]
    else:
        data = lda_v.dist_top_doc([int(topic_no)])[N:]
        data = reversed(data)
    
    md = lda_c.view_metadata('book')
    ids = md['book_label']
    labels = htrc_label_fn_1315(md)
    label = dict(zip(ids,labels))

    js = []
    for doc, prob in data:
        if doc != 'sample.txt':
            js.append({'doc' : doc, 'label': label[doc], 'prob' : 1-prob,
                'topics' : dict([(str(t), p) for t,p in lda_v.doc_topics(doc)])})

    return json.dumps(js)

@route('/docs_topics/<doc_id>.json')
def doc_topics(doc_id, N=40):
    try:
        N = int(request.query.n)
    except:
        pass

    response.content_type = 'application/json; charset=UTF8'

    if N > 0:
        data = lda_v.dist_doc_doc(doc_id)[:N]
    else:
        data = lda_v.dist_doc_doc(doc_id)[N:]
        data = reversed(data)
    
    md = lda_c.view_metadata('book')
    ids = md['book_label']
    labels = htrc_label_fn_1315(md)
    label = dict(zip(ids,labels))

    js = []
    for doc, prob in data:
        if doc != 'sample.txt':
            js.append({'doc' : doc, 'label': label[doc], 'prob' : 1-prob,
                'topics' : dict([(str(t), p) for t,p in lda_v.doc_topics(doc)])})

    return json.dumps(js)

@route('/topics.json')
def topics():
    response.content_type = 'application/json; charset=UTF8'
    response.set_header('Expires', _cache_date())

    data = lda_v.topics()

    js ={} 
    for i,topic in enumerate(data):
        for word, prob in topic[:10]:
            js.update({str(i) : dict([(w, p) for w,p in topic[:10]])})

    return json.dumps(js)

@route('/docs.json')
def docs():
    response.content_type = 'application/json; charset=UTF8'
    response.set_header('Expires', _cache_date())

    md = lda_c.view_metadata('book')
    ids = md['book_label']
    labels = htrc_label_fn_1315(md)
    label = dict(zip(ids,labels))

    js = list()
    for id in ids:
        js.append({
            'id': id,
            'label' : labels.get(id, id)
        })

    return json.dumps(js)


@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='www/')

@route('/')
def index():
    return send_static('index.html')

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('k', type=int)
    parser.add_argument('-p', dest='port', type=int, 
        help="Port Number", default=None)
    args = parser.parse_args()

    if args.port is None: 
        port = '17%03d' % (args.k)
    else:
        port = args.port

    load_model(args.k)
    run(host='0.0.0.0', port=port)

