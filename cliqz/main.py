import sys
import click
import datetime
import yaml
import os
import random
import json
import requests
# import cliqz.configuration


# missing_items type displays all but one of the valid items in the question, and the excluded valid_choice plus false_choices in the choices.
# choose_items type displays all the valid items plus the false_choices in the choices.

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
QUIZ_DIR = f'{ROOT_DIR}/quizzes/'


def load_config(file_path):
    with open(file_path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        return config

def load_cliqzdex(url):
    response = requests.get(url)
    return response.text

CONFIG = {
    "cliqzdex_url": "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/index.yaml",
    "quiz_url": "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/quizzes/"
}

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
        line =str.replace(line, CLIQZDEX_REPLACE, "")
        if(len(line)):
            print(index, line)
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
    index = 0
    max_questions = 200
    max_missing = 1
    max_choose = 1
    def __init__(self, quiz):
        self.count = len(quiz['questions'])
        if 'max_questions' in quiz: self.max_questions = quiz['max_questions']
        self.questions = random.sample(quiz['questions'], len(quiz['questions']))
        self.description = quiz['description']
        self.deadline = datetime.datetime.now() + datetime.timedelta(0, 60 * quiz['duration_minutes'])
        for i in range(self.count):
            self.questions[i]['valid'] = None
        pass

    def get_choices(self, question):
        # Get numbered list of options
        # TODO: Make change by question type
        if('false_choices' not in question): return ""
        choice_items = question['false_choices']

        # leaving randomization of valid_choices in for now, pending implementation of select_valid_count
        choice_items += random.sample(question['valid_choices'], len(question['valid_choices']))
        random_choices = random.sample(choice_items, len(choice_items))

        return random_choices

    def get_prompt(self, question):
        choices = '\n'.join(f"{i}: {str(x)}" for i,x in enumerate(question['choices']))
        if(question['type'] == "missing_item"):
            question_title = f"{question['title']}\n{random.sample(question['valid_choices'], len(question['valid_choices']) - 1)}"
        else:
            question_title = question['title']
        return f"{bcolors.WARNING}{question_title}{bcolors.ENDC}\n\n{choices}\n{bcolors.WARNING}Answer{bcolors.ENDC}"

    def validate(self, question, response):
        """Handle response validation based on question type"""
        #TODO: If ask_next inserts one valid answer, how does validate() know which one is valid?
        validated = False
        if question['type'] == "text":
            response_items = response.split(',')
            print("Response Text Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in question['valid_choices']]
            extra_validators = [x for x in question['valid_choices'] if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        elif question['type'] == "missing_item":
            response_items = [x for i,x in enumerate(question['choices']) if str(i) in response.split(',')]
            response_items += question['valid_choices']
            print("Response Missing Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in question['valid_choices']]
            extra_validators = [x for x in question['valid_choices'] if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        elif question['type'] == "choose_items":
            response_items = [x for i,x in enumerate(question['choices']) if str(i) in response.split(',')]
            print("Response Choose Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in question['valid_choices']]
            extra_validators = [x for x in question['valid_choices'] if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        return validated

    def ask_next(self):
        """Ask a single unanswered test question and register the response"""
        questions = [question for question in self.questions if question['valid'] == None]
        if len(questions) > 0 and self.index < self.max_questions:
            question = questions[0]
            question['choices'] = self.get_choices(question)
            prompt = self.get_prompt(question)
            response = click.prompt(prompt)
            self.index += 1
            validated = self.validate(question, response)
            if(validated):
                print(f"{bcolors.OKGREEN}CORRECT{bcolors.ENDC}")
                question['valid'] = True
            else:
                print(f"{bcolors.FAIL}FAIL{bcolors.ENDC}")
                print("Valid Items: " + json.dumps(question['valid_choices']))
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
        outstanding_count = min([len(outstanding_items), quiz.max_questions - quiz.index])
        t_remaining = str(quiz.deadline - datetime.datetime.now()).split('.')[0]
        print(f"{bcolors.OKBLUE}There are {str(outstanding_count)} items remaining and {t_remaining} time remaining{bcolors.ENDC}.\n")
    valid_answers = [question for question in quiz.questions if question['valid'] == True]
    percent = len(valid_answers) / len(quiz.questions)
    print(f"{bcolors.OKGREEN}You got {len(valid_answers)} out of {min([len(quiz.questions), quiz.max_questions])} questions.{bcolors.ENDC} Percent: {percent}")

if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("LiveTest")
    main()


