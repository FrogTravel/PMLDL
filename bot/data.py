import os
import logging
import pandas as pd


class Dataset:
    """Wrapper for the DataFrame to return values similar 
    to `AbstractJokeGenerator` output.
    """

    def __init__(self, dataset_path, promt_token, answer_token):
        self.promt_token = promt_token
        self.answer_token = answer_token
        self.name = os.path.split(dataset_path)[1]
        self.data = pd.read_csv(dataset_path)
        self.logger = logging.getLogger("DS: " + self.name)

    def __getitem__(self, idx):
        question = self.data['Question'].iloc[idx].strip()
        answer = self.data['Answer'].iloc[idx].strip()
        text = (self.promt_token + question + '\n'
                + self.answer_token + ' ' + answer)
        self.logger.info('Got joke from dataset')
        return {
            'text': text,
            'generated_by': self.name,
        }

    def __len__(self):
        return len(self.data)


class Joke:
    """An interface class for a Joke."""

    def __init__(self, text, id):
        self.id = id
        self.text = text
