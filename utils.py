import boto3
import os
import json
import csv 
import pandas as pd

# Load the name list from config json
def load_namelist(file_path):

    if not os.path.exists(file_path):
        print("Namelist file does not exist")
        exit()

    with open(file_path, 'r') as f:
        name_list = json.load(f)
    
    name_list = {int(k):v for k,v in name_list.items()}
    
    return name_list


# Load latest date for article query from monitor file on aws s3
def latest_date(bucket_name, file_key):

    s3 = boto3.client('s3', region_name='us-east-1')
    
    obj = s3.get_object(Bucket = bucket_name, Key = file_key)
    data = obj['Body'].read().decode('utf-8').splitlines(True)
    records = list(csv.reader(data))

    return records


# Update the latest date for articles downloaded for the people
def update_date(file_path, name_list, today):

    os.remove(file_path)

    for person_id in range (1,len(name_list)):

        update = name_list[person_id] + "," + today + "\n"

        with open(file_path, 'a') as f_date:
            f_date.write(update)


# Check latest date and if articles are up-to-date before LLM analysis
def LLM_action(article_datelist, LLM_datelist, date_default, today, person, articles_path):

    article_datelist = pd.DataFrame(article_datelist, columns=['name','latest_date'])
    LLM_datelist = pd.DataFrame(LLM_datelist, columns=['name','latest_date'])
    
    item = LLM_datelist[LLM_datelist['name']==person]

    if len(item) == 0:
        LLM_latest_date = date_default
    
    elif len(item) == 1:
        index = item.index[0]
        LLM_latest_date = item['latest_date'][index]
    
        if str(LLM_latest_date) ==  today:
            status = 0
            print(f'Up-to-date LLM analysis has been performed for {person} already')
            
        else:

            if not os.path.exists(articles_path):
                status = 1
                print(f"No articles found for {person}")
                print(f"Need to download articles for {person} before LLM analysis")

            else:
                download_date = article_datelist[article_datelist['name']==person]
                index = download_date.index[0]
                download_date = download_date['latest_date'][index]

                if str(download_date) != today:
                    status = 2
                    print(f"Articles downloaded for {person} are not up-to-date")
            
                else:
                    status = 'ready'
    else:
        status = 3
        print(f'More than one latest date record for {person}, please check!')
    
    return status, int(LLM_latest_date)

# Data preprocessing for LLM analysis
def data_preprocessing(dataset_path, start_date, keep_only_columns, keep_random_rows):

    dataset = pd.read_csv(dataset_path)
    dataset = dataset[keep_only_columns]
    dataset = dataset[dataset['published'] > start_date]

    if (keep_random_rows != None):
        dataset = dataset.sample(n=keep_random_rows)
    
    return dataset

# Dataframe columns selection
def data_selection(dataset, keep_columns):

    if not os.path.exists(dataset):
        print("file does not exist")

    df_person = pd.read_csv(dataset)
    df_person = df_person[keep_columns]
    
    return df_person