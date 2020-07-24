#Climate App
from flask import Flask, jsonify

import numpy as np
import sqlalchemy
from matplotlib import style
style.use('fivethirtyeight')

import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from scipy import stats

#Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine,reflect=True)

#Tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask
app = Flask(__name__)

#Climate App
@app.route("/")
def homepage():
    return(
        f"<body>Routes:<br/>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>/api/v1.0/<start></li>"
        f"<li>/api/v1.0/<start>/<end></li>"
        f"</ul></body>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    
    # Calculate the date 1 year ago from the last data point in the database
    lastdate = session.query(func.max(Measurement.date)).scalar()

    oneyearago = dt.date(int(lastdate[0:4]),int(lastdate[6:7]),int(lastdate[9:10])) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= oneyearago).order_by(Measurement.date.desc())

    session.close()
    
    tuples = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(tuples)

@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)
    
    result = session.query(Station.station).all()
    
    session.close()
    
    return jsonify(result)

@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)
    
    station_activity = session.query(Measurement.station,func.count(Measurement.station).label('Count')).group_by(Measurement.station).order_by(desc(func.count(Measurement.station)))

    most_active = station_activity.first()[0]
    most_active_lastdate = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active).scalar()

    most_active_oneyearago = dt.date(int(most_active_lastdate[0:4]),int(most_active_lastdate[6:7]),int(most_active_lastdate[9:10])) - dt.timedelta(days=365)
    
    session.close()
    
    return jsonify(most_active_oneyearago)


@app.route("/api/v1.0/<start>")
def start(start=None):
    
    session = Session(engine)
    
    api_temperatures = (session.query(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    api_temperatures_df = pd.DataFrame(api_temperatures)
    
    session.close()
    
    return jsonify(api_temperatures_df["tobs"].mean(),api_temperatures_df["tobs"].max(),api_temperatures_df["tobs"].min())

@app.route("/api/v1.0/<start>/<end>")
def startandend(start=None, end=None):
    
    session = Session(engine)
    
    api_temperatures = (session.query(Measurement.tobs)).filter(Measurement.date.between(start,end)).all()
    
    api_temperatures_df = pd.DataFrame(api_temperatures)
    
    session.close()
    
    return jsonify(api_temperatures_df["tobs"].mean(),api_temperatures_df["tobs"].max(),api_temperatures_df["tobs"].min())

if __name__ = "main":
    app.run(debug=True)
