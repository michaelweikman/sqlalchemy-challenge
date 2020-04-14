import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import datetime as dt

app = Flask(__name__)

#I was getting a thread error, found this connect_arg fix, not sure what causes the error need to research later.
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False})

Base = automap_base()
Base.prepare(engine, reflect=True)

Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

#Get most recent date used later
recent_date = session.query(func.Max(Measurement.date)).first()[0]
print(recent_date)
start_date = dt.datetime.strptime(recent_date, '%Y-%m-%d').date() - dt.timedelta(days=365)

@app.route("/")
def home():
    return (
        f"App Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt EX Date format: 2017-01-01<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt EX Date format: 2017-01-01<br/>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, func.avg(Measurement.prcp)).group_by(Measurement.date).all()

    json_result = []
    for date, prcp in results:
        json_result.append({str(date): prcp})
    return jsonify(json_result)

@app.route("/api/v1.0/stations")
def station():
    results = session.query(Station.station).all()

    #Returns list of list, using ravel to return single str list.
    raveled = list(np.ravel(results))
    return jsonify(raveled)

@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.date, func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).group_by(Measurement.date).all()
    json_result = []
    for date, temp in results:
        json_result.append({str(date): temp})
    return jsonify(json_result)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=recent_date):
    print(start)
    if end != recent_date:
        query_end_date = end
    else:
        query_end_date = recent_date

    query_end_date = dt.datetime.strptime(query_end_date, '%Y-%m-%d').date()
    start = dt.datetime.strptime(start, '%Y-%m-%d').date()
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).filter(Measurement.date <= query_end_date).all()[0]
    
    results_list = [{"TMIN": temps[0]}, 
                    {"TAVG": temps[1]}, 
                    {"TMAX": temps[2]}]
    return jsonify(results_list)


if __name__ == "__main__":
    app.run(debug=True)