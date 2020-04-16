import threading

from bot import storage
from bot.inference import ModelWrapper
from bot.joke import Joke


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


class JokeGenerator(object):
    default_promt_token = "Q:"
    POS_GRADE = 1
    NEG_GRADE = -1

    def __init__(self, model_path, max_joke_len=40, jokes_buffer_size=16):
        self.model = ModelWrapper(model_path, max_length=max_joke_len)
        self.store = storage

        self.jokes_buffer_size = jokes_buffer_size
        self.__fill_jokes_buffer()

    @synchronized
    def __fill_jokes_buffer(self):
        self.jokes_buffer = self.model.generate(self.default_promt_token, num_return_sequences=self.jokes_buffer_size)

    @synchronized
    def generate_joke(self, promt=""):
        if promt:
            joke_text = self.__continue_joke(promt)
        else:
            joke_text = self.__get_joke_from_buffer()
        joke_id = self.store.add_joke(joke_text)
        return Joke(id=joke_id, text=joke_text)

    @synchronized
    def __get_joke_from_buffer(self):
        if len(self.jokes_buffer) == 0:
            self.__fill_jokes_buffer()
        return self.jokes_buffer.pop()

    def __continue_joke(self, promt):
        return self.model.generate(promt, num_return_sequences=1)

    def positive_grade(self, user_id, joke_id):
        self.store.add_or_update_vote(joke_id=joke_id, user_id=user_id, rating=self.POS_GRADE)

    def negative_grade(self, user_id, joke_id):
        self.store.add_or_update_vote(joke_id=joke_id, user_id=user_id, rating=self.NEG_GRADE)
