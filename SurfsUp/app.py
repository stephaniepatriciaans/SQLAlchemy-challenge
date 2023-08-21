from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

app = Flask(__name__)

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Define route for the homepage
@app.route("/")
def welcome():
    return (
        "Available Routes for Hawaii Weather Data:\n\n"
        "- Precipitation Data for the Last Year: /api/v1.0/precipitation\n"
        "- List of Active Weather Stations: /api/v1.0/stations\n"
        "- Temperature Observations for Last Year (Station USC00519281): /api/v1.0/tobs\n"
        "- Min, Avg, and Max Temperatures for a Date Range: /api/v1.0/start_date/end_date\n"
        "NOTE: If no end-date is provided, the query assumes end_date=2017-08-23\n" 
    )

# Precipitation query function
@app.route("/api/v1.0/precipitation")
def get_precipitation():
    try:
        session = Session(engine)
        start_date = '2016-08-23'
        data = session.query(Measurement.date, func.sum(Measurement.prcp)).\
            filter(Measurement.date >= start_date).\
            group_by(Measurement.date).all()
        session.close()

        precipitation_dict = dict(data)
        return jsonify(precipitation_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Stations query function
@app.route("/api/v1.0/stations")
def get_stations():
    try:
        session = Session(engine)
        stations = session.query(Station.station, Station.name).all()
        session.close()

        station_list = [{"station": station, "name": name} for station, name in stations]
        return jsonify(station_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Station temperatures query function
@app.route("/api/v1.0/tobs")
def get_tobs():
    try:
        session = Session(engine)
        start_date = '2016-08-23'
        data = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date >= start_date, Measurement.station == 'USC00519281').all()
        session.close()

        temp_list = [{"date": date, "tobs": tobs} for date, tobs in data]
        return jsonify(temp_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to calculate temperature statistics for a date range
def calculate_temps(start_date, end_date='2017-08-23'):
    try:
        session = Session(engine)
        query_result = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
        session.close()

        min_temp, avg_temp, max_temp = query_result[0]
        temp_stats = {
            "Min Temperature": min_temp,
            "Average Temperature": avg_temp,
            "Max Temperature": max_temp
        }

        return temp_stats

    except Exception as e:
        return {"error": str(e)}

# Route for temperature statistics for a date range
@app.route("/api/v1.0/<start_date>/<end_date>")
def get_temp_stats(start_date, end_date='2017-08-23'):
    temp_stats = calculate_temps(start_date, end_date)

    if "error" in temp_stats:
        return jsonify({"error": temp_stats["error"]}), 400

    return jsonify(temp_stats)

# Debug
if __name__ == '__main__':
    app.run(debug=True)
