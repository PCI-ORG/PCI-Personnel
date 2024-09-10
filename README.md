Updated on 05 Sep, 2024

## 1. What is PCI Personnel Analysis?

The goal of the PCI Personnel Analysis is to understand the relationship between different Chinese politicial officiers and the Chinese President, Xi Jinping. 
Numerical models and indicators are introduced to quantify the relationship and its change as a function of time. The plot of our current results can be found here:
https://gearfactory-ai.github.io/PCI-personnel-plot/

## 2. The design

The pipeline consists of the following five steps:

1. Data extraction: Taking input data from the full text of the People's Daily --- the official newspaper of the Communist Party of China. 

2. Data preparation: Selecting all news articles that involve the targeted person and President Xi Jinping.
   The article query is performed using article_query.py in the repository. 

3. Data analysis: Employing large language models (LLM) to assign a score of -5 to +5 for the relationship between the targeted person and President Xi as revealed from
   the content of articles. For each person, the LLM analysis is implemented separately for every selected news article in Step 2.
   This is performed using LLM_analysis.py in the repository. 

4. Modelling: Calculating a numerical index to quantify the change in relationship (also known as public images as preceived from the People's Daily).
   This calculation is performed using cumulative_score.py in the repository. In Section 3 below, a more detailed description of the model will be provided.

5. Data visualization: Plotting and deploying the result. The graph for the numerical index (public images as preceived from the People's Daily) is obatined from graph_score.py
   in the repository. The graph is then deployed on https://gearfactory-ai.github.io/PCI-personnel-plot/ 

The config folder in the repository contains the name list (both Chinese and English names) of the targetted personnel, and the prompts being used in the LLM analysis. 
They can be updated in future applications. The main.py automates the above pipeline and deployment procedure. This python code is ran on our private AWS EC2 server. 
Regular update is achieved by using other AWS cloud computing services.

## 3. The model of numerical index (public images as preceived from the People's Daily)

The model consists of the following parameters:

- Decay factor: 0.99
- Double count factor: 1

Each person started with an index of 0 on the date 01 Jan, 2001. On a day when both the person and President Xi were mentioned in any news article, 
the numerical index for the person is adjusted by the score obtained from the LLM analysis. Meanwhile, the index is multiplied to the decay factor when no news article was found. 
The same article (i.e., same title and same body) might be published more than once in People's Daily but on different pages. 
In this case, LLM analysis will assign the same score to all these articles. All these scores will be used to adjust the numerical index if the double count factor is set to 1. 
To prevent such a double or multiple counting, the double count factor should be set to 0. Both decay factor and double count factor can be changed in cumulative_score.py.

## 4. Examples

To check our model, we plotted the results for all 28 people in the name list. The indices obtained for Wang Yi, Qin Gang, Bo Xilai, and Wang Huning 
suggested that our model gives a highly reasonable trend.

## 5. Limitations and Outlook

In the future, we plan to 

(1) Include name entity recogniition (NER) before performing LLM analysis. This step is crucial in obtaining a more relevant selection of news articles 
and a more accurate score from the LLM analysis. For example, we noticed that there is a reporter whose name is also "Li Qiang". 
Furthermore, our article query process may return irrelevant articles that actually involve names or objects "Li Qiang Guo", "Ba Wang Yi", etc.

(2) Some people may have low indices, but they are actually gaining power. For example, Dong Jun and Zhang Youxia. 
This discrepancy may appear if the people are in the military department, so that few news of them are published in People's Daily. 
It will be useful to include other newspaper as well. 

(3) Improve the model to have a better index which can be **predictive**. 
For example, introduce an anomaly indicator which can predict a possible power gaining or losing of different people. 
Our plan is to improve the model and change the news_count plot (not yet deployed) to an anomaly indicator plot.
