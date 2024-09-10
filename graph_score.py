import pandas as pd
import datetime
import json
import os
from utils import load_namelist, data_selection

# For plotting offline, use plotly directly:
import plotly as py 
import plotly.express as px

# Prepare the data for plot and obtain the plot
def plot(name_list, name_list_eng, df_grand, range_start, range_end, choice, output_path):

    # list of people to plot
    person_list = [f'{key}' for key in range(1, len(list(name_list.keys())))]

    plot_data = df_grand.loc[(df_grand['date'] >=range_start) & (df_grand['date'] <=range_end)]
    plot_data = pd.concat([plot_data[['date']], plot_data[person_list]],axis=1)
    plot_data['date'] = plot_data['date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))


    legend_names = {f'{key}': f'{name_list_eng[key]} ({name_list[key]})' for key in list(name_list.keys())}

    # plotly express line chart
    fig = px.line(plot_data, x="date", y=plot_data.columns, color_discrete_sequence=px.colors.qualitative.Alphabet)

    fig.for_each_trace(lambda t: t.update(name = legend_names[t.name],
                                        legendgroup = legend_names[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, legend_names[t.name])
                                        )
                    )

    # Disable the traces that are not in the selection
    if choice ==2:
        fig.update_traces(visible='legendonly')

    # Update the layout of the figure
    fig.update_layout(
        
        xaxis_title = '',
        xaxis_tickformat = '%d-%b-%Y',
        yaxis_title = "Daily PCI-Personnel for Top Chinese Politicians",
        legend={
            "y": 0.95,
            "title": "Xi's Personnel"},
        xaxis_rangeslider_visible = False,
    )

    # Add the "select all" and "diselect all" buttons
    fig.update_layout(dict(updatemenus=[
                        dict(
                            type = "buttons",
                            direction = "left",
                            buttons=list([
                                dict(
                                    args=["visible", "legendonly"],
                                    label="Unselect All",
                                    method="restyle"
                                ),
                                dict(
                                    args=["visible", True],
                                    label="Select All",
                                    method="restyle"
                                )
                            ]),
                            pad={"r": 10, "t": 10},
                            showactive=False,
                            x=1.25,
                            xanchor="right",
                            y=1.05,
                            yanchor="top"
                        ),
                    ]
              ))
    
    # html file on local PC to display the plot
    py.offline.plot(fig, filename = output_path)



##### Main part of the code #####

# Obtain the paths for loading and saving files
with open('/home/ubuntu/PCI-person/config/directory.json', 'r') as f:
    directory = json.load(f)

namelist_path = directory["namelist_path"]
namelist_eng_path = directory["namelist_eng_path"]
output_path = directory["plot_score_path"]

name_list = load_namelist(namelist_path)
name_list_eng = load_namelist(namelist_eng_path)

if len(name_list) != len(name_list_eng):
    print("Chinese and English name lists do not match. Please check")
    exit()

# Choose which LLM model's result to plot. Choices now: eng-v1, chi-v1
LLM_model = "eng-v1"

# Prepare and combine data from different people
df_grand = pd.DataFrame()

for person_id in range (1,len(name_list)):

    person = name_list[person_id]
    data_path = directory["score_local_path"].format(LLM_model = LLM_model, person = person)

    if not os.path.exists(data_path):
        print(f"missing score file for {person}, check again")
        quit()

    else:
        df_person = data_selection(dataset = data_path, keep_columns = ["date", "cum_score"])
        df_person = df_person.rename(columns={"cum_score": f'{person_id}'})
        df_grand = pd.concat([df_grand, df_person], axis=1)

df_grand = df_grand.astype({'date': 'string'})
df_grand = df_grand.loc[:, ~df_grand.columns.duplicated()]

# Specify the range and choice for ploting

range_start = '20070101'

today = datetime.datetime.now() # Note AWS use UTC!
today = today.strftime('%Y%m%d') 
range_end = today

# Choices for plot at launching: 1. All traces on, 2. All traces off
choice = 1
plot(name_list, name_list_eng, df_grand, range_start, range_end, choice, output_path)