import os

#JSON paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.normpath(os.path.join(BASE_DIR, "../json"))

DATA_FILE     = os.path.join(JSON_DIR, "data.json")
COMPLETE_DATA = os.path.join(JSON_DIR, "complete_data.json")

#Thabella
THABELLA_BACKEND_MAIN_URL = "https://thabella.th-deg.de/thabella/opn/period/findByDate/"
THABELLA_PERIOD_LIST = "https://thabella.th-deg.de/thabella/opn/period/list"
