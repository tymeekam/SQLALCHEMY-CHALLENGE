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
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    # Query all passengers
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    sel = [Measurement.date, Measurement.prcp]
    data_within_1_year = session.query(*sel).\
    filter(Measurement.date >= year_ago_date).all()
    # Save the query results as a Pandas DataFrame and set the index to the date column
    measurements_df = pd.DataFrame(data_within_1_year, columns=['Date','Prcp'])
    measurements_df.set_index('Date', inplace=True)
    # Sort the dataframe by date
    measurements_df.sort_values(by='Date')
    #convert to dicts
    prcp_dict = measurements_df.to_dict()
    #close
    session.close()
    #jsonify
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    # session = Session(engine)
    # Return a JSON list of stations from the dataset.
    station_list = session.query(Station.station,Station.name).all()
    #close
    session.close()
    #jsonify
    results = np.ravel(station_list)
    return jsonify(stations = results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in data set.
    year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    temp_data = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= year_ago_date).all()
    session.close()
    #jsonify
    tobs_info = []
    for date,tobs in temp_data:
        tobs_dic = {}
        tobs_dic["date"] = date
        tobs_dic["tobs"] = tobs
        tobs_info.append(tobs_dic)
    return jsonify(tobs_info)
   
@app.route("/api/v1.0/start")
def start():
    start_date = dt.date(2016, 12, 19)
    # Return JSON list of the min temp, the avg temp, and max temp for a specified start or start-end range
    start = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()
    jsonify_start = list(np.ravel(start))
    return jsonify(jsonify_start)

@app.route("/api/v1.0/<start>/<end>")
def start_end():
    start_date = dt.date(2016, 12, 19)
    end_date = dt.date(2017, 1, 28)
    start_end = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    jsonify_start_end = list(np.ravel(start_end))
    return jsonify(jsonify_start_end)

if __name__ == '__main__':
    app.run(debug=True)  