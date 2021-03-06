import logging
import socket
import os


LOG_PATH = "log/experiment.log"

configs = [i.replace("\n", "") for i in open(".rookie.pwd", "r")]

ROOKIE_USER = [i.split("=")[1] for i in configs if "USER" in i].pop()
ROOKIE_PW = [i.split("=")[1] for i in configs if "PASSWORD" in i].pop()
IP = [i.split("=")[1] for i in configs if "IP" in i].pop()

# http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
if socket.gethostname() == "dewey":
    CORPUS_LOC = "data/lens_processed/"
    IP = "localhost"
    PG_HOST = "localhost"
    ROOKIE_JS = "static/js/"
    ROOKIE_CSS = "static/css/"
    BASE_URL = "/"
    files_location = "/Users/ahandler/research/rookie/"
    processed_location = "/Users/ahandler/research/rookie/lens_processed"
elif socket.gethostname() == "hobbes":
    BASE_URL = "/"
    CORPUS_LOC = "/home/ubuntu/data/lens_processed/"
    IP = IP # read from config file
    ROOKIE_JS = "https://s3-us-west-2.amazonaws.com/rookie2/js/"
    ROOKIE_CSS = "https://s3-us-west-2.amazonaws.com/rookie2/css/"
    PG_HOST = os.environ.get('PG_PORT_5432_TCP_ADDR','localhost')


if 'btop2' in socket.gethostname():
    server_port=8000
    core_nlp_location = None
    corpus_loc = None
    files_location = None
    processed_location = None
    tagger_base = None
    window_length = 30


CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
     ROOKIE_USER,
     ROOKIE_PW, # pw
     PG_HOST,
     'rookie', # db
)

SAVEMODE = False


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

filehandler = logging.FileHandler(LOG_PATH)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
