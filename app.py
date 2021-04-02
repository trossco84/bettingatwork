import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input,Output
import plotly.express as px

# VALID_USERNAME_PASSWORD_PAIRS = [
#     ['xpyragt-a', 'Cooper.777'],
#     ['xpyragt-a', 'cooper.777'],
#     ['tross', 'admin']
# ]

#data folder is weekly outputs, eventually be able to filter on this
#for now:
# wiq = pd.read_csv('https://raw.githubusercontent.com/trossco84/TrevorRoss/master/Sports%20Science/betatwork/weekly_outputs/3_22_2021')
# wiq2 = wiq.copy()
# wiq2.set_index('Player',inplace=True)
# wiq2['Totals'] = [wiq2.loc[x].Amount if wiq2.loc[x].Action == "Request" else (wiq2.loc[x].Amount*(-1)) for x in wiq2.index]
# wiq2.reset_index(inplace=True)
# agent_totals = wiq2.drop(['Amount'],axis=1).groupby('Agent').sum().reset_index()


#create data
totals = pd.read_csv('https://raw.githubusercontent.com/trossco84/TrevorRoss/master/Sports%20Science/betatwork/agent_totals.csv')
raws = pd.read_csv('https://raw.githubusercontent.com/trossco84/TrevorRoss/master/Sports%20Science/betatwork/raw_archives.csv')
last_week = raws.Week.max()
lw_data = raws[raws.Week == last_week]
raw2 = raws.copy()


#overall revenue
overall = totals.reset_index()

#growth
growth = raw2[['Week',"Number of Players","Final Balance"]]
g2 = growth.groupby('Week').sum().reset_index()
g2['Revenue'] = [g2.iloc[:x]['Final Balance'].sum() for x in g2.index]
g2['Number of Players'][0:4] = [5,17,10,14]
totalrevenue = "${:,.2f}".format(g2.iloc[-1].Revenue)
bestweek = "${:,.2f}".format(g2['Final Balance'].max())
worstweek = "${:,.2f}".format(g2['Final Balance'].min())
totalfees = pd.read_csv('https://raw.githubusercontent.com/trossco84/TrevorRoss/master/Sports%20Science/betatwork/totalfees.txt').columns[0]
fees = int(totalfees)
profit = g2.iloc[-1].Revenue - fees
total_profit = "${:,.2f}".format(profit)
blue62 = raw2.groupby('Agent').sum()
b62 = pd.DataFrame(((.6)*blue62['Expected Balance']) * ((.4)*blue62['Number of Players']),columns=['Rank'])
topagent = b62.Rank.idxmax()

# colorscales = px.colors.named_colorscales()
# my_colors = 'Plotly3 Turbo Bluered GnBu dense algae Tealgrn Purp'.split()
# colors = [color for color in colorscales if color in my_colors ]

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash( __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server

app.title= 'RapiDash'
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
# app.layout = html.Div(
#     children=[
#         html.Div(children=[
#                 html.Img(src="https://raw.githubusercontent.com/trossco84/TrevorRoss/master/Sports%20Science/logo2.jpg",className="header-img",alt="logo"),
#                 html.H1(
#                     children="", className="header-title"
#                 ),
#                 html.P(
#                     children="Agent Dashboard for Betting at Work",
#                     className="header-description",
#                 ),
#                 html.P(
#                     children="",
#                     className="header-description",
#                 ),
#                 dcc.Dropdown(
#                     id='DataFilter',
#                     options=[
#                         {'label': 'Overall Revenue', 'value': 'OR'},
#                         {'label': 'Average Players per Week','value':'AP'},
#                         {'label': 'Average Revenue per Week', 'value': 'AR'}
#                         ],
#                         value='OR',
#                         clearable=False,
#                         className='dropdown',
#                         )
#             ],
#             className="header",
#         ),
#     dcc.Graph(
#         id='OverallGraph',
#         className='card'
#     ),
# ]
# )


app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.Img(className="logo", src="https://raw.githubusercontent.com/trossco84/TrevorRoss/master/Sports%20Science/logo2.jpg"),
                        html.H2("Agent Dashboard for Betting at Work"),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.Dropdown(
                                    id='DataFilter',
                                    options=[
                                        {'label': 'Overall Revenue', 'value': 'OR'},
                                        {'label': 'Average Players per Week','value':'AP'},
                                        {'label': 'Average Revenue per Week', 'value': 'AR'}
                                        ],
                                        value='OR',
                                        clearable=False,
                                        className='dropdown',
                                        )
                                        ],
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.Dropdown(
                                    id='GrowthFilter',
                                    options=[
                                        {'label': 'Weekly Revenue', 'value': 'RG'},
                                        {'label': 'Weekly Players', 'value': 'PG'},
                                        {'label': 'Total Revenue Growth','value':'TG'}
                                        ],
                                        value='TG',
                                        clearable=False,
                                        className='dropdown',
                                        )
                                        ],
                        ),
                        html.Div(
                            children=[
                            html.H5(f"Total Profit: {total_profit}"),
                            html.H5(f"Best Week: {bestweek}"),
                            html.H6(f"Worst Week: {worstweek}")
                            ]
                        ),
                        html.Div(
                            children=[
                            html.H2(f"Top Agent: {topagent}"),
                            html.P(f" - top agent defined as a combination of revenue and players")]
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="OverallGraph"),
                        dcc.Graph(id="GrowthGraph")
                    ]
                )
            ]
        )
    ]    
)



@app.callback(
    [Output("OverallGraph","figure"),Output("GrowthGraph","figure")],
    [
        Input("DataFilter","value"),
        Input("GrowthFilter","value")
    ],
)


def update_overall(selectedfilter1,selectedfilter2):
    if selectedfilter1 == 'OR':
        oGraph2 = px.bar(overall,x='Agent',y='Total Revenue',color='Total Revenue',color_continuous_scale='dense')
        oGraph2.update_layout({
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
                },
            'title': 'Total Revenue'
        })
        OverallGraph_figure = oGraph2
        # OverallGraph_figure = {
        #     'data':[
        #         {
        #             'x':overall.Agent,
        #             'y':overall['Total Revenue'],
        #             'type':'bar'
        #         }
        #     ],
        #     'layout': {
                # 'plot_bgcolor': colors['background'],
                # 'paper_bgcolor': colors['background'],
                # 'font': {
                #     'color': colors['text']
                # },
                # 'title': 'Total Revenue'
        #         },
        #     }
    elif selectedfilter1 =='AP':
        oGraph2 = px.bar(overall,x='Agent',y='Avg Players per Week',color='Avg Players per Week',color_continuous_scale='dense')
        oGraph2.update_layout({
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
                },
            'title': 'Average Players Per Week'
        })
        OverallGraph_figure = oGraph2

        # OverallGraph_figure = {
        #     'data':[
        #         {
        #             'x':overall.Agent,
        #             'y':overall['Avg Players per Week'],
        #             'type':'bar'
        #         }
        #     ],
        #     'layout': {
        #         'plot_bgcolor': colors['background'],
        #         'paper_bgcolor': colors['background'],
        #         'font': {
        #             'color': colors['text']
        #         },
        #         'title': 'Average Players Per Week'
        #         },
        #     }
    elif selectedfilter1 == 'AR':
        oGraph2 = px.bar(overall,x='Agent',y='Avg Revenue per Week',color='Avg Revenue per Week',color_continuous_scale='dense')
        oGraph2.update_layout({
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
                },
            'title': 'Average Revenue Per Week'
        })
        OverallGraph_figure = oGraph2
        
        # OverallGraph_figure = {
        #     'data':[
        #         {
        #             'x':overall.Agent,
        #             'y':overall['Avg Revenue per Week'],
        #             'type':'bar'
        #         }
        #     ],
        #     'layout': {
        #         'plot_bgcolor': colors['background'],
        #         'paper_bgcolor': colors['background'],
        #         'font': {
        #             'color': colors['text']
        #         },
        #         'title': 'Average Revenue Per Week'
        # },
        # }

    if selectedfilter2 == 'RG':
    
        gg2 = px.line(g2,x='Week',y='Final Balance')
        gg2.update_layout({
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
                },
            'title': 'Revenue per Week'
        })
        GrowthGraph_figure = gg2
            # GrowthGraph_figure = {
            # 'data':[
            #     {
            #         'x':g2['Week'],
            #         'y':g2['Final Balance'],
            #         'type':'line'
            #     }
            # ],
            # 'layout': {
            #     'plot_bgcolor': colors['background'],
            #     'paper_bgcolor': colors['background'],
            #     'font': {
            #         'color': colors['text']
            #     },
            #     'title': 'Revenue per Week'
            #     },
            # }
    elif selectedfilter2 =='PG':
        gg2 = px.line(g2,x='Week',y='Number of Players')
        gg2.update_layout({
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
                },
            'title': 'Number of Players per Week'
        })
        GrowthGraph_figure = gg2
        
        # GrowthGraph_figure = {
        #     'data':[
        #         {
        #             'x':g2['Week'],
        #             'y':g2['Number of Players'],
        #             'type':'line'
        #         }
        #     ],
        #     'layout': {
        #         'plot_bgcolor': colors['background'],
        #         'paper_bgcolor': colors['background'],
        #         'font': {
        #             'color': colors['text']
        #         },
        #         'title': 'Players per Week'
        #         },
        #     }
    elif selectedfilter2=='TG':
        gg2 = px.line(g2,x='Week',y='Revenue')
        gg2.update_layout({
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
                },
            'title': 'Total Revenue Growth'
        })
        GrowthGraph_figure = gg2


        # GrowthGraph_figure = {
        #     'data':[
        #         {
        #             'x':g2['Week'],
        #             'y':g2['Revenue'],
        #             'type':'line'
        #         }
        #     ],
        #     'layout': {
        #         'plot_bgcolor': colors['background'],
        #         'paper_bgcolor': colors['background'],
        #         'font': {
        #             'color': colors['text']
        #         },
        #         'title': 'Total Revenue Growth'
        #         },
        #     }        
    
    return OverallGraph_figure,GrowthGraph_figure
    


if __name__ == '__main__':
    app.run_server(debug=True)


#   style={'backgroundColor': colors['background']}, 
    # dcc.Graph(
#         id='Graph1',
#         figure={
#             'data': [
#                 {'x': ['Trev'], 'y': [700], 'type': 'bar', 'name': 'Trev'},
#                 {'x': ['Gabe'], 'y': [300], 'type': 'bar', 'name': 'Gabe'},
#             ],
            # 'layout': {
            #     'plot_bgcolor': colors['background'],
            #     'paper_bgcolor': colors['background'],
            #     'font': {
            #         'color': colors['text']
            #     }
#             }
#         }
#     )
# ]

# dcc.Dropdown(
#     options=[
#         {'label': 'New York City', 'value': 'NYC'},
#         {'label': 'Montréal', 'value': 'MTL'},
#         {'label': 'San Francisco', 'value': 'SF'}
#     ],
#     value='MTL'
# )

                # html.Img(src="/Users/trevorross/Desktop/My Projects/bettingatwork/dashboard/assets/logo2.jpg",className="header-img",alt="logo")
                # html.H1(
                #     children="RapiDash", className="header-title"
                # ),
                # html.P(
                #     children="Agent Dashboard for Betting at Work",
                #     className="header-description",
                # )