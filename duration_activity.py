from datetime import datetime


def _check_duration(location_history, activity):
    """Checks if the activity is no longer than 24 hours
    Args:
        location_history (dict): Google Semantic Location History data
        activity: the activity type of interest
    Returns:
        count: times requirement not met
    """
    count = 0
    for data_unit in location_history["timelineObjects"]:
        if "activitySegment" in data_unit.keys():
            if data_unit["activitySegment"]["activityType"]:
                start_time = data_unit["activitySegment"]["duration"]["startTimestamp"]
                end_time = data_unit["activitySegment"]["duration"]["endTimestamp"]
                start_time = _test_time_format(start_time)
                end_time = _test_time_format(end_time)
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                if ((end_time - start_time) / (60 * 60)) > 24:
                    count += 1
    return count


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
