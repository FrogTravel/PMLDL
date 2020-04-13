# Modern Application Production

Language: Python

Version Control: GitHub 

Tests: Python unittest package 

Tasks: [Trello](https://https://trello.com/invite/b/6k7nigbp/8d26ddad39c33393cf6053e7ac0ac4ac/pmldl)

User Stories: [GitHub issues](https://github.com/FrogTravel/PMLDL/issues)

## Project Proposal 

### General

These days jokes and memes become part of modern people's life. Each day everybody spends time consuming content. Communities like *Reddit* or *9GAG* periodically release meme calendars.

We propose a question-answer joke generator telegram bot with the aim to distinguish if artificially generated content can entertain users at the same level as human-created jokes.

### Training
For training, we will apply transfer learning. As a starting model we will try different state-of-the-art language models, such as *BERT* [2], *GPT-2* [3]. As a training dataset will use set from *Kaggle* [1], which we will extend with other 2-liner jokes from the internet.

### Evaluation
Joking is a subjective topic, so we are planning to ask people to evaluate samples of generated jokes. And afterward, we'll compare the results for different models.

### Final result
We are planning to deploy this project into telegram infrastructure for simple interaction with the user. The flexibility of this platform covers all requirements described above such as: deliver content, collecting evaluation from users and easy deployment.

1) [ Kaggle dataset](https://www.kaggle.com/jiriroz/qa-jokes )
2) BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. 
Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova 
3) Language Models are Unsupervised Multitask Learners. Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever

Below are reports that we made for our course assignments. They might be different from the real tasks in trello in some way
## Sprint 4
### Overview
This week we focused on the prototype development. We contributed in the Telegram bot, deployment part and improvement of the fine-tuning of the GPT-2.

### Telegram bot
During this sprint, we implemented the last part for our bot interface. Our bot has two use cases. The first one is the /joke command, which generates the joke as a pair "Joke-Answer." Another case only the "answer" generation. To use this function, send a question to our bot, it will concern any text without backslash as a question for a generation. Though we will change this in the next spring to reduce the load on the server.
After generation, the bot will display two buttons - thumb up and thumb down. The user might grade the joke. After that, the "grading" message will be changed to "Thank you for your feedback."

### Deployment
First of all, we reviewed open source solutions for wrapping models into web API.

*Cortex* [2] - an open-source platform for deploying machine learning models as production web services. Provides logging, auto-scaling, forwarding GPU into the container, etc. However, this framework is designed to be self-hosted on AWS infrastructure. During this project, we aimed to run anything locally, because of the hardware requirements of the selected language model. 

*Model Asset Exchange (MAX)* [3] - this is a project template wrapped around flask python backend framework. We found it over architected because the main goal of this project is to force developers to provide API documentation to the endpoints. 

Finally, we decided to rewrite the CLI of the transformers repository [1] in simple format convenient for our task. In our case, it is enough to keep the model in memory - usual python class instance - and run forward whenever bot receives a message from the user. But, as requests can be processed in an asynchronous manner (especially in time of presentation), we found an issue of GPU memory leak when more than 1 requests processed.

### Training
For the training part, this week we worked on improving the fine-tuning of the GPT-2 model:

- *Fixed preprocessing* - we had a few errors as we forgot to put special tokens for the start and end of the documents, so now they are fixed.
- *Experimented with different frameworks* - we experimented with a couple of TensorFlow/Pytorch frameworks for fine-tuning the GPT-2, transformers [1] and gpt-2-simple [5]. And now are settled at the transformers, with the planning of some adoption of functionality from the other one.
- *Collected new dataset for fine-tuning* - as our previous results were repetitive and not diverse, as we think it is because of the small size of the dataset (3 MB), so we proposed an additional dataset of stand up transcripts (13 MB), which we gathered ourselves. We haven't yet tested our proposal.

### References
1) https://github.com/huggingface/transformers/blob/master/examples/run_language_modeling.py - Transformers. Run language model example
2) https://github.com/cortexlabs/cortex/ Cortex. Cloud native model serving infrastructure
3) https://developer.ibm.com/tutorials/getting-started-with-the-ibm-code-model-asset-exchange/ IBM Model Asset Exchange
4) https://github.com/FrogTravel/PMLDL}{Our Github repository
5) https://github.com/minimaxir/gpt-2-simple}{\texttt{gpt-2-simple GitHub page

## Sprint 5

We are now at Sprint 5. We are connecting our bot interface to a backend and making tests for a bot. We fine-tune the final model at the backend. 
