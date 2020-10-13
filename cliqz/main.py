import sys
import click
import datetime
import yaml
import os
import random
import json
import requests
from cliqz.configuration import CONFIG
from cliqz.configuration import bcolors


# missing_items type displays all but one of the valid items in the question, and the excluded valid_choice plus false_choices in the choices.
# choose_items type displays all the valid items plus the false_choices in the choices.

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
QUIZ_DIR = f'{ROOT_DIR}/quizzes/'

def test_test():
    print("test success")

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
def search(filter = ""):
    """Search quizes"""
    # print(f"{bcolors.WARNING}Searching in path: {bcolors.ENDC}" + CONFIG['cliqzdex_url'])
    print(get_available_tests(filter))

def get_available_tests(filter):
    lines = []
    for index, line in enumerate(CLIQZDEX.splitlines()):
        line = str.replace(line, CONFIG['quiz_url'], "")
        if(len(line) and filter in line):
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

class Quiz:
    count = 0
    questions = []
    description = ""
    deadline = None
    index = 0
    max_questions = 10
    max_missing = 1
    choose_quantity = 1
    max_options = 5
    max_valid = 2
    def __init__(self, quiz):
        self.count = len(quiz['questions'])
        self.questions = self.get_random_questions(quiz)
        self.description = quiz['description']
        self.deadline = datetime.datetime.now() + datetime.timedelta(0, 60 * quiz['duration_minutes'])
        for i in range(self.count):
            self.questions[i]['valid'] = None
        pass

    def get_random_questions(self, quiz):
        if 'max_questions' in quiz: self.max_questions = quiz['max_questions']
        return random.sample(quiz['questions'], min([len(quiz['questions']), self.max_questions]))

    def get_false_choices(self, question):
        """
        Get enough false_choices to add up with valid_choices to make max_choices
        """
        max_valid = min([len(question['valid_choices']), self.max_valid])
        max_false_choices = min([self.max_options - max_valid, len(question['false_choices'])])
        false_choices = random.sample(question['false_choices'], max_false_choices)
        return false_choices

    def get_valid_choices(self, question):
        """
        Get up to max_valid of available valid choices
        """
        max_valid = min([len(question['valid_choices']), self.max_valid])
        return random.sample(question['valid_choices'], max_valid)

    def get_choices(self, question):
        """
        select a limited number of randomized valid_choices and combine with randomized false_choices to product max_options number of choices.
        """
        if('false_choices' not in question): return ""
        choice_items = self.get_false_choices(question) + self.get_valid_choices(question)
        random_choices = random.sample(choice_items, len(choice_items))
        if(question['type'] == "missing_item"):
            #TODO: Make sure missing item is in choose_items
            items_not_omitted = random.sample(question['valid_choices'], len(question['valid_choices']))
            items_omitted = items_not_omitted[0]
            items_not_omitted.remove(items_omitted)
            question['items_not_omitted'] = items_not_omitted
            question['items_omitted'] = items_omitted
            random_choices = items_omitted
        if(question['type'] == "choose_items"):
            #TODO: Make sure missing item is in choose_items
            items_not_omitted = random.sample(question['valid_choices'], len(question['valid_choices']))
            omitted_quantity = question['choose_quantity'] if('choose_quantity' in question) else self.choose_quantity
            items_omitted = items_not_omitted[:omitted_quantity] # Choose qty based on settings.
            # items_not_omitted.remove(items_omitted)
            question['items_not_omitted'] = items_not_omitted
            question['items_omitted'] = items_omitted
            random_choices = items_omitted
        return random_choices

    def get_prompt(self, question):
        """
        properly style and bracket the prompt string.
        """
        choices = '\n'.join(f"{i}: {str(x)}" for i,x in enumerate(question['choices']))
        if(question['type'] == "missing_item"):
            question_title = f"{question['title']}\n\n{CONFIG['newline'].join(question['items_not_omitted'])}"
        else:
            question_title = question['title']
        return f"{bcolors.WARNING}{question_title}{bcolors.ENDC}\n\n{choices}\n{bcolors.WARNING}Answer{bcolors.ENDC}"

    def validate(self, question, response):
        """Handle response validation based on question type"""
        validated = False
        if question['type'] == "text":
            # The responses are string literals, separated by commas
            response_items = response.split(',')
            print("Response Text Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in question['valid_choices']]
            extra_validators = [x for x in question['valid_choices'] if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        elif question['type'] == "missing_item":
            response_items = [x for i,x in enumerate(question['choices']) if str(i) in response.split(',')]
            # Add remaining valid choices to response to validate.
            # response_items += question['items_not_omitted']
            print("Response to Missing Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in question['valid_choices']]
            extra_validators = [x for x in question['valid_choices'] if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        elif question['type'] == "choose_items":
            #TODO: Wrong number is getting added to choices and response is compared to rull valid_items list.
            response_items = [x for i,x in enumerate(question['choices']) if str(i) in response.split(',')]
            print("Response Choose Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in question['items_omitted']]
            extra_validators = [x for x in question['items_omitted'] if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        return validated

    def ask_next(self):
        """Ask a single unanswered test question and register the response"""
        questions = [question for question in self.questions if question['valid'] == None]
        if len(questions) > 0:
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
                if(question['type'] in ['choose_items', 'missing_item']):
                    print("Omitted Items: " + json.dumps(question['items_omitted']))
                else:
                    print("Valid Items: " + json.dumps(question['valid_choices']))
                question['valid'] = False
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
        print("CliQz -- CLI Quiz")
    main()


