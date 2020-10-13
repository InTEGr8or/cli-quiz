CLIQZDEX_URL = "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/index.yaml"
quiz_url = "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/quizzes/"
default_max_questions = 10

CONFIG = {
    "cliqzdex_url": "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/index.yaml",
    "quiz_url": "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/quizzes/",
    "newline": '\n'
}

cliqdex_url_array = CONFIG['cliqzdex_url'].split('/')
del cliqdex_url_array[-1]
CLIQZDEX_REPLACE = '/'.join(cliqdex_url_array)
CLIQZDEX_REPLACE = CONFIG['quiz_url']

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

