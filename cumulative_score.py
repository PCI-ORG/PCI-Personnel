import pandas as pd
import datetime
import os
import json
import boto3
from utils import load_namelist, data_selection

# Obtain newspaper score from GPT analysis (if articles exist)
def news_score(news, double_count):
    
    day_score = 0
    
    for n_news in range (0,len(news)):
    
        if n_news==0:
            day_score = news.iloc[0]['rating_1']
        
        else:
            same = int(news.iloc[n_news]['title'] == news.iloc[n_news-1]['title'])

            if same==1:
                day_score = day_score + (double_count * news.iloc[n_news]['rating_1'])
            else:
                day_score = day_score + news.iloc[n_news]['rating_1']
    
    return day_score


# Obtain aggregate score
def aggregate(time_range, df_person, decay_factor, double_count):
    
    cum_score = 0
    df_score = pd.DataFrame()  
    
    column_name = ['date','cum_score','news_score', 'title', 'url']

    for date in time_range:

        date = int(date.strftime('%Y%m%d'))
        news = df_person.loc[df_person["published"]== date]

        if len(news)==0:
            cum_score = cum_score * decay_factor
            gpt_score = 'NA'
            title = 'NA'
            url = 'NA'

        else:
            cum_score = cum_score + news_score(news, double_count)
            gpt_score = ''
            title = ''
            url = ''

            for i in range(0,len(news)):
                gpt_score = '   '.join([gpt_score, str(news.iloc[i]['rating_1'])])
                title = '   '.join([title, news.iloc[i]['title']])
                url = '   '.join([url, news.iloc[i]['url']]) 

            gpt_score = gpt_score.lstrip()
            title = title.lstrip()
            url = url.lstrip()
        
        df_new = pd.DataFrame([[str(date),round(cum_score,2),gpt_score,title,url]], columns=column_name)
        df_score = pd.concat([df_score, df_new],ignore_index=True)
    
    return df_score


########  Main program here  #######

s3 = boto3.client('s3', region_name='us-east-1')

# Note AWS use UTC!
today = datetime.datetime.now()
today = today.strftime('%Y%m%d') 

# Which LLM model to obtain the cumulative score?
# Current possible choices: eng-v1, chi-v1
LLM_model = 'eng-v1'

# Obtain the paths for loading and saving files
with open('/home/ubuntu/PCI-person/config/directory.json', 'r') as f:
    directory = json.load(f)

namelist_path = directory["namelist_path"]
namelist_eng_path = directory["namelist_eng_path"]
s3_bucket = directory["s3_bucket"]

# Load the name list and LLM results 
name_list = load_namelist(namelist_path)
name_list_eng = load_namelist(namelist_eng_path)

start_date = '20010101'
end_date = today
time_range = pd.date_range(start_date, end_date)

'''

# Chose 1 to sum over all scores if the same article appears more than once on the same day. Choose 0 to stop multiple counting
double_count = 1 

# The cumulative score is multiplied by this decay factor if the person had no news that day. Set to 1 for no decay.
decay_factor = 0.99

for person_id in range(1,len(name_list)):

    person = name_list[person_id]

    dataset = directory["LLM_result_local_path"].format(LLM_model = LLM_model, person = person)
    df_person = data_selection(dataset, keep_columns = ["title", "rating_1", "published", "url"])
    df_score = aggregate(time_range, df_person, decay_factor, double_count)

    output_path = directory["score_local_path"].format(LLM_model = LLM_model, person = person)
    df_score.to_csv(output_path, index = False)

    s3_key = directory["score_s3_key"].format(LLM_model = LLM_model, person = person)
    s3.upload_file(output_path, s3_bucket, s3_key)
'''

# Output csv file for the resulting indices of different people

if len(name_list) != len(name_list_eng):
    print("Chinese and English name lists do not match. Please check")
    exit()

df_grand = pd.DataFrame()

for person_id in range (1,len(name_list)):

    person = name_list[person_id]
    person_eng = name_list_eng[person_id]
    data_path = directory["score_local_path"].format(LLM_model = LLM_model, person = person)

    if not os.path.exists(data_path):
        print(f"missing score file for {person_eng}, check again")
        quit()

    else:
        df_person = data_selection(dataset = data_path, keep_columns = ["date", "cum_score"])
        df_person = df_person.rename(columns={"cum_score": f'{person_eng}'})
        df_grand = pd.concat([df_grand, df_person], axis=1)

df_grand = df_grand.astype({'date': 'string'})
df_grand = df_grand.loc[:, ~df_grand.columns.duplicated()]

# Specify the range and choice for ploting
range_start = '20070101'
range_end = today

df_grand = df_grand.loc[(df_grand['date'] >=range_start) & (df_grand['date'] <=range_end)]
df_grand['date'] = df_grand['date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))

df_grand.to_csv('/home/ubuntu/PCI-Personnel/results/PCI-personnel.csv', index = False)