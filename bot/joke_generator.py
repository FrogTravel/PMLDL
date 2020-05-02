import random
import threading
from itertools import cycle

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
    default_promt_token = '[QUESTION] '
    answer_token = '[ANSWER] '
    stop_token = '<|endoftext|>'
    POS_GRADE = 1
    NEG_GRADE = -1

    def __init__(self, model_path, max_joke_len=40, jokes_buffer_size=16, model_device='cpu'):
        self.model = ModelWrapper(model_path, max_length=max_joke_len)
        self.store = storage

        self.jokes_buffer_size = jokes_buffer_size
        self.__fill_jokes_buffer()

    def positive_grade(self, user_id, joke_id):
        self.store.add_or_update_vote(joke_id=joke_id, user_id=user_id, rating=self.POS_GRADE)

    def negative_grade(self, user_id, joke_id):
        self.store.add_or_update_vote(joke_id=joke_id, user_id=user_id, rating=self.NEG_GRADE)

    @synchronized
    def generate_joke(self, promt=""):
        if promt:
            joke_text = self.__continue_joke(self.default_promt_token + promt + f'\n{self.answer_token}')
        else:
            joke_text = self.__get_joke_from_buffer()
        joke_id = self.store.add_joke(joke_text)
        return Joke(id=joke_id, text=joke_text)

    def _prettify_result(self, model_output):
        def pp_answer(text):
            """Pretty-print the answer."""
            # Remove all text after the stop token
            text = text[: text.find(self.stop_token) if self.stop_token else None]
            text = text.replace(self.default_promt_token, '<b>Question:</b> ')
            text = text.replace(self.answer_token, '\n<b>Answer:</b> ')
            # TODO: Delete multiple answers / inform user about the input format.
            return text

        if isinstance(model_output, str):
            return pp_answer(model_output)
        else:
            return [pp_answer(ans) for ans in model_output]

    @synchronized
    def _call_model(self, prompt, num_return_sequences):
        """Generate the joke and prettify the output."""
        model_output = self.model.generate(prompt, num_return_sequences)
        return self._prettify_result(model_output)

    @synchronized
    def __fill_jokes_buffer(self):
        self.jokes_buffer = self._call_model(self.default_promt_token, num_return_sequences=self.jokes_buffer_size)

    @synchronized
    def __get_joke_from_buffer(self):
        if len(self.jokes_buffer) == 0:
            self.__fill_jokes_buffer()
        return self.jokes_buffer.pop()

    @synchronized
    def __continue_joke(self, promt):
        return self._call_model(promt, num_return_sequences=1)


class TestABGenerator(JokeGenerator):
    def __init__(self, datasets, models_paths, max_joke_len=40, jokes_buffer_size=16, model_device='cpu'):
        """
        Loads datasets and models. Initiates pools and orders of passing
        :param datasets:
        :param models_paths:
        """
        if not isinstance(datasets, list):
            datasets = list(datasets)
        self.jokes_buffer_size = jokes_buffer_size

        dataset_keys = [f"dataset{i}" for i in range(len(datasets))]
        model_keys = [f"model{i}" for i in range(len(models_paths))]

        self.key2model = dict()
        self.key2pool = dict()
        for model_key, model_path in zip(model_keys, models_paths):
            self.key2model[model_key] = ModelWrapper(model_path, max_length=max_joke_len)
            self.__fill_jokes_buffer(model_key)

        self.key2dataset = dict()
        for dataset_key, dataset in zip(dataset_keys, datasets):
            self.key2dataset[dataset_key] = dataset

        self.dataset_keys = cycle(dataset_keys)
        self.model_keys = cycle(model_keys)
        self.use_dataset = cycle([True, False])  # which source to use: True - dataset, False - next model's pool

        self.store = storage

    def generate_joke(self, promt=""):
        if promt:
            key, joke_text = self.__continue_joke(self.default_promt_token + promt + f'\n{self.answer_token}')
        else:
            key, joke_text = self.__get_joke_from_buffer()
        joke_id = self.store.add_joke(joke_text, generated_by=key)
        return Joke(id=joke_id, text=joke_text)

    @synchronized
    def _call_model(self, model_key, prompt, num_return_sequences):
        """Generate the joke and prettify the output."""
        model_output = self.key2model[model_key].generate(prompt, num_return_sequences)
        return self._prettify_result(model_output)

    @synchronized
    def __fill_jokes_buffer(self, model_key):
        self.key2pool[model_key] = self._call_model(model_key,
                                                    self.default_promt_token,
                                                    num_return_sequences=self.jokes_buffer_size)

    @synchronized
    def __get_joke_from_buffer(self):
        """
        From one of datasets or from one of models
        """
        if next(self.use_dataset):
            key = next(self.dataset_keys)
            joke = random.choice(self.key2dataset[key])
        else:
            key = next(self.model_keys)
            if len(self.key2pool[key]) == 0:
                self.__fill_jokes_buffer(key)
            joke = self.key2pool[key].pop()
        return key, joke

    @synchronized
    def __continue_joke(self, promt):
        model_key = next(self.model_keys)
        return model_key, self._call_model(model_key, promt, num_return_sequences=1)


if __name__ == '__main__':
    def readlines(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.readlines()


    datasets = [readlines("../data/transcripts/dave-chappelle-deep-heart-texas-2017-full-transcript.txt"),
                readlines("../data/transcripts/dave-chappelle-equanimity-2017-full-transcript.txt")]
    models = ["gpt2"]

    gen = TestABGenerator(datasets, models)

    for i in range(10):
        print(gen.generate_joke().text)
