# -*- coding: utf-8 -*-
"""
@author: Shivraj Patil

"""


import plotly.graph_objects as go
from  plotly.subplots import make_subplots
import pandas as pd
import requests
from datetime import datetime

raw= requests.get("https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/Coronavirus_2019_nCoV_Cases/FeatureServer/1/query?where=1%3D1&outFields=*&outSR=4326&f=json")
data = raw.json()
df = pd.DataFrame(data["features"])

data_list = df['attributes'].tolist()
df_final = pd.DataFrame(data_list)
df_final.set_index('OBJECTID')
df_final = df_final[["Country_Region", "Province_State", "Lat", "Long_", "Confirmed", "Deaths", "Recovered", "Last_Update"]]
df_final.head()

def convertTime(t):
    t = int(t)
    return datetime.fromtimestamp(t)

df_final = df_final.dropna(subset=["Last_Update"])
df_final["Province_State"].fillna(value="", inplace=True)
df_final["Last_Update"] = df_final["Last_Update"]/1000
df_final["Last_Update"] = df_final["Last_Update"].apply(convertTime)
df_final.head()


df_total = df_final.groupby("Country_Region", as_index=False).agg({ 
        "Confirmed": "sum",
        "Deaths": "sum",
        "Recovered": "sum"})


df_total.head()


# GLobal level
total_Confirmed = df_final["Confirmed"].sum()
total_Deaths = df_final["Deaths"].sum()
total_Recovered = df_final["Recovered"].sum()


# Top 10 countries level
df_top_10 = df_final.nlargest(10,columns=["Confirmed"])
top10_countries_1 = df_top_10["Country_Region"].tolist()
top10_confirmed = df_top_10["Confirmed"].tolist()


df_top_10 = df_final.nlargest(10,columns=["Recovered"])
top10_countries_2 = df_top_10["Country_Region"].tolist()
top10_Recovered = df_top_10["Recovered"].tolist()



df_top_10 = df_final.nlargest(10,columns=["Deaths"])
top10_countries_3 = df_top_10["Country_Region"].tolist()
top10_Deaths = df_top_10["Deaths"].tolist()


fig = make_subplots(
    rows=4,
    cols=6,
    specs=[
        [{"type": "scattergeo", "rowspan": 4, "colspan": 3}, None, None, {"type": "indicator"}, {"type": "indicator"},
         {"type": "indicator"}],
        [None, None, None, {"type": "bar", "colspan": 3}, None, None],
        [None, None, None, {"type": "bar", "colspan": 3}, None, None],
        [None, None, None, {"type": "bar", "colspan": 3}, None, None],
    ]
)
    
    
message = df_final["Country_Region"] + "" + df_final["Province_State"] + "<br>"
message += "Confirmed: " + df_final["Confirmed"].astype(str) + "<br>"
message += "Deaths: " + df_final["Deaths"].astype(str) + "<br>"
message += "Recovered: " + df_final["Recovered"].astype(str) + "<br>"
message += "Last_Update: " + df_final["Last_Update"].astype(str) + "<br>"
df_final["text"] =  message

fig.add_trace(
        go.Scattergeo(
                locationmode="country names",
                lon=df_final["Long_"],
                lat=df_final["Lat"],
                hovertext=df_final["text"],
                showlegend=False,
                marker=dict(
                        size=10,
                        opacity =0.8,
                        reversescale = True,
                        autocolorscale = True,
                        symbol = 'square',
                        line = dict(
                                width = 1,
                                color = 'rgba(102,102,103)'
                                ),
                        cmin = 0,
                        color = df_final["Confirmed"],
                        cmax = df_final["Confirmed"].max(),
                        colorbar_title = 'Confirmed Cases<br>Latest Update',
                        colorbar_x = -0.05
                        )
                ),
                row=1,
                col=1
            )

fig.add_trace(
        go.Indicator(
                mode="number",
                value=total_Confirmed,
                title="Confirmed Cases"),
        row=1,
        col=4
        )
        
fig.add_trace(
        go.Indicator(
                mode="number",
                value=total_Recovered,
                title="Recovered Cases"),
        row=1,
        col=5
        )

fig.add_trace(
        go.Indicator(
                mode="number",
                value=total_Deaths,
                title="Deaths Cases"),
        row=1,
        col=6
        )


fig.add_trace(
        go.Bar(
                x=top10_countries_1,
                y=top10_confirmed,
                name="Confirmed Cases",
                marker=dict(color="Orange"),
                showlegend=True),
        row=2,
        col=4
        )


fig.add_trace(
        go.Bar(
                x=top10_countries_2,
                y=top10_Recovered,
                name="Recovered Cases",
                marker=dict(color="Green"),
                showlegend=True),
        row=3,
        col=4
        )

fig.add_trace(
        go.Bar(
                x=top10_countries_3,
                y=top10_Deaths,
                name="Deaths Cases",
                marker=dict(color="Red"),
                showlegend=True),
        row=4,
        col=4
        )



fig.update_layout(
    template="plotly_dark",
    title = "Global COVID-19 Cases (Last Updated: " + str(df_final["Last_Update"][0]) + ")",
    showlegend=True,
    legend_orientation="h",
    legend=dict(x=0.65, y=0.8),
    geo = dict(
            projection_type="orthographic",
            showcoastlines=True,
            landcolor="white", 
            showland= True,
            showocean = True,
            lakecolor="LightBlue"
    ),

    annotations=[
        dict(
            text="Source: https://bit.ly/3aEzxjK",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.35,
            y=0)
    ]
)
    
fig.write_html('covid-19.html', auto_open=True)

    