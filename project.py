import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt


@st.experimental_singleton(suppress_st_warning=True)
def init_connection():
    CONNECTION_STRING = "mongodb+srv://<usrname>:<pwd>@cluster0.p2rhw80.mongodb.net/test"
    client = MongoClient(CONNECTION_STRING)
    return client


client = init_connection()
db = client.aat_project
all_items = list(db.covid.find())

pipeline1 = [
    {
        "$group":
        {
            "_id": "$State/UnionTerritory",
            "total_deaths": {"$sum": "$Deaths"},
            "total_cured": {"$sum": "$Cured"}
        }
    },
    {
        "$sort":
        {
            "_id": 1
        }
    }
]

pipeline2 = [
    {
        "$group":
        {
            "_id": "$State/UnionTerritory",
            "total_deaths": {"$sum": "$Deaths"},
            "total_cured": {"$sum": "$Cured"}
        }
    },
    {"$match":
        {
            "$expr": {
                "$gt": ["$total_cured", "$total_deaths"]
            }
        }
     },
    {
        "$sort":
        {
            "_id": 1
        }
    }
]

state_wise_deaths = list(db.covid.aggregate(pipeline1))
more_cured = list(db.covid.aggregate(pipeline2))

pipeline3 = [
    {
        "$group":
        {
            "_id": "$Date",
            "total_deaths": {"$sum": "$Deaths"},
            "total_cured": {"$sum": "$Cured"}
        }
    },
    {
        "$sort":
        {
            "_id": 1
        }
    }
]

date_wise_dataset = list(db.covid.aggregate(pipeline3))

st.title("Covid-19 Region-Wise Analysis")
st.text("This is an in-depth analysis of covid cases in India. The analysis is done State-wise as well as with respct to dates.")

wanted_keys = ("Date", "State/UnionTerritory", "Cured", "Deaths", "Confirmed")


def filtered_data(items, keys):
    diseases_dataset = dict()
    for key in keys:
        diseases_dataset[key] = []
    for item in items:
        for key in keys:
            diseases_dataset[key].append(item[key])
    return diseases_dataset


st.header("Covid-19 Region-Wise Analysis Dataset")
st.dataframe(pd.DataFrame(filtered_data(all_items, wanted_keys)))

st.header("State-Wise covid-19 Total Deaths and Total Cured Persons")
st.dataframe(pd.DataFrame(filtered_data(
    state_wise_deaths, ["_id", "total_deaths", "total_cured"])))

st.header("States Where Total Cured Cases is Greater than Total Deaths")
st.dataframe(pd.DataFrame(filtered_data(
    more_cured, ["_id", "total_deaths", "total_cured"])))

st.header("Date-Wise covid-19 Total Deaths and Total Cured Persons")
st.dataframe(pd.DataFrame(filtered_data(
    date_wise_dataset, ["_id", "total_deaths", "total_cured"])))

dates = filtered_data(date_wise_dataset, [
                      "_id", "total_deaths", "total_cured"])["_id"]
date_deaths = filtered_data(date_wise_dataset, [
    "_id", "total_deaths", "total_cured"])["total_deaths"]

for i in range(len(dates)):
    dates[i] = dates[i].strftime('%m-%d-%Y')

st.header("Graphical Representation of Date vs. No. of Deaths")
fig, ax = plt.subplots()
ax.plot(date_deaths)
ax.set_xticklabels(dates, rotation=90)
ax.set_title("date(x-axis) vs. no. of deaths(y-axis)")
st.pyplot(fig)
