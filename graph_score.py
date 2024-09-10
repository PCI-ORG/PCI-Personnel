import pandas as pd
import datetime
import json
import os
from utils import load_namelist

# For plotting offline, use plotly directly:
import plotly as py 
import plotly.express as px

# Prepare the data for plot and obtain the plot
def plot(name_list, name_list_eng, plot_data, choice, output_path):

    # plot_data['date'] = plot_data['date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))
    legend_names = {f'{name_list_eng[key]}': f'{name_list_eng[key]} ({name_list[key]})' for key in list(name_list.keys())}

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

# Specify the range and choice for ploting
range_start = '20070101'
today = datetime.datetime.now() # Note AWS use UTC!
today = today.strftime('%Y%m%d') 
range_end = today

# Choices for plot at launching: 1. All traces on, 2. All traces off
choice = 1

# Load the data set for plotting
plot_data = '/home/ubuntu/PCI-Personnel/results/PCI-personnel.csv'

if not os.path.exists(plot_data):
    print("file does not exist")

else:
    plot_data = pd.read_csv(plot_data)
    plot(name_list, name_list_eng, plot_data, choice, output_path)