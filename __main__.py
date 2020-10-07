import sys
import click
import datetime
import yaml
import os
import random
import json

# missing_items type displays all but one of the valid items in the question, and the excluded valid_item plus choose_items in the choices.
# choose_items type displays all the valid items plus the choose_items in the choices.

@click.group()
@click.version_option("1.0.0")
def main():
    """An open source quiz script"""
    pass

@main.command()
@click.argument('filter', required=False)
def search(filter):
    """Search quizes"""
    for subdir, dirs, files in os.walk('./quizes/'):
        for file in files:
            if(".yaml" in file or ".yml" in file):
                print(file)
    pass

@main.command()
@click.argument('file_name', required=False)
def look_up(file_name):
    """Describe quiz"""
    quiz = get_quiz(file_name)
    print(quiz.description)
    print("Contains " + str(quiz.count) + " items.")
    pass

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
            self.questions[i]['prompt'] = self.questions[i]['title'] + '\n' + '\n'.join(str(x) for x in self.questions[i]['choose_items'])
        pass

    def ask_next(self):
        """Ask a single unanswered test question and register the response"""
        questions = [question for question in self.questions if question['valid'] == None]
        if len(questions) > 0:
            question = questions[0]
            response = click.prompt(question['prompt'])
            print("Response: " + response)
            print("Valid Items: " + json.dumps(question['valid_items']))
            question['valid'] = True
            return True
        else:
            return False

def get_quiz(file_name):
    file_path = os.getcwd() + os.sep + "quizes" + os.sep + file_name
    if(os.path.isfile(file_path)):
        with open(file_path) as file:
            quiz = Quiz(yaml.load(file, Loader=yaml.FullLoader))
            return quiz
    else:
        click.echo("Quiz file not found")

@main.command()
@click.argument('file_name', required=True)
def take(file_name):
    """Take a quiz"""
    quiz = get_quiz(file_name)
    while quiz.ask_next():
        outstanding_items = [question for question in quiz.questions if question['valid'] == None]
        print("There are " + str(len(outstanding_items)) + " items remaining and due by " + quiz.deadline.strftime("%H:%M:%S") + '\n')

if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("LiveTest")
    main()


