import os
import os.path
# Change working directory so relative paths (and template lookup) work again
print __file__
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import bottle
import topicexplorer.server
from argparse import Namespace
args = Namespace()
args.config = 'ap.ini'
args.k = 20
args.port = None
args.host = None
args.ssl = False
args.certfile = None
args.keyfile = None
args.ca_certs = None
args.daemon = True
topicexplorer.server.main(args)


# Do NOT use bottle.run() with mod_wsgi
application = bottle.default_app()
