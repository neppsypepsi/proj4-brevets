"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#

SPEED_TABLE = [
    (0, 200, 15, 34),
    (200, 400, 15, 32),
    (400, 600, 15, 30),
    (600, 1000, 11.428, 28),
]
FINISH_CLOSE_HOURS = {
    200: 13.5, 300: 20, 400: 27, 600: 40, 1000: 75
    }

def _clean_distance(control_dist_km, brevet_dist_km):
    if control_dist_km < 0:
        raise ValueError("Control distance can't be negative")
    if control_dist_km > brevet_dist_km * 1.2:
        raise ValueError("Control is more than 20% past the brevet distance")
    if control_dist_km > brevet_dist_km:
        return brevet_dist_km
    return control_dist_km

def _hours_for_distance(dist_km, use_max_speed):
    hours = 0
    for start, end, min_speed, max_speed in SPEED_TABLE:
        km_in_band = min(dist_km, end) - start
        if km_in_band <= 0:
            break
        if use_max_speed:
            speed = max_speed
        else:
            speed = min_speed
        hours += km_in_band / speed
    return hours

def _shift_time(brevet_start_time, hours):
    minutes = round(hours * 60)
    start = arrow.get(brevet_start_time)
    return start.shift(minutes=minutes).isoformat()


        
def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """

    dist = _clean_distance(control_dist_km, brevet_dist_km)
    hours = _hours_for_distance(dist, use_max_speed=True)
    return _shift_time(brevet_start_time, hours)



def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    dist = _clean_distance(control_dist_km, brevet_dist_km)
    if dist >= brevet_dist_km:
        hours = FINISH_CLOSE_HOURS[brevet_dist_km]
    elif dist <= 60:
        hours = dist / 20 + 1
    else:
        hours = _hours_for_distance(dist, use_max_speed=False)
    return _shift_time(brevet_start_time, hours)

