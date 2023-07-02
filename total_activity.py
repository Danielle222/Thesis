from datetime import datetime

TRANSPORT = ["IN_TRAIN", "IN_BUS", "IN_TRAM", "IN_SUBWAY", "FLYING"]


def _activity_duration(location_history):
    """Get total duration of activities
    Args:
        location_history (dict): Google Semantic Location History data
    Returns:
        float: duration of activities in days
    """
    activity_duration = 0.0
    count = 0
    for data_unit in location_history["timelineObjects"]:
        if "activitySegment" in data_unit.keys():
            if data_unit["activitySegment"]["activityType"] in TRANSPORT:
                start_time = data_unit["activitySegment"]["duration"]["startTimestamp"]
                end_time = data_unit["activitySegment"]["duration"]["endTimestamp"]
                start_time, start_count = _test_time_format(start_time)
                end_time, end_count = _test_time_format(end_time)
                count = count + start_count + end_count
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                activity_duration += ((end_time - start_time) / (24 * 60 * 60))
    return activity_duration


def _test_time_format(timestamp):
    """Add milliseconds to the timestamp when necessary and counts when this is needed
    Args:
        timestamp: the Google Semantic Location History activity segment start or end timestamp

    Returns:
        timestamp: the input timestamp but with milliseconds added
        count (int): number of times timestamp in wrong format
    """
    count = 0
    if len(timestamp) == 20:
        timestamp = timestamp[:len(timestamp) - 1] + ".000" + timestamp[len(timestamp) - 1:]
        count += 1
    return timestamp, count


def _activity_distance(location_history):
    """Get total distance of activities
    Args:
        location_history (dict): Google Semantic Location History location_history
    Returns:
        float: distance of activities in km
    """
    activity_distance = 0.0
    count = 0
    for location_history_unit in location_history["timelineObjects"]:
        if "activitySegment" in location_history_unit.keys():
            if location_history_unit["activitySegment"]["activityType"] in TRANSPORT:
                dis_count = _test_missing_distance(location_history_unit["activitySegment"])
                count += dis_count
                if "distance" in location_history_unit["activitySegment"]:
                    activity_distance += int(location_history_unit["activitySegment"]["distance"]) / 1000.0
    return activity_distance, count


def _test_missing_distance(location_history_unit):
    """Count number of times distance is missing from the activity segment
    Args:
        location_history_unit (dict): Google Semantic Location History activity segment
    Returns:
        count (int): number of times distance is missing
    """
    count = 0
    if 'distance' not in location_history_unit:
        count = count + 1
    return count


def _activity_count(location_history, activity):
    """Counts how often an activity type was predicted
    Args:
        location_history: the Google Semantic Location History in json format of a month
        activity: the activity type of interest

    Returns:
        count (int): number of times the activity type of interest was predicted
    """
    count = 0
    for activity_segment in location_history["timelineObjects"]:
        if "activitySegment" in activity_segment.keys():
            if activity_segment["activitySegment"]["activityType"] == activity:
                count += 1
    return count

