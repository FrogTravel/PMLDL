import os
import re
import random
import threading
import logging
from abc import ABC, abstractmethod

import storage
from inference import ModelWrapper
from data import Dataset, Joke


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

    def __init__(self, buffer_size):
        self.store = storage
        self.buffer_size = buffer_size

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

    def generate_joke(self, model, promt=""):
        """Generate the joke from given promt.

        :param model: model to use to generate joke.
        :param promt: (optional) promt for a joke, if not given
        generates the whole joke
        :return: `Joke` object
        """
        if promt:
            res = self._continue_joke(model, promt)
        else:
            res = self._get_new_joke()
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
    def _get_from_buffer(self, model, buffer):
        """Get a joke from the buffer.

        :param buffer: buffer to get the joke from
        :param model: model to use to fill the buffer
        :return: joke from the buffer
        """
        model.logger.info('Got joke from the buffer')
        if len(buffer) == 0:
            self._fill_buffer(model)
        return buffer.pop()

    @synchronized
    @abstractmethod
    def _fill_buffer(self, model):
        """Fill the buffer associated with this model."""
        pass

    @synchronized
    def _generate_for_buffer(self, model):
        """Generates jokes to fill the buffer.

        :param model: model to use
        :return: see `__call_model` function
        """
        model.logger.info('Filling the buffer')
        return self.__call_model(model, self.default_promt_token,
                                 num_return_sequences=self.buffer_size)

    @abstractmethod
    def _get_new_joke(self, model):
        """Get the new joke from the given model.
        """
        pass

    @synchronized
    def _continue_joke(self, model, promt):
        """Continue the joke given in promt."""
        model.logger.info('Continue joke')
        model_promt = self.custom_promt.format(' ' + promt.strip())
        return self.__call_model(model, model_promt, num_return_sequences=1)[0]


class JokeGenerator(AbstractJokeGenerator):
    """Simple Joke generator using one model."""

    def __init__(self, model_path, max_len=40, buffer_size=16, model_device='cpu'):
        super().__init__(buffer_size)
        model_name = os.path.split(model_path)[1]
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.info('Loading models...')
        self.model = ModelWrapper(model_path, model_name, max_length=max_len)
        self.logger.info(f'Loaded {self.models[-1].name}')
        self._fill_buffer()
        self.logger.info('Ready to work!')

    def generate_joke(self, promt=""):
        return super().generate_joke(self.model, promt)

    @synchronized
    def _fill_buffer(self, model):
        self.jokes_buffer = super()._generate_for_buffer(model)

    def _get_new_joke(self):
        return self._get_from_buffer(self.model, self.jokes_buffer)


class TestABGenerator(AbstractJokeGenerator):
    """Joke generator for a/b testing.
    Outputs the joke from either of models/datasets.
    Chooses the source randomly.
    """

    def __init__(self, dataset_paths, model_paths, max_len=40,
                 buffer_size=16, model_device='cpu'):
        """
        Loads datasets and models. Initiates pools and orders of passing
        :param dataset_paths: paths to the dataset
        :param model_paths: paths to the model
        """
        super().__init__(buffer_size)

        self.models, self.key2pool = list(), dict()
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.info('Loading models...')
        for m_path in model_paths:
            m_name = os.path.split(m_path)[1]
            self.models.append(ModelWrapper(m_path, m_name, max_length=max_len))
            self.logger.info(f'Loaded {self.models[-1].name}')
            self._fill_buffer(self.models[-1])

        self.logger.info('Loading datasets...')
        self.datasets = list()
        for d_path in dataset_paths:
            self.datasets.append(Dataset(d_path, self.default_promt_token,
                                         self.answer_token))
            self.logger.info(f'Loaded {self.datasets[-1].name}')
        self.logger.info('Ready to work!')
        self.num_of_pools = len(self.models) + len(self.datasets)

    def generate_joke(self, promt=""):
        idx = random.randint(0, len(self.models) - 1)
        model = self.models[idx]
        return super().generate_joke(model, promt)

    @synchronized
    def _fill_buffer(self, model):
        self.key2pool[model.name] = super()._generate_for_buffer(model)

    def _get_new_joke(self):
        """Get the joke either from the model buffer, or dataset."""
        idx = random.randint(0, self.num_of_pools - 1)
        if idx < len(self.datasets):
            return random.choice(self.datasets[idx])
        idx = idx - len(self.datasets) - 1
        key = self.models[idx].name
        return self._get_from_buffer(self.models[idx],
                                     self.key2pool[key])


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    datasets = ["../data/qa_jokes.csv"]
    models = ["../train/models/output_8"]

    gen = TestABGenerator(datasets, models)

    for i in range(10):
        print(gen.generate_joke().text)
