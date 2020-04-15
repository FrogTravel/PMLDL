from joke import Joke

def generate_joke():
    return Joke("SampleQuestion", "SampleAnswer", 0)

def generate_answer(joke: Joke):
    return Joke(joke.question, "SAMPLE GENERATED ANSWER", 0)

def positive_grade(joke_id):
    pass

def negative_grade(joke_id):
    pass