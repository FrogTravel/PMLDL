import torch
from torch import LongTensor
import logging

from transformers import (
    CTRLLMHeadModel,
    CTRLTokenizer,
    GPT2LMHeadModel,
    GPT2Tokenizer,
    OpenAIGPTLMHeadModel,
    OpenAIGPTTokenizer,
    TransfoXLLMHeadModel,
    TransfoXLTokenizer,
    XLMTokenizer,
    XLMWithLMHeadModel,
    XLNetLMHeadModel,
    XLNetTokenizer,
)
from yt_encoder import YTEncoder

MODEL_CLASSES = {
    "gpt2": (GPT2LMHeadModel, GPT2Tokenizer),
    "gpt2-yttm": (GPT2LMHeadModel, YTEncoder),
    "ctrl": (CTRLLMHeadModel, CTRLTokenizer),
    "openai-gpt": (OpenAIGPTLMHeadModel, OpenAIGPTTokenizer),
    "xlnet": (XLNetLMHeadModel, XLNetTokenizer),
    "transfo-xl": (TransfoXLLMHeadModel, TransfoXLTokenizer),
    "xlm": (XLMWithLMHeadModel, XLMTokenizer),
}

# Don't show warnings.
logging.getLogger("transformers.tokenization_utils").setLevel(logging.ERROR)
logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)
logging.getLogger("transformers.configuration_utils").setLevel(logging.ERROR)


class ModelWrapper:
    def __init__(self, model_path, model_name,
                 device='cpu',
                 model_type='gpt2',
                 max_len=40,
                 temperature=0.9,
                 n_return_sequences=1,
                 repetition_penalty=1.0,
                 k=50,
                 p=0.95,
                 **kwargs):
        self.n_return_sequences = n_return_sequences
        self.repetition_penalty = repetition_penalty
        self.k = k
        self.p = p
        self.temperature = temperature
        self.device = torch.device(device)
        self.max_length = max_len
        model_class, tokenizer_class = MODEL_CLASSES[model_type]
        self.tokenizer = tokenizer_class.from_pretrained(model_path)
        self.model = model_class.from_pretrained(model_path)
        self.name = model_name
        self.logger = logging.getLogger('ML: ' + self.name)
        self.model.to(self.device)

    def __encode(self, text):
        encoded_prompt = self.tokenizer.encode(text, add_special_tokens=False)
        encoded_prompt = LongTensor(encoded_prompt).unsqueeze(0)
        return encoded_prompt.to(self.device)

    def generate(self, beginning, n_return_sequences=None):
        if n_return_sequences is None:
            n_return_sequences = self.n_return_sequences
        encoded_prompt = self.__encode(beginning)
        output_sequences = self.model.generate(
            input_ids=encoded_prompt,
            max_length=self.max_length + len(encoded_prompt[0]),
            temperature=self.temperature,
            top_k=self.k,
            top_p=self.p,
            repetition_penalty=self.repetition_penalty,
            do_sample=True,
            num_return_sequences=n_return_sequences,
        )

        # Remove the batch dimension when returning multiple sequences
        if len(output_sequences.shape) > 2:
            output_sequences.squeeze_()
        return [self.tokenizer.decode(j, clean_up_tokenization_spaces=True) for j in output_sequences]


if __name__ == '__main__':
    import datetime

    total_time = datetime.datetime.now()
    m = ModelWrapper(model_path='gpt2', device='cuda')
    # Time test
    # for i in range(10):
    #     start = datetime.datetime.now()
    #     m.generate("hello, world")
    #     dt = datetime.datetime.now() - start
    #     print("\t", dt)
    # Batch processing test
    res = m.generate("[QUESTION] ", n_return_sequences=4)
    for j in res:
        print(j)

    print("Total time: ", datetime.datetime.now() - total_time)
