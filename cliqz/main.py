from cliqz.quiz import Quiz
from cliqz.bcolors import bcolors
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
    print(f"{bcolors.OKGREEN}You got {len(valid_answers)} out of {min([len(quiz.questions), quiz.max_questions])} questions.{bcolors.ENDC} Grade: {int(percent * 100)}%")
    pass


if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("CliQz -- CLI Quiz")
    main()

