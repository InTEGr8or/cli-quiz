import click
import cliqz
from click.testing import CliRunner

runner = CliRunner()

MISSING_FALSE = {
        "title": "False Choices",
        "type": "missing_items",
        "false_choices": [
            "false_choice_1",
            "false_choice_2"
        ],
        "valid_choices": [
            "valid_choice_1",
            "valid_choice_2"
        ]
    }

def test_false_choices():
    #TODO: instantiate the Quiz object using pytest best practices.
    response = cliqz.Quiz.get_false_choices(MISSING_FALSE)
    assert True

def test_search():
    response = runner.invoke(cliqz.search, "pract")
    assert(response.exit_code == 0)
    assert("https://" in response.output)

#TODO: OK, now write tests to hand the choose_items, omitted_items and stuff. Make it check that the numbers add right.

def test_available_tests(capsys):
    response = cliqz.get_available_tests('pract')
    assert(len(response) > 0)
    assert("https" in response[0])

def test_test(capsys):
    cliqz.test_test()
    out, err = capsys.readouterr()
    assert(out == "test success\n")
    assert(err == '')

def test_look_up():
    assert(cliqz.look_up)

def test_other():
    assert(cliqz.search)
