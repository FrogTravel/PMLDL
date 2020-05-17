# Modern Application Production

Language: Python

Version Control: GitHub 

Tasks: [Trello](https://https://trello.com/invite/b/6k7nigbp/8d26ddad39c33393cf6053e7ac0ac4ac/pmldl)

User Stories: [GitHub issues](https://github.com/FrogTravel/PMLDL/issues)

We are using feature-oriented branches

Team: Irina Podlipnova, Boris Guryev, Ekaterina Levchenko (Scram Master), Vladislav Kuleykin

## Project Proposal 

### General

These days jokes and memes become part of modern people's life. Each day everybody spends time consuming content. Communities like *Reddit* or *9GAG* periodically release meme calendars.

We propose a question-answer joke generator telegram bot with the aim to distinguish if artificially generated content can entertain users at the same level as human-created jokes.

### Training
For training, we will apply transfer learning. As a starting model we will try different state-of-the-art language models, such as *BERT* [2], *GPT-2* [3]. As a training dataset will use set from *Kaggle* [1], which we will extend with other 2-liner jokes from the internet.

### Evaluation
Joking is a subjective topic, so we are planning to ask people to evaluate samples of generated jokes. And afterward, we'll compare the results for different models.

### Expected Final Result
We are planning to deploy this project into telegram infrastructure for simple interaction with the user. The flexibility of this platform covers all requirements described above such as: deliver content, collecting evaluation from users and easy deployment.

1) [ Kaggle dataset](https://www.kaggle.com/jiriroz/qa-jokes )
2) BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. 
Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova 
3) Language Models are Unsupervised Multitask Learners. Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever

## Sprint 1 
### Burndown chart
![](https://i.imgur.com/FZn2vI5.png)
storypoints on vertical x days on horizontal axis
Blue - ideal burndown, Green - our result

## Sprint 2 & 3
### Burndown charts
#### Sprint 2
![](https://i.imgur.com/nYpBchu.png)
storypoints on vertical x days on horizontal axis
Blue - ideal burndown, Green - our result
#### Sprint 3
![](https://i.imgur.com/mVXGmoX.png)
storypoints on vertical x days on horizontal axis
Blue - ideal burndown, Green - our result

Below are reports that we made for our course assignments. They might be different from the real tasks in trello in some way

### Dataset
The dataset we going to use is taken from Kaggle competition [4]. It contains more than 38000 samples of so-called question-answer jokes. All jokes are parsed from Reddit.


Jokes examples:

    Q: Why is Yoda the worst copilot?
    A: "Yoda, are we still going the right way?" 
       "Off course we are"

    Q: What do you call a blonde who dyes her hair brown?
    A: AI (Artificial Intelligence)


    Q: Why do programmers confuse Christmas and Halloween?
    A: Because Dec 25 is Oct 31

Also, we'd like to extend Kaggle's dataset with some more examples because we still think that the number of jokes in the dataset is not enough to train a good model. Moreover, some jokes are duplicated, so it makes the model to "overfit" and generate a lot of similar jokes. There can be at least 3 possible ways to solve this problem: add more examples, so to neglect the influence of duplicates on the model; exclude duplicates from the dataset using some measurement of similarity or just ignore it assuming that this will not lead to overfitting.

Finally, we need to clear the dataset and make some pre-processing because jokes are just parsed from Reddit and not cleaned up. So there can be some notes inside jokes, explanations, editions marks, some credits to authors of jokes, jokes can be in the wrong format and etc. Below some examples of such cases:

Initial version:

    Q: How do Muslims laugh?
    A: Muahahahamed Note: I don't have any prejudices against Islamic
    
Pre-processed version:

    Q: How do Muslims laugh?
    A: Muahahahamed

Initial version:

    Q: Why did Eric Clapton make the switch from PC to Apple?
    A: Well because he had a horrible experience with windows. (credit to Neil Hamburger for this amazing joke)
    
Pre-processed version:

    Q: Why did Eric Clapton make the switch from PC to Apple?
    A: Well because he had a horrible experience with windows.

Initial version:
    
    Q: What do you have left after you burn a French alphabet?
    A: H Edit: I don't like explaining jokes but since the first guy didn't get I might as well: When pronounced in a French accent it sounds like ash.
    
Pre-processed version:

    Q: What do you have left after you burn a French alphabet?
    A: H
Initial version:

    Q: Why does Santa have three gardens?
    A: Q: Why does Santa have three gardens? A: So he can ""hoe, hoe, hoe.""
    
Pre-processed version:

    Q: Why does Santa have three gardens?
    A: So he can ""hoe, hoe, hoe.""


### Telegram bot
#### Reasons
We decided to use a Telegram bot because it is a very lightweight solution to communicate with a user and retrieve feedback from them. The flexibility of the bot API allows us to implement all planned features and possible increments in the future.

#### Functional description
Our primary feature is the question-answer jokes generation when the joke sends by a user and funny candidate answer returned by bot. Each generated joke will include two inline buttons: "Thumb-up" and "Thumb-down". Then we can collect accepted by humans jokes to pool and use them in future: a) for fine-tuning; b) for sharing funny joke responses. There are two ways of doing so - directly in a bot or in a separate channel.



### Language models review
#### BERT
Still a famous and widely used model. However, initially this model natural to use for tasks like classification, named entity detection or casual embedding [1]. However, there are several improvements on BERT adopted to model language [2] or trained/fine-tuned for modeling language

For now, we took the pre-trained model from [2] and produced several samples for text generation with non-empty (provided by us) seed sentences:

    Q: who touched my pasta ?
    A: bad people , like me . like pretty girl . 
    but so far i was a little hungry .

    Q: who touched my spaghetti ?
    A: nobody had never touched my hand , 
    pleasant bo ##le , who had not played any such game yet ?

So, even pre-trained for sentence generation, this model still can return some meaningful in context respond as well as fluctuated sequence. Still, we will try to fine-tune the model with our data to evaluate final behavior. 

There are many BERT modifications and one of them could be applicable for our task. We found the Question-Answer dataset [3] with links to implementation papers. Probably one of their models or training approaches will be significant for our work.



### GPT-2
#### Model selection
GPT-2 is the current state-of-the-art generative transformer model. It's a direct scale-up of their previous GPT model, the only change is the number of parameters ($>$10x more), and new, cleaner dataset (also $>$10x bigger). GPT-2 achieves state-of-the-art scores on a variety of domain-specific language modeling tasks without any fine-tuning.

Also, GPT-2 has models of different sizes\footnote{We use the names from the https://huggingface.co/transformers/v2.3.0/pretrained_models.html transformers framework documentation, and as we have multiple limitations:

- *processing power* - current consumer GPUs can't even fit \texttt{gpt2-large} and \texttt{gpt2-xl} models for training, so our focus will be on a smaller versions;
- *small dataset* - as our dataset is quite small (3.6 MB) compared to original (40 GB), we'll not be able to fine-tune big models, but for the small models, this is a right amount of data, as they fine-tune fast;
- *inference time* - and as we plan to deploy the final model, we need to think about inference time, as it needs to be fast, for the bot to provide in-time responses.


So, for now we'll consider gpt-2, gpt-2-medium and DistilGPT2 models.

### Fine-tuning results
For now we tried to fine-tune the gpt-2 and gpt-2-medium models, and their results were not distinct from each other, so I'll cover them jointly.

Firstly, disclaimer: there's a lot of filthy words, as the dataset is full of them.

The model generates a lot of classic cross the road, change the bulb jokes, which again can come from a bad jokes balance in the dataset:

    Q: Why did the monkey cross the road?
    A: For his brother's sake.
    
    Q: How many babies does it takes to screw in a lightbulb?
    A: About 4,000.
    
    Q: How many feminists does it take to change a lightbulb?
    A: None. They can't change anything.

Most of the other jokes make no sense:

    Q: What is Gordon Ramsay's favorite beverage?
    A: Mountain Bison
    
    Q: Why is it so windy in Russia?
    A: Because everything is worth it.
    
    Q: What do Jesus and the world have in common?
    A: They are all tied up by a knot of knotches.
    
    Q: Why do Chinese men laugh when circumcised?
    A: This is how they greet the penis, not theirs.
    
    Q: Who is Mario?
    A: More of a dictator who can watch video games while hiding in secrets.

And sometimes...


    Q: What does the man and an egg sandwich have in common?
    A: They both have eggs.

    Q: What do you call a person that has a fetish for cheese?
    A: A cheetah.

    Q: What's the most popular food at a gay barbecue?
    A: KFC.

    Q: Where do poor people live?
    A: In India.

### References
1) https://github.com/huggingface/transformers/issues/401 - Transformers package "How can I generate new text after having fine-tuned BERT on a custom dataset?" issue discussion.
2) https://arxiv.org/pdf/1902.04094.pdf - BERT has a Mouth, and It Must Speak: BERT as a Markov Random Field Language Model
3) https://rajpurkar.github.io/SQuAD-explorer/ - SQuAD - The Stanford Question Answering Dataset
4) https://www.kaggle.com/jiriroz/qa-jokes - Kaggle. Question-Answer Jokes
5) https://github.com/FrogTravel/PMLDL - Our Github repository


## Sprint 4
### Burndown chart 
![](https://i.imgur.com/TAce2qR.png)
storypoints on vertical x days on horizontal axis
Blue - ideal burndown, Green - our result
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
