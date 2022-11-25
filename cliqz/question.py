import random
import json
from cliqz.bcolors import bcolors

CONFIG = {
    "cliqzdex_url": "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/index.yaml",
    "quiz_url": "https://raw.githubusercontent.com/InTEGr8or/cliqzdex/main/quizzes/",
    "newline": '\n'
}
QUESTION_TYPE = [
    "missing_item",
    "choose_items",
    "text"
]

class Question:
    max_missing = 1 # the maximum number of items to omit from the missing_item type of test.
    choose_quantity = 1 # the number of items to be selected
    max_options = 5 
    max_valid = 2 # maximum number of valid choices to be included in the list of choices
    valid = None
    title = ""
    type = ""
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
        self.valid_choices = self.__get_valid_choices(question) 
        self.false_choices = self.__get_false_choices(question) 
        self.choices = self.__get_choices()

    def __get_false_choices(self, question):
        if(not 'false_choices' in question): return []
        result = random.sample(question['false_choices'], min([self.max_options - self.max_valid, len(question['false_choices'])]))
        return result

    def __get_valid_choices(self, question):
        result = random.sample(question['valid_choices'], min([len(question['valid_choices']), self.max_valid]))
        return result

    def __get_choices(self):
        """
        select a limited number of randomized valid_choices and combine with randomized false_choices to product max_options number of choices.
        """
        choice_items = self.false_choices + self.valid_choices
        random_choices = random.sample(choice_items, len(choice_items))
        if(self.type == "missing_item"):
            random_choices = self.get_missing()
        if(self.type == "choose_items"):
            random_choices = self.get_choose()
        return random_choices

    def get_missing(self):
        """
        missing_items type displays
            - all but one of the valid items in the question
            - the excluded valid_choice plus false_choices in the choices.
        """
        #TODO: Make sure missing item is in choose_items
        items_not_omitted = random.sample(self.valid_choices, len(self.valid_choices))
        items_omitted = items_not_omitted[:1]
        items_not_omitted.remove(items_omitted[0])
        self.items_not_omitted = items_not_omitted
        self.items_omitted = items_omitted
        choice_items = random.sample(self.false_choices[:4] + items_omitted, len(self.false_choices[:4]) + len(items_omitted))
        return choice_items

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
        choice_items = random.sample(self.false_choices[:4] + items_omitted, len(self.false_choices[:4]) + len(items_omitted))
        return choice_items


    def get_prompt(self, choices=None):
        """
        properly style and bracket the prompt string.
        """
        _choices = '\n'.join(f"{i}: {str(x)}" for i,x in enumerate(choices))
        if(self.type == "missing_item"):
            question_title = f"{bcolors.BOLD + self.title}\n\n{CONFIG['newline'].join(self.items_not_omitted)}"
            result = f"{bcolors.WARNING}{question_title}{bcolors.ENDC}\n\n{_choices}\n{bcolors.WARNING}Answer{bcolors.ENDC}"
        elif(self.type == "choose_items"):
            question_title = bcolors.BOLD + self.title
            result = f"{bcolors.WARNING}{question_title}{bcolors.ENDC}\n\n{_choices}\n{bcolors.WARNING}Answer{bcolors.ENDC}"
        else: # assume 'text' type
            result = bcolors.BOLD + bcolors.WARNING + self.title + bcolors.ENDC
        return result

    def validate(self, response, choices):
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
            response_items = [x for i,x in enumerate(choices) if str(i) in response]
            # Add remaining valid choices to response to validate.
            # response_items += self.items_not_omitted
            print("Response to Missing Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in self.items_omitted]
            extra_validators = [x for x in self.items_omitted if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
            if(not validated):
                print(f"Extra answers: {','.join(extra_answers)}\nExtra validators: {','.join(extra_validators)}\n")
        elif self.type == "choose_items":
            #TODO: Wrong number is getting added to choices and response is compared to rull valid_items list.
            response_items = [x for i,x in enumerate(choices) if str(i) in response.split(',')]
            print("Response Choose Items: " + json.dumps(response_items))
            extra_answers = [x for x in response_items if x not in self.items_omitted]
            extra_validators = [x for x in self.items_omitted if x not in response_items]
            validated = len(extra_answers) == 0 and len(extra_validators) == 0
        return validated
