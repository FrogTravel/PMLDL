class Joke():
    def __init__(self, question, answer, id):
        self.question = question
        self.answer = answer
        self.id = id
        self.text = question + " \n" + answer
