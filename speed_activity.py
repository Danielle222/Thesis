from datetime import datetime


def _check_speed_requirement(location_history, activity, max_speed):
    """Counts how often the speed requirement of the average speed being lower than the maximum allow speed
    of the activity type is not met
    Args:
        location_history: the Google Semantic Location History in json format of a month
        activity: the activity type of interest
        max_speed (int): the maximum allowed speed of the activity type of interest

    Returns:
        max_count (int): number of times the requirement is not met
    """
    max_count = 0
    for location_history_unit in location_history["timelineObjects"]:
        if "activitySegment" in location_history_unit.keys():
            if "distance" in location_history_unit["activitySegment"]:
                if location_history_unit["activitySegment"]["activityType"] == activity:
                    distance = location_history_unit["activitySegment"]["distance"]
                    start_time = location_history_unit["activitySegment"]["duration"]["startTimestamp"]
                    end_time = location_history_unit["activitySegment"]["duration"]["endTimestamp"]
                    ave_speed = _average_speed(start_time, end_time, distance)
                    if ave_speed > max_speed:
                        max_count += 1
    return max_count


def _average_speed(start_time, end_time, distance):
    """Calculates the average speed of an activity
    Args:
        start_time: the Google Semantic Location History activity segment start timestamp
        end_time: the Google Semantic Location History activity segment end timestamp
        distance (int): the distance of the activity in meters

    Returns:
        (float) the average speed of the activity in km/h
    """
    start_time = _test_time_format(start_time)
    end_time = _test_time_format(end_time)
    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
    duration = ((end_time - start_time) / (60 * 60))
    return (distance / duration) / 1000


def _test_time_format(timestamp):
    """Add milliseconds to the timestamp when necessary
    Args:
        timestamp: the Google Semantic Location History activity segment start or end timestamp

    Returns:
        timestamp: the input timestamp but with milliseconds added
    """
    if len(timestamp) == 20:
        timestamp = timestamp[:len(timestamp) - 1] + ".000" + timestamp[len(timestamp) - 1:]
    return timestamp
