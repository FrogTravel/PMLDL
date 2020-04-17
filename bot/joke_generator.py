import threading

import storage
from inference import ModelWrapper
from joke import Joke


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


class JokeGenerator(object):
    default_promt_token = '<|startoftext|>[QUESTION] '
    answer_token = '[ANSWER] '
    stop_token = '<|endoftext|>'
    POS_GRADE = 1
    NEG_GRADE = -1

    def __init__(self, model_path, max_joke_len=40, jokes_buffer_size=16):
        self.model = ModelWrapper(model_path, max_length=max_joke_len)
        self.store = storage

        self.jokes_buffer_size = jokes_buffer_size
        self.__fill_jokes_buffer()

    def __pp_answer(self, text):
        """Pretty-print the answer."""
        # Remove all text after the stop token
        text = text[: text.find(self.stop_token) if self.stop_token else None]
        text = text.replace(self.default_promt_token, '<b>Question:</b>')
        text = text.replace(self.answer_token, '\n<b>Answer:</b>')
        # TODO: Delete multiple answers / inform user about the input format.
        return text

    def __prettify_result(self, model_output):
        if isinstance(model_output, str):
            return self.__pp_answer(model_output)
        else:
            return [self.__pp_answer(ans) for ans in model_output]

    @synchronized
    def _generate_joke(self, *args, **kwargs):
        """Generate the joke and prettify the output."""
        model_output = self.model.generate(*args, **kwargs)
        return self.__prettify_result(model_output)

    @synchronized
    def __fill_jokes_buffer(self):
        self.jokes_buffer = self._generate_joke(self.default_promt_token, num_return_sequences=self.jokes_buffer_size)

    @synchronized
    def generate_joke(self, promt=""):
        if promt:
            joke_text = self.__continue_joke(self.default_promt_token + promt + f'\n{self.answer_token}')
        else:
            joke_text = self.__get_joke_from_buffer()
        joke_id = self.store.add_joke(joke_text)
        return Joke(id=joke_id, text=joke_text)

    @synchronized
    def __get_joke_from_buffer(self):
        if len(self.jokes_buffer) == 0:
            self.__fill_jokes_buffer()
        return self.jokes_buffer.pop()

    @synchronized
    def __continue_joke(self, promt):
        return self._generate_joke(promt, num_return_sequences=1)

    def positive_grade(self, user_id, joke_id):
        self.store.add_or_update_vote(joke_id=joke_id, user_id=user_id, rating=self.POS_GRADE)

    def negative_grade(self, user_id, joke_id):
        self.store.add_or_update_vote(joke_id=joke_id, user_id=user_id, rating=self.NEG_GRADE)
