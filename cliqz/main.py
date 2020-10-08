import sys
import click
import datetime
import yaml
import os
import random
import json
import requests

# missing_items type displays all but one of the valid items in the question, and the excluded valid_item plus choose_items in the choices.
# choose_items type displays all the valid items plus the choose_items in the choices.

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
QUIZ_DIR = f'{ROOT_DIR}/quizzes/'


def load_config(file_path):
    with open(file_path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        return config

def load_cliqzdex(url):
    response = requests.get(url)
    return response.text

CONFIG = load_config(f'{ROOT_DIR}/configuration.yaml')
CLIQZDEX = load_cliqzdex(CONFIG['cliqzdex_url'])
cliqdex_url_array = CONFIG['cliqzdex_url'].split('/')
del cliqdex_url_array[-1]
CLIQZDEX_REPLACE = '/'.join(cliqdex_url_array)
CLIQZDEX_REPLACE = CONFIG['quiz_url']


@click.group()
@click.version_option("0.1.1")
def main():
    """An open source quiz script"""
    pass

@main.command()
@click.argument('filter', required=False)
def search(filter):
    """Search quizes"""
    print(f"{bcolors.WARNING}Searching in path: {bcolors.ENDC}" + CONFIG['cliqzdex_url'])
    for index, line in enumerate(CLIQZDEX.splitlines()):
        print(index, str.replace(line, CLIQZDEX_REPLACE, ""))

    pass

@main.command()
@click.argument('file_name', required=False)
def look_up(file_name):
    """Describe quiz"""
    quiz = get_quiz(file_name)
    print(quiz.description)
    print("Contains " + str(quiz.count) + " items.")
    pass

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Quiz:
    count = 0
    questions = []
    description = ""
    deadline = None
    def __init__(self, quiz):
        self.count = len(quiz['questions'])
        self.questions = random.sample(quiz['questions'], len(quiz['questions']))
        self.description = quiz['description']
        self.deadline = datetime.datetime.now() + datetime.timedelta(0, 60 * quiz['duration_minutes'])
        for i in range(self.count):
            self.questions[i]['valid'] = None
            if('choose_items' in self.questions[i]):
                choose_items = '\n'.join(f"{i}: {str(x)}" for i,x in enumerate(self.questions[i]['choose_items']))
            else:
                choose_items = ""
            self.questions[i]['prompt'] = self.create_prompt(self.questions[i], choose_items)
        pass

    def create_prompt(self, question, choose_items):
        prompt = ""
        prompt = f"{bcolors.WARNING}{question['title']}{bcolors.ENDC}\n\n{choose_items}\n{bcolors.WARNING}Answer{bcolors.ENDC}"
        return prompt

    def validate(self, question, response):
        """Handle response validation based on question type"""
        validated = False
        if question['type'] == "text":
            response_items = response.split(',')
            print("Response Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in question['valid_items']]
            extra_validators = [x for x in question['valid_items'] if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        elif question['type'] == "missing_item":
            response_items = [x for i,x in enumerate(question['choose_items']) if str(i) in response.split(',')]
            print("Response Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in question['valid_items']]
            extra_validators = [x for x in question['valid_items'] if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        elif question['type'] == "choose_items":
            response_items = [x for i,x in enumerate(question['choose_items']) if str(i) in response.split(',')]
            print("Response Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in question['valid_items']]
            extra_validators = [x for x in question['valid_items'] if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        return validated

    def ask_next(self):
        """Ask a single unanswered test question and register the response"""
        questions = [question for question in self.questions if question['valid'] == None]
        if len(questions) > 0:
            question = questions[0]
            response = click.prompt(question['prompt'])
            validated = self.validate(question, response)
            if(validated):
                print(f"{bcolors.OKGREEN}CORRECT{bcolors.ENDC}")
                question['valid'] = True
            else:
                print(f"{bcolors.FAIL}FAIL{bcolors.ENDC}")
                print("Valid Items: " + json.dumps(question['valid_items']))
                question['valid'] = False
            return True
        else:
            return False

def get_quiz(file_name):
    file_path = [line for line in CLIQZDEX.splitlines() if file_name in line][0]
    if(not file_path == None or len(file_path) > 0):
        quiz_yaml = requests.get(file_path).text
        quiz = Quiz(yaml.load(quiz_yaml, Loader=yaml.FullLoader))
        return quiz
    else:
        click.echo(f"{bcolors.FAIL}Quiz file not found:{bcolors.ENDC} {file_name}")
        sys.exit()

@main.command()
@click.argument('file_name', required=True)
def take(file_name):
    """Take a quiz"""
    quiz = get_quiz(file_name)
    while quiz.ask_next():
        outstanding_items = [question for question in quiz.questions if question['valid'] == None]
        t_remaining = str(quiz.deadline - datetime.datetime.now()).split('.')[0]
        print(f"{bcolors.OKBLUE}There are {str(len(outstanding_items))} items remaining and {t_remaining} time remaining{bcolors.ENDC}.\n")
    valid_answers = [question for question in quiz.questions if question['valid'] == True]
    percent = len(valid_answers) / len(quiz.questions)
    print(f"{bcolors.OKGREEN}You got {len(valid_answers)} out of {len(quiz.questions)} questions.{bcolors.ENDC} Percent: {percent}")

if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("LiveTest")
    main()


