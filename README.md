# Joke Generator Bot
A Question-Answer joke generator bot for Telegram. As a joke generator we used a fine-tuned GPT-2 model.

**Authors**:
* Vlad Kuleykin
* Boris Guryev
* Ekaterina Levchenko
* Irina Podlipnova

## Purposes
This project was done during the *Practical Machine Learning and Deep Learning* course at Spring 2020 semester at *Innopolis University* (Innopolis, Russia). You can find our technical report in `report.pdf` file.

## How to Use
Put in the bot token and path to the model in `bot.cfg`, after which you can run the next command:
```cmd
python3 bot\main_bot.py
```
And you have a working bot!

## How to train a model
To train the model, we have three datasets:
* **QA Jokes** (3.29 MB) - the original dataset we've found on Kaggle [1]. It contains ~38k question-answer jokes
* **Short Jokes** (22.8 MB) - the biggest dataset in our collection, it was also found on Kaggle [2] and consists of ~231k short length jokes from Twitter and Reddit. But it also contains a lot of noise and misspellings
* **Stand up transcripts** (13.5 MB) - the manually scraped dataset of stand up transcripts from one site [3]

But you're free to use others! (and please, write me if you found good one)

For the training, the `GPT-2 train helper.ipynb` in train folder can come in handy. As it can convert the datasets to appropriate GPT-2 input files and extract the QA jokes from the *Short Jokes* dataset.

And as for the actual training use the `run_language_modelling.py` script taken from the Transformers library [4]:
```cmd
python3 run_language_modeling.py \
    --model_type=gpt2 \
    --model_name_or_path=**INPUT_MODEL_PATH** \
    --output_dir=**OUTPUT_MODEL_PATH** \
    --learning_rate=1e-05 \
    --num_train_epochs=10 \
    --per_gpu_train_batch_size=2 \
    --gradient_accumulation_steps=8 \
    --save_steps=1000 \
    --train_data_file=**TRAIN_DATA_PATH** \
    --do_train \
```
If the model doesn't fit in your GPU, try changing the `block_size` or `per_gpu_train_batch_size`.

To test the current model run the `run_generation.py` script:
```cmd
python3 run_generation.py \
    --model_type=gpt2 \
    --model_name_or_path=**TRAINED_MODEL_PATH** \
    --prompt="[QUESTION]" \
    --length=60 \
    --stop_token="<|endoftext|>" \
    --temperature=0.9 \
    --repetition_penalty=1.05 \
    --k=50 \
    --p=0.95 \
    --num_return_sequences=40
```
Feel free to experiment with the `temperature`, `k`, `p` and `repetition_penalty`, to get better insights as to what do this arguments do, visit this [link][5].



[1]: https://www.kaggle.com/jiriroz/qa-jokes "QA Jokes dataset"
[2]: https://www.kaggle.com/abhinavmoudgil95/short-jokes "Short Jokes dataset"
[3]: https://render.githubusercontent.com/view/scrapsfromtheloft.com "Stand Up transcripts site"

[4]: https://github.com/huggingface/transformers/blob/master/examples/run_language_modeling.py "Transformers. Run language model example"

[5]: https://huggingface.co/blog/how-to-generate "Hugging face. How to generate"