import pandas as pd
import datetime
import json
import boto3
from utils import *

# Load keys
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

# Choose the model to use for the LLM analysis
model = ChatOpenAI(model="gpt-4o", temperature=0)

# Enter the LLM model here. Choices available now: eng-v1, chi-v1
LLM_model = "eng-v1"

# Define pydantic output variables to output rating (integer) and explanation (string)
from langchain_core.pydantic_v1 import BaseModel, Field


# Setting up the prompt and the structured output class
def prompt_setting(LLM_model, person1, person2, news_title, news_body):

    # Reading the rating question, explanation question, and prompt
    config_file = f'/home/ubuntu/PCI-Personnel/config/LLM-{LLM_model}.json'

    # Check if the config json exists
    if not os.path.exists(config_file):
        print("Config file for the prompt does not exist. Please create it first.")
        exit()

    with open(config_file, 'r') as f:
        setting = json.load(f)

    rating_question = setting["rating_question"].format(p1 = person1, p2 = person2)
    explanation_question = setting["explanation_question"]
    prompt = setting["prompt"].format(p1 = person1, p2 = person2, title = news_title, body = news_body)

    # The structured output class
    class PCI_personnel(BaseModel):
        rating: int = Field(description = rating_question)
        explanation: str = Field(description = explanation_question)

    return prompt, PCI_personnel


# Call GPT for sentiment analysis
def ask_LLM(prompt, sturcutre_output_class):

    structured_llm = model.with_structured_output(sturcutre_output_class)
    output = structured_llm.invoke(prompt)

    rating_LLM = output.__dict__['rating']
    explanation_LLM = output.__dict__['explanation']
    
    return rating_LLM, explanation_LLM


######  Main program here  #####
s3 = boto3.client('s3', region_name='us-east-1')

# Note: AWS use UTC!
today = datetime.datetime.now()
today = today.strftime('%Y%m%d') 

# Obtain the paths for loading and saving files
with open('/home/ubuntu/PCI-Personnel/config/directory.json', 'r') as f:
    directory = json.load(f)

namelist_path = directory["namelist_path"]
s3_bucket = directory["s3_bucket"]
article_date_s3_key = directory["articles_date_s3_key"]
article_local_folder = directory["articles_records_local_folder"]
LLM_date_s3_key = directory["LLM_date_s3_key"].format(LLM_model = LLM_model)
LLM_date_local_path = directory["LLM_date_local_path"].format(LLM_model = LLM_model)
LLM_result_s3_key = directory["LLM_result_s3_key"]
LLM_result_local_path = directory["LLM_result_local_path"]

# Load the name list and last modified date for articles and LLM analysis
name_list = load_namelist(namelist_path)
article_monitor = latest_date(s3_bucket, article_date_s3_key)
LLM_monitor = latest_date(s3_bucket, LLM_date_s3_key.format(LLM_model = LLM_model))


def LLM_compile(n):

    for person_id in range(1,len(name_list)):

        person = name_list[person_id]
        articles_path = f'{article_local_folder}/{person}-articles.csv'
        
        LLM_result_local_path = directory["LLM_result_local_path"].format(LLM_model = LLM_model, person = person)
        LLM_result_s3_key = directory["LLM_result_s3_key"].format(LLM_model = LLM_model, person = person)
        
        status, LLM_latest_date = LLM_action(article_monitor, LLM_monitor, 20010101, today, person, articles_path)

        # Start LLM analysis only if the status is ready!
        if status =='ready':
            print(f'LLM analysis on articles will be performed for {person} with published date after {LLM_latest_date}')

            # Prepare data set from articles, keep_random_rows = None means keeping all rows
            dataset = data_preprocessing(articles_path, LLM_latest_date, keep_only_columns = ["title", "body", "published", "source", "url"], keep_random_rows = None)
            LLM_result_new = dataset.copy()

            for index, row in dataset.iterrows():
                    
                prompt, PCI_personnel_output_class = prompt_setting(LLM_model, person1=name_list[0], person2=person, news_title = row["title"], news_body = row["body"])
                rating_LLM, explanation_LLM = ask_LLM(prompt, sturcutre_output_class = PCI_personnel_output_class)
                LLM_result_new.loc[index, f'rating_{n}'] = rating_LLM
                LLM_result_new.loc[index, f'explanation_{n}'] = explanation_LLM  
    
            if os.path.exists(LLM_result_local_path):
                LLM_result_old = pd.read_csv(LLM_result_local_path)
                LLM_result = pd.concat([LLM_result_old, LLM_result_new], ignore_index=True)
                
            else:
                LLM_result = LLM_result_new
                        
            LLM_result.to_csv(LLM_result_local_path, index=False)
            s3.upload_file(LLM_result_local_path, s3_bucket, LLM_result_s3_key)

# The number of times to ask ChatGPT for analysis for the same article
n_trial = 1

for n in range (1,n_trial+1):
    LLM_compile(n)

# Update the latest date for performing LLM analysis and upload to s3
update_date(LLM_date_local_path, name_list, today)
s3.upload_file(LLM_date_local_path, s3_bucket, LLM_date_s3_key)