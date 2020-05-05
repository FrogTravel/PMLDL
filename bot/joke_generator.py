import random
import os
import threading
import re
from itertools import cycle

import storage
from inference import ModelWrapper
from data import Dataset, Joke

from abc import ABC, abstractmethod


def synchronized(func):
    """Decorator for the syncronized usage of the function."""
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func

class AbstractJokeGenerator(ABC):
    """Abstract class for joke generation using `ModelWrapper`."""

    default_promt_token = '[QUESTION]'
    answer_token = '[ANSWER]'
    custom_promt = f'{default_promt_token}{{}}\n{answer_token}'
    stop_token = '<|endoftext|>'
    POS_GRADE = 1
    NEG_GRADE = -1

    def __init__(self, jokes_buffer_size):
        self.store = storage
        self.jokes_buffer_size = jokes_buffer_size

    def positive_grade(self, user_id, joke_id):
        self.store.add_or_update_vote(
            joke_id=joke_id, user_id=user_id, rating=self.POS_GRADE)

    def negative_grade(self, user_id, joke_id):
        self.store.add_or_update_vote(
            joke_id=joke_id, user_id=user_id, rating=self.NEG_GRADE)
    
    def _prettify_result(self, model_output):
        def pp_answer(text):
            """Pretty-print the answer."""
            # Remove all text after the stop token
            text = text[: text.find(self.stop_token) if self.stop_token else None]
            # Remove multiple answers
            text = self.answer_token.join(text.split(self.answer_token, 2)[:2])
            # Replace model tokens with html formatted ones.
            text = re.sub(f'\{self.default_promt_token} *', '<b>Question:</b> ', text)
            text = re.sub(f'\{self.answer_token} *', '\n<b>Answer:</b> ', text)
            return text

        if isinstance(model_output, str):
            return pp_answer(model_output)
        else:
            return [pp_answer(ans) for ans in model_output]

    @synchronized
    def generate_joke(self, model, promt=""):
        """Generate the joke from given promt.
        
        :param model: model to use to generate joke.
        :param promt: (optional) promt for a joke, if not given
        generates the whole joke
        :return: `Joke` object
        """
        if promt:
            print(f'[INFO] continue - Model: {model.name}')
            res = self._continue_joke(model, promt)
        else:
            res = self._get_joke_from_buffer()
        res['text'] = self._prettify_result(res['text'])
        joke_id = self.store.add_joke(**res)
        return Joke(id=joke_id, text=res['text'])
    
    @synchronized
    def __call_model(self, model, prompt, num_return_sequences):
        """Call the model to generate the joke.

        :param model: model to use
        :param promt: prompt for the model
        :param num_return_sequences: number of sequences to generate
        :return: list of (num_return_sequences) dicts
        with 'text' and 'generated_by' fields
        """
        return [{
            'generated_by': model.name,
            'text': seq
        } for seq in model.generate(prompt, num_return_sequences)]
    
    @synchronized
    def _fill_jokes_buffer(self, model):
        """Fill the jokes buffer associated with given model.
        WARNING: Default implementation just returns the result.

        :param model: model to use
        :return: see `__call_model` function
        """
        return self.__call_model(model, self.default_promt_token,
                                num_return_sequences=self.jokes_buffer_size)
    
    @synchronized
    @abstractmethod
    def _get_joke_from_buffer(self, model):
        """Get the new joke from the buffer for given model.
        If needed update the buffer.
        """
        pass
    
    @synchronized
    def _continue_joke(self, model, promt):
        """Continue the joke given in promt."""
        model_promt = self.custom_promt.format(' ' + promt.strip())
        return self.__call_model(model, model_promt, num_return_sequences=1)[0]

class JokeGenerator(AbstractJokeGenerator):
    """Simple Joke generator using one model."""

    def __init__(self, model_path, max_joke_len=40, jokes_buffer_size=16, model_device='cpu'):
        super().__init__(jokes_buffer_size)
        model_name = os.path.split(model_path)[1]
        self.model = ModelWrapper(model_path, model_name, max_length=max_joke_len)
        self._fill_jokes_buffer()

    @synchronized
    def _fill_jokes_buffer(self):
        self.jokes_buffer = super()._fill_jokes_buffer(self.model)

    @synchronized
    def _get_joke_from_buffer(self):
        if len(self.jokes_buffer) == 0:
            self._fill_jokes_buffer()
        return self.jokes_buffer.pop()

    @synchronized
    def generate_joke(self, promt=""):
        return super().generate_joke(self.model, promt)


class TestABGenerator(AbstractJokeGenerator):
    """Joke generator for a/b testing.
    Outputs the joke from either of models/datasets.
    Chooses the source randomly."""
    def __init__(self, dataset_paths, model_paths, max_joke_len=40, jokes_buffer_size=16, model_device='cpu'):
        """
        Loads datasets and models. Initiates pools and orders of passing
        :param dataset_paths: paths to the dataset
        :param model_paths: paths to the model
        """
        super().__init__(jokes_buffer_size)

        self.models, self.key2pool = list(), dict()
        for model_path in model_paths:
            model_name = os.path.split(model_path)[1]
            self.models.append(ModelWrapper(model_path, model_name, max_length=max_joke_len))
            self._fill_jokes_buffer(self.models[-1])

        self.datasets = [Dataset(path) for path in dataset_paths]
        self.num_of_pools = len(self.models) + len(self.datasets)

    @synchronized
    def generate_joke(self, promt=""):
        idx = random.randint(0, len(self.models) - 1)
        model = self.models[idx]
        return super().generate_joke(model, promt)

    @synchronized
    def _fill_jokes_buffer(self, model):
        self.key2pool[model.name] = super()._fill_jokes_buffer(model)

    @synchronized
    def _get_joke_from_buffer(self):
        idx = random.randint(0, self.num_of_pools - 1)
        res = {}
        if idx < len(self.datasets):
            print(f'[INFO] generate - Dataset: {self.datasets[idx].name}')
            return random.choice(self.datasets[idx])
        idx = idx - len(self.datasets) - 1
        key = self.models[idx].name
        print(f'[INFO] generate - Model: {key}')
        if len(self.key2pool[key]) == 0:
            self._fill_jokes_buffer(self.models[idx])
        return self.key2pool[key].pop()


if __name__ == '__main__':

    datasets = ["data/qa_jokes.csv"]
    models = ["train/models/output_6"]

    gen = TestABGenerator(datasets, models)

    for i in range(10):
        print(gen.generate_joke().text)
