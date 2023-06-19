import warnings
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from functools import partial
import pyproj
from shapely.ops import transform

warnings.filterwarnings('ignore')


def _create_coordinates(coord_csv):
    """Transforms the public transport stations and stops to EPSG 4326 and EPSG 32634
    Args:
        coord_csv: csv file with public transport x and y coordinates.

    Returns:
        gdf_4326: dataframe of public transport stations with coordinates in EPSG 4326
        gdf_32634: dataframe of public transport stations with coordinates in EPSG 32634
    """
    df = pd.read_csv(coord_csv, delimiter=",")
    gdf_4326 = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['xcoord'], df['ycoord']), crs='EPSG:4326')
    gdf_32634 = gdf_4326.to_crs("EPSG:32634")
    return gdf_4326, gdf_32634


def _transform_coordinates(location_history_unit):
    """Transforms coordinates of the start or end location
    Args:
        location_history_unit: One segment of the Google Semantic Location History data

    Returns:
        start_trans: transformed start coordinates
        end_trans: transformed end coordinates
    """
    start_point = location_history_unit["activitySegment"]["startLocation"]["latitudeE7"] / 10000000, \
                  location_history_unit["activitySegment"]["startLocation"]["longitudeE7"] / 10000000
    end_point = location_history_unit["activitySegment"]["endLocation"]["latitudeE7"] / 10000000, \
                location_history_unit["activitySegment"]["endLocation"]["longitudeE7"] / 10000000
    start_trans = Point(start_point)
    end_trans = Point(end_point)
    project = partial(
        pyproj.transform,
        pyproj.Proj('epsg:4326'),
        pyproj.Proj('epsg:32634'))
    start_trans = transform(project, start_trans)
    end_trans = transform(project, end_trans)
    return start_trans, end_trans


def _check_location(location_history, station_32634, activity):
    """Checks if start or end location is an airport and counts when not
    Args:
        location_history (dict): Google Semantic Location History data
        station_32634: dataframe with EPSG 32634 coordinates of stations
        activity: the activity type of interest

    Returns:
        tot_no_station_count (int): total number of no station found for start or end location
        no_station_count (int): number of times no station was found for both the start and end location
    """
    tot_no_station_count = 0
    no_station_count = 0
    for location_history_unit in location_history["timelineObjects"]:
        if "activitySegment" in location_history_unit.keys():
            if location_history_unit["activitySegment"]["activityType"] == activity:
                start_trans, end_trans = _transform_coordinates(location_history_unit)
                start_count = 0
                end_count = 0
                for station in station_32634.iterrows():
                    station_buffer = station[1][7].buffer(500, join_style=1)
                    if station_buffer.contains(start_trans) and start_count < 1:
                        start_count += 1
                    elif station_buffer.contains(end_trans) and end_count < 1:
                        end_count += 1
                if start_count + end_count <= 1:
                    tot_no_station_count += 1
                if start_count == 0 and end_count == 0:
                    no_station_count += 1
    return tot_no_station_count, no_station_count


def _train_check_location(location_history, train_32634, tram_32634, subway_32634):
    """Checks if start or end location is an train station and counts when not
    Args:
        location_history (dict): Google Semantic Location History data
        train_32634: dataframe with EPSG 32634 coordinates of train stations
        tram_32634: dataframe with EPSG 32634 coordinates of tram stops
        subway_32634: dataframe with EPSG 32634 coordinates of subway stops

    Returns:
        tot_no_train_count: total number of times a start of end location was not a train station
        tot_tram_station: total number of tram stops found
        tot_subway_station: total number of subway stops found
        tram_travel: total number of times tram travel instead of train travel
        subway_travel: total number of times subway travel instead of train travel
        tot_not_train: total number of times both the start and end station was not a train station
        tot_not_station_count: total number of times no other station type was found
    """
    tot_no_train_count = 0
    tot_tram_station = 0
    tot_subway_station = 0
    tram_travel = 0
    subway_travel = 0
    tot_not_train = 0
    tot_not_station_count = 0
    for location_history_unit in location_history["timelineObjects"]:
        if "activitySegment" in location_history_unit.keys():
            if location_history_unit["activitySegment"]["activityType"] == "IN_TRAIN":
                start_trans, end_trans = _transform_coordinates(location_history_unit)
                start_count = 0
                end_count = 0
                tram_count = 0
                subway_count = 0
                for station in train_32634.iterrows():
                    station_buffer = station[1][7].buffer(500, join_style=1)
                    if station_buffer.contains(start_trans) and start_count < 1:
                        start_count += 1
                    elif station_buffer.contains(end_trans) and end_count < 1:
                        end_count += 1
                if start_count == 0:
                    tram_count, subway_count, no_station_count = _station_different_location(start_trans, tram_32634, subway_32634)
                    tot_tram_station += tram_count
                    tot_subway_station += subway_count
                    tot_no_train_count += 1
                    tot_not_station_count += no_station_count
                elif end_count == 0:
                    tram_count, subway_count, no_station_count = _station_different_location(end_trans, tram_32634, subway_32634)
                    tot_tram_station += tram_count
                    tot_subway_station += subway_count
                    tot_no_train_count += 1
                    tot_not_station_count += no_station_count
                elif start_count == 0 and end_count == 0:
                    tot_not_train += 1
                if tram_count > subway_count:
                    tram_travel += 1
                elif subway_count > tram_count:
                    subway_travel += 1
    return tot_no_train_count, tot_tram_station, tot_subway_station, tram_travel, subway_travel, tot_not_train, tot_not_station_count


def _station_different_location(coords, tram_32634, subway_32634):
    """Checks if start or end location is an tram or subway stop and counts when it is
    Args:
        coords: Coordinates start or end location
        tram_32634: dataframe with EPSG coordinates of tram stops
        subway_32634: dataframe with EPSG coordinates of subway stops

    Returns:
        tram_count: number of times start or end location was a tram stop
        subway_count: number of times start of end location was a subway stop
        no_station_count: number times no other type of station was found
    """
    tram_count = 0
    subway_count = 0
    no_station_count = 0
    for tram in tram_32634.iterrows():
        tram_buffer = tram[1][7].buffer(500, join_style=1)
        if tram_buffer.contains(coords):
            tram_count += 1
    for subway in subway_32634.iterrows():
        subway_buffer = subway[1][7].buffer(500, join_style=1)
        if subway_buffer.contains(coords):
            subway_count += 1
    if tram_count == 0 and subway_count == 0:
        no_station_count += 1
    return tram_count, subway_count, no_station_count


def _airport_check_location(location_history, station_32634):
    """Checks if start or end location is an airport and counts when it is
    Args:
        location_history (dict): Google Semantic Location History data

    Returns:
        no_airport_count (int): number of times start or end location was not an airport
    """
    no_airport_count = 0
    for location_history_unit in location_history["timelineObjects"]:
        if "activitySegment" in location_history_unit.keys():
            if location_history_unit["activitySegment"]["activityType"] == "FLYING":
                start_trans, end_trans = _transform_coordinates(location_history_unit)
                start_count = 0
                end_count = 0
                for station in station_32634.iterrows():
                    station_buffer = station[1][7].buffer(500, join_style=1)
                    if station_buffer.contains(start_trans) and start_count < 1:
                        start_count += 1
                    elif station_buffer.contains(end_trans) and end_count < 1:
                        end_count += 1
                if start_count + end_count < 1:
                    no_airport_count += 1
    return no_airport_count
