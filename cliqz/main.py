import sys
import click
import datetime
import yaml
import os
import random
import json
import requests

CONFIG = {
    "cliqzdex_url": "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/index.yaml",
    "quiz_url": "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/quizzes/",
    "newline": '\n'
}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
QUIZ_DIR = f'{ROOT_DIR}/quizzes/'

def load_config(file_path):
    with open(file_path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        return config

def load_cliqzdex(url):
    response = requests.get(url)
    return response.text

CLIQZDEX = load_cliqzdex(CONFIG['cliqzdex_url'])

@click.group()
@click.version_option("0.1.1")
def main():
    """An open source quiz script"""
    pass

@main.command()
@click.argument('filter', required=False)
def search(filter =""):
    """Search quizes"""
    # print(f"{bcolors.WARNING}Searching in path: {bcolors.ENDC}" + CONFIG['cliqzdex_url'])
    print(get_available_tests(filter))

def get_available_tests(filter=""):
    lines = []
    for index, line in enumerate(CLIQZDEX.splitlines()):
        line = str.replace(line, CONFIG['quiz_url'], "")
        if(len(line) and (not(filter) or filter in line)):
            lines.append(f"{index} {line}")
    return lines

@main.command()
@click.argument('file_name', required=False)
def look_up(file_name):
    """Describe quiz"""
    quiz = get_quiz(file_name)
    print(quiz.description)
    print("Contains " + str(quiz.count) + " items.")
    pass

class Question:
    max_missing = 1
    choose_quantity = 1
    max_options = 5
    max_valid = 2
    valid = None
    title = ""
    type = ""
    choices = []
    false_choices = []
    valid_choices = []
    items_omitted = []
    items_not_omitted = []
    def __init__(self, question):
        self.title = question['title']
        self.type = question['type']
        self.max_missing = question['max_missing'] if 'max_missing' in question else self.max_missing
        self.choose_quantity = question['choose_quantity'] if 'choose_quantity' in question else self.choose_quantity
        self.max_options = question['max_options'] if 'max_options' in question else self.max_options
        self.max_valid = question['max_valid'] if 'max_valid' in question else self.max_valid
        self.valid_choices = random.sample(question['valid_choices'], min([len(question['valid_choices']), self.max_valid]))
        self.false_choices = random.sample(question['false_choices'], min([self.max_options - self.max_valid, len(question['false_choices'])]))

    def get_missing(self):
        """
        missing_items type displays
            - all but one of the valid items in the question
            - the excluded valid_choice plus false_choices in the choices.
        """
        #TODO: Make sure missing item is in choose_items
        items_not_omitted = random.sample(self.valid_choices, len(self.valid_choices))
        items_omitted = items_not_omitted[0]
        items_not_omitted.remove(items_omitted)
        self.items_not_omitted = items_not_omitted
        self.items_omitted = items_omitted
        return items_omitted

    def get_choose(self):
        """
        choose_items type displays
            - Prompt:
            - all the valid items in the choices
            - plus the false_choices in the choices.
        """
        #TODO: Make sure missing item is in choose_items
        items_not_omitted = random.sample(self.valid_choices, len(self.valid_choices))
        omitted_quantity = self.choose_quantity
        items_omitted = items_not_omitted[:omitted_quantity] # Choose qty based on settings.
        # items_not_omitted.remove(items_omitted)
        self.items_not_omitted = items_not_omitted
        self.items_omitted = items_omitted
        return items_omitted


    def get_choices(self):
        """
        select a limited number of randomized valid_choices and combine with randomized false_choices to product max_options number of choices.
        """
        print("Valid choices: ", json.dumps(self.valid_choices))
        print("False choices: ", json.dumps(self.false_choices))
        choice_items = self.false_choices + self.valid_choices
        random_choices = random.sample(choice_items, len(choice_items))
        if(self.type == "missing_item"):
            random_choices = self.get_missing()
        if(self.type == "choose_items"):
            random_choices = self.get_choose()
        return random_choices

    def get_prompt(self):
        """
        properly style and bracket the prompt string.
        """
        choices = '\n'.join(f"{i}: {str(x)}" for i,x in enumerate(self.choices))
        print(f"get_prompt choices: {json.dumps(choices)}")
        if(self.type == "missing_item"):
            question_title = f"{self.title}\n\n{CONFIG['newline'].join(self.items_not_omitted)}"
        else:
            question_title = self.title
        return f"{bcolors.WARNING}{question_title}{bcolors.ENDC}\n\n{choices}\n{bcolors.WARNING}Answer{bcolors.ENDC}"

    def validate(self, response):
        """Handle response validation based on question type"""
        validated = False
        if self.type == "text":
            # The responses are string literals, separated by commas
            response_items = response.split(',')
            print("Response Text Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in self.valid_choices]
            extra_validators = [x for x in self.valid_choices if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        elif self.type == "missing_item":
            response_items = [x for i,x in enumerate(self.choices) if str(i) in response.split(',')]
            # Add remaining valid choices to response to validate.
            # response_items += self.items_not_omitted
            print("Response to Missing Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in self.valid_choices]
            extra_validators = [x for x in self.valid_choices if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        elif self.type == "choose_items":
            #TODO: Wrong number is getting added to choices and response is compared to rull valid_items list.
            response_items = [x for i,x in enumerate(self.choices) if str(i) in response.split(',')]
            print("Response Choose Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in self.items_omitted]
            extra_validators = [x for x in self.items_omitted if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        return validated

class Quiz:
    count = 0
    questions = []
    description = ""
    deadline = None
    index = 0
    max_questions = 10
    def __init__(self, quiz):
        self.count = len(quiz['questions'])
        self.questions = self.get_initial_random_question_set(quiz)
        self.description = quiz['description']
        self.deadline = datetime.datetime.now() + datetime.timedelta(0, 60 * quiz['duration_minutes'])

    def get_initial_random_question_set(self, quiz):
        if 'max_questions' in quiz: self.max_questions = quiz['max_questions']
        random_questions = random.sample(quiz['questions'], min([len(quiz['questions']), self.max_questions]))
        return [Question(question) for question in random_questions]

    def ask_next(self):
        """Ask a single unanswered test question and register the response"""
        questions = [question for question in self.questions if question.valid == None]
        if len(questions) > 0:
            question = questions[0]
            question.choices = question.get_choices()
            prompt = question.get_prompt()
            response = click.prompt(prompt)
            self.index += 1
            validated = question.validate(response)
            if(validated):
                print(f"{bcolors.OKGREEN}CORRECT{bcolors.ENDC}")
                question.valid = True
            else:
                print(f"{bcolors.FAIL}FAIL{bcolors.ENDC}")
                if(question.type in ['choose_items', 'missing_item']):
                    print("Omitted Items: " + json.dumps(question.items_omitted))
                else:
                    print("Valid Items: " + json.dumps(question.valid_choices))
                question.valid = False
            return True
        else:
            return False

def get_quiz(file_name):
    file_path = [line for line in CLIQZDEX.splitlines() if file_name in line][0]
    if(not file_path == None or len(file_path) > 0):
        print(f"Fetching quiz from {file_path}")
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
        outstanding_items = [question for question in quiz.questions if question.valid == None]
        outstanding_count = min([len(outstanding_items), quiz.max_questions - quiz.index])
        t_remaining = str(quiz.deadline - datetime.datetime.now()).split('.')[0]
        print(f"{bcolors.OKBLUE}There are {str(outstanding_count)} items remaining and {t_remaining} time remaining{bcolors.ENDC}.\n")
    valid_answers = [question for question in quiz.questions if question.valid == True]
    percent = len(valid_answers) / len(quiz.questions)
    print(f"{bcolors.OKGREEN}You got {len(valid_answers)} out of {min([len(quiz.questions), quiz.max_questions])} questions.{bcolors.ENDC} Percent: {percent}")
    pass


if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("CliQz -- CLI Quiz")
    main()

