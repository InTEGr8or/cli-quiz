from cliqz.question import Question
import cliqz
from click.testing import CliRunner
import json
import pytest_mock

runner = CliRunner()

BASE = {
        "title": "Baseline Choices",
        "false_choices": [
            "false_choice_1",
            "false_choice_2",
            "false_choice_3",
            "false_choice_4",
        ],
        "type": "missing_item",
        "valid_choices": [
            "valid_choice_1",
            "valid_choice_2",
            "valid_choice_3",
            "valid_choice_4",
            "valid_choice_5"
        ],

    }

# BASE, but with too few false choices, expecting fewer results
MISSING_FALSE = {**BASE, **{"title": "missing false-choices", "type":"missing_item", "false_choices": BASE['false_choices'][:2]}, "test_results": 3}
MISSING_FALSE_VALID_1 = {**BASE, **{"max_valid": 1, "false_choices": BASE['false_choices'][:2], "test_results": 3}}

def test_false_choices(mocker):
    qz = MISSING_FALSE
    question = Question(qz)
    assert(len(question.choices) == qz['test_results'])

def test_get_prompt():
    qz = BASE
    question = Question(qz)
    prompt = question.get_prompt(question.choices)
    assert(len(prompt.split('\n')) > 2 and len(prompt.split('\n')) < 25)

def test_get_missing():
    qz = BASE
    question = Question(qz)
    missing = question.get_missing()
    assert(len(missing) == question.max_options)

def test_get_choose():
    qz = BASE
    question = Question(qz)
    choose = question.get_missing()
    assert(len(choose) == question.max_options)

def test_reduced_max_valid():
    qz = MISSING_FALSE_VALID_1
    question = Question(qz)
    assert(len(question.choices) == qz['test_results'])
def test_validation():
    qz = BASE
    question = Question(qz)
    response = ",".join([str(i) for i,x in enumerate(question.choices) if x in question.items_omitted])
    assert(question.validate(response, question.choices))

def test_search():
    response = runner.invoke(cliqz.search, "pract")
    assert(response.exit_code == 0)
    assert("https://" in response.output)

#TODO: OK, now write tests to hand the choose_items, omitted_items and stuff. Make it check that the numbers add right.

def test_available_tests(capsys):
    response = cliqz.get_available_tests('pract')
    assert(len(response) > 0)
    assert("https" in response[0])

def test_test():
    question = Question(MISSING_FALSE)
    assert(question.valid == None)

def test_look_up():
    assert(cliqz.look_up)

def test_other():
    assert(cliqz.search)
