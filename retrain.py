import multiprocessing
import os.path
import sys

from vsm.corpus import Corpus
from vsm.model.ldacgsmulti import LdaCgsMulti as LDA

import train

def continue_training(corpus_filename, model_path, krange, old_iterations=200,
                      new_iterations=100, n_proc=2):

    corpus = Corpus.load(corpus_filename)
    if 'book' in corpus.context_types:
        corpus_type = 'book'
    else:
        corpus_type = 'document'

    basefilename = os.path.basename(corpus_filename).replace('.npz','')
    basefilename += "-LDA-K%s-%s-%s.npz" % ('{k}', corpus_type,'{iter}')
    basefilename = os.path.join(model_path, basefilename)


    for k in krange:
        print "Training model for k={0} Topics".format(k)
        m = LDA.load(basefilename.format(k=k, iter=old_iterations))
        m.train(n_iterations=new_iterations, n_proc=n_proc)
        m.save(basefilename.format(k=k, iter=new_iterations))

    return basefilename

if __name__ == '__main__':
    from argparse import ArgumentParser
    from ConfigParser import RawConfigParser as ConfigParser
    parser = ArgumentParser()
    parser.add_argument("model_path",
        help="Model Path [Default: [corpus_path]/../models]")
    """
    parser.add_argument("--restart", action=store_true,
        help="Restart training")
    parser.add_argument("-c", "--continue", action=store_true,
        help="Continue last training")
    """
    parser.add_argument("-p", "--processes", default=-2, type=int,
        help="Number of CPU cores for training [Default: total - 2]")
    parser.add_argument("-k", nargs='+',
        help="K values to train upon", type=int)
    parser.add_argument('--iter', type=int,
        help="Number of training iterations")
    args = parser.parse_args()
    
    args.model_path = os.path.abspath(args.model_path)
    if not os.path.exists(args.model_path):
        print "ERROR: invalid path, please specify a valid corpus file"
        sys.exit(74)

    if args.k is None:
        args.k = range(120,0,-20)
    
    if args.iter is None:
        while args.iter is None:
            iters = raw_input("Number of Training Iterations [Default 200]: ")
            try:
                args.iter = int(iters)
            except ValueError:
                if iters.strip() == '':
                    args.iter = 200
                else:
                    print "Enter a valid integer!"

        print "\nTIP: number of training iterations can be specified with argument '--iter N':"
        print "python retrain.py --iter %d %s\n" % (args.iter, args.model_path)

    if args.processes < 0:
        args.processes = multiprocessing.cpu_count() + args.processes

    dirname = os.path.dirname(args.model_path)
    try:
        train.build_models(args.model_path, dirname, args.k,
                           n_iterations=args.iter, n_proc=args.processes)
    except IOError:
        print "ERROR: invalid path, please specify a valid corpus file"
        sys.exit(74)
    """
    if args.mode == 'restart':
        try:
            train.build_models(args.model_path, dirname, args.k,
                               n_iterations=args.iter, n_proc=args.processes)
        except IOError:
            print "ERROR: invalid path, please specify a valid corpus file"
            sys.exit(74)
    elif args.mode == 'continue':
        try:
            conitnue_training(args.model_path, dirname, args.k,
                              new_iterations=args.iter, n_proc=args.processes)
        except IOError:
            print "ERROR: invalid path, please specify a valid corpus file"
            sys.exit(74)
    else:
        print "Enter a valid mode: restart, continue"
    """
