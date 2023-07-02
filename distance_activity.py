from haversine import haversine

# The different activity types in the Google Semantic Location History data that are of interest
TRANSPORT = ["IN_TRAIN", "IN_BUS", "IN_TRAM", "IN_SUBWAY", "FLYING"]


def _distance_total(location_history):
    """Calculates the total distances of one month
        Args:
            location_history (dict): Google Semantic Location History data
        Returns:
            tot_dis: the total distance
            tot_wrong_count (int): number of times distance does not meet requirement
        """
    tot_wrong_count = 0
    tot_dis = 0
    wrong_count = 0
    for location_history_unit in location_history["timelineObjects"]:
        if "activitySegment" in location_history_unit.keys():
            if location_history_unit["activitySegment"]["activityType"] in TRANSPORT:
                start_point = location_history_unit["activitySegment"]["startLocation"]["latitudeE7"] / 10000000, \
                              location_history_unit["activitySegment"]["startLocation"]["longitudeE7"] / 10000000
                end_point = location_history_unit["activitySegment"]["endLocation"]["latitudeE7"] / 10000000, \
                            location_history_unit["activitySegment"]["endLocation"]["longitudeE7"] / 10000000
                if "distance" in location_history_unit["activitySegment"]:
                    distance, wrong_count = _distance_compare(start_point, end_point,
                                                              location_history_unit["activitySegment"]["distance"])
                    tot_dis = tot_dis + distance
                else:
                    distance = haversine(start_point, end_point)*1000
                    tot_dis = tot_dis + distance
                tot_wrong_count = tot_wrong_count + wrong_count
    return tot_dis, tot_wrong_count


def _distance_compare(start_point, end_point, distance):
    """Checks if Google Semantic Location History distance is within 5 kilometers of haversine distance
       and counts the times it is not
    Args:
        start_point: start location activity
        end_point: end location activity
        distance: distance activity from Google Semantic Location History
    Returns:
        distance: the distance between start and end location
        count (int): number of times distance does not meet requirement
    """
    count = 0
    haver = haversine(start_point, end_point)
    if (distance/1000) - haver > 5 or (distance/1000) - haver < -5:
        count += 1
        return (haver*1000), count
    else:
        return distance, count
