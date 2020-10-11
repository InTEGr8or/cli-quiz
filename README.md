# Cliqz Intro

I wanted to knock this out in a day to solve a problem I had no time budgeted for. Python was the perfect option but I'm a n00b to it, so be cruel.

The other quizzes I use, like Anki-droid and Udemy quizzes are not open-source-ish enough. There is some difficulty adding question sets and types. I want questions in a data format that is more verifiable and standard.

We all need to learn, so maybe we can learn to trade our learning and the product of our learning.

## Inspiration

I was inspired yesterday by this article: [How to Build And Publish Command-Line Applications With Python](https://towardsdatascience.com/how-to-build-and-publish-command-line-applications-with-python-96065049abc1)

## Quiz Schema

The Quiz structure is starting to look like this:

```yaml
description: string
duration_minutes: number
questions:
- item:
  title: string
  type: [missing_items choose_items]
  false_choices: [text_string_one text_string_two text_string_three]
  valid_choices: [text_string_one]
  notes: >
    Multiline text
```


## Roadmap

* [X] ~~*Colorize questions*~~ [2020-10-06]
* [X] ~~*Minutes left instead of a deadline*~~ [2020-10-06]
* [X] ~~*Validate and register answer results.*~~ [2020-10-06]
* [X] ~~*Allow select by answer number or letter.*~~ [2020-10-07]
* [X] ~~*Tally a list of results at the end of the test.*~~ [2020-10-07]
* [ ] Add code tests to the project
* [ ] Add several quizzes and expand questions.
* [X] ~~*Move quizzes into an open-source repo of some modern type.*~~ [2020-10-08]
* [ ] Variation in handling of various test types not property implemented for missing_item.

<!-- ```ps1
pip install -e ./


rm build/*; rm cliqz.egg-info/*; rm dist/*;
python setup.py sdist bdist_wheel
python -m twine upload dist/*
``` -->
