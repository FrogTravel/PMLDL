# Modern Application Production

Language: Python

Version Control: GitHub 

Tests: Python unittest package 

Tasks: [Trello](https://https://trello.com/invite/b/6k7nigbp/8d26ddad39c33393cf6053e7ac0ac4ac/pmldl)

User Stories: GitHub issues 

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


