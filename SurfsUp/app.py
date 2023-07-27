# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def homepage():
    return (
        """
        Welcome to the homepage of the Climate API!<br/>
        <br/>
        The following routes are available:<br/>
        /api/v1.0/precipitation  -  the last 12 months of precipitation data<br/>
        /api/v1.0/stations  -  list of stations<br/>
        /api/v1.0/tobs  -  temperature observations of the most-active station for the previous year<br/>
        /api/v1.0/start  -  list of the minimum, average and maximum temperature for a specified start date<br/>
        /api/v1.0/start/end  -  list of the minimum, average and maximum temperature for a specified start-end range<br/>
        """)

@app.route('/api/v1.0/precipitation')
def precipitation_data():
    most_recent = dt.date(2017, 8, 23)
    past_year = most_recent - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= past_year).all()
    precipitation = {date: prcp for date, prcp in results}
    return jsonify(precipitation)


@app.route('/api/v1.0/stations')
def station_data():
    results = session.query(station.station).all()
    station_list = list(np.ravel(results))
    return jsonify(station_list)


@app.route('/api/v1.0/tobs')
def temperature_data():
    most_recent = dt.date(2017, 8, 23)
    past_year = most_recent - dt.timedelta(days=365)
    results = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= past_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps)


@app.route(f'/api/v1.0/<start>')
def start_date(start):
    data = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    results = session.query(*data).filter(measurement.date >= start).all()
    temps = list(np.ravel(results))
    return jsonify(temps)
    

@app.route(f'/api/v1.0/<start>/<end>')
def date_range(start, end):
    data = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    results = session.query(*data).filter(measurement.date >= start).filter(measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)   

if __name__ == '__main__':
    app.run(debug=True)
