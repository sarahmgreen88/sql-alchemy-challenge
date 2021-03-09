import numpy as np

import sqlalchemy
import datetime as dt
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station
session = Session(bind = engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# * `/`
#   * Home page.
#   * List all routes that are available.
@app.route("/")
def welcome():
    return (f"Surfs up! Welcome to the Hawaii Weather API!<br/><br/> "
            f"Available Routes: <br/><br/>"
            f"/api/v1.0/precipitation<br/>This route returns data from the percipitation between the dates of 08-23-2016 and 08-23-2017.<br/> <br/>"
            f"/api/v1.0/stations<br/> This route returns information about the number of weather reports for each of the stations in the data. <br/><br/>"
            f"/api/v1.0/tobs<br/>This route gives you information on the most active stations temperature ranges.<br/><br/>"
            f"/api/v1.0/<start> and /api/v1.0/<start>/<end><br/>This route calculates the minimum temperature, maximum temperature and the average temperature of a given start and end date.")

#   * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
#   * Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    past_year = (dt.datetime.strptime(most_recent, "%Y-%m-%d")) - dt.timedelta(days=365)
    precp_scores = session.query(measurement.date, measurement.prcp).filter(measurement.date>= past_year).order_by(measurement.date).all()

    return jsonify(precp_scores)

#   * Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(station.station, station.name)
    all_stations = pd.read_sql(stations.statement, stations.session.bind)
    return jsonify(all_stations.to_dict())

#   * Query the dates and temperature observations of the most active station for the last year of data.
#   * Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def temperature():
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    past_year = (dt.datetime.strptime(most_recent, "%Y-%m-%d")) - dt.timedelta(days=365)
    most_active = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    active_station = most_active[0][0]
    temp_best = session.query(measurement.station, measurement.tobs, measurement.date).filter(measurement.station == active_station).filter(measurement.date >= past_year).all()
    # temp = session.query(measurement.date, measurement.tobs).filter(measurement.date>= past_year).order_by(measurement.date).all()
    return jsonify(temp_best)

# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
@app.route("/api/v1.0/<date>")
def StartDate(date):
    return jsonify(session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= date).all())

@app.route("/api/v1.0/<start>/<end>")
def StartDateEndDate(start, end):
    return jsonify(session.query(func.min(measurement.tobs), func.avg(measurement.tobs). func.max(measurement.tobs)).filter(measurment.date>=start).filter(measurement.date<=end).all())

#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

session.close()  
if __name__ == '__main__':
    app.run(debug=True)
