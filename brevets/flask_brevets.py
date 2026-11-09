"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times for one control.
    Expects URL arguments: km, brevet_dist_km, begin_date (YYYY-MM-DD),
    begin_time (HH:mm). Returns JSON with ISO 8601 formatted open and close times,
    or an error message with status 400 if the input is invalid.
    """
    km = request.args.get('km', type=float)
    brevet_dist_km = request.args.get('brevet_dist_km', 200, type=int)
    begin_date = request.args.get('begin_date', '', type=str)
    begin_time = request.args.get('begin_time', '', type=str)
    app.logger.debug("km={} brevet={} start={} {}".format(
        km, brevet_dist_km, begin_date, begin_time))

    if km is None:
        return flask.jsonify(error="Enter a number for the control distance"), 400

    try:
        start = arrow.get(begin_date + "T" + begin_time).isoformat()
        open_time = acp_times.open_time(km, brevet_dist_km, start)
        close_time = acp_times.close_time(km, brevet_dist_km, start)
    except ValueError as e:
        return flask.jsonify(error=str(e)), 400

    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)



#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
