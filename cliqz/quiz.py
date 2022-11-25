import datetime
import random
import click
import json
from cliqz.question import Question
from cliqz.bcolors import bcolors


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
            prompt = question.get_prompt(question.choices)
            response = click.prompt(prompt)
            self.index += 1
            validated = question.validate(response, question.choices)
            if(validated):
                print(f"{bcolors.OKGREEN}CORRECT{bcolors.ENDC}")
                question.valid = True
            else:
                print(f"{bcolors.FAIL}FAIL{bcolors.ENDC}")
                if(question.type in ['choose_items', 'missing_item']):
                    print("Valid Items: " + json.dumps(question.items_omitted))
                else:
                    print("Valid Items: " + json.dumps(question.valid_choices))
                question.valid = False
            return True
        else:
            return False
