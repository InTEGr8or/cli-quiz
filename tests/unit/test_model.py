import json
from cliqz.question import Question

class Question_T(Question):
    test_resut = None
    test_function = None
    def __init__(self, question):
        super().__init__(question)
        func = question['test_function']
        print(json.dumps(self))
        test_result = question['test_result']
        test_function = eval(func)
