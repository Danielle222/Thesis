"""Script to extract data from Google Semantic History Location zipfile"""
__version__ = '0.1.0'

import json
import re
import zipfile
import pandas as pd
import os

from station_activity import _create_coordinates, _check_location, _train_check_location, _airport_check_location
from speed_activity import _check_speed_requirement
from total_activity import _activity_distance, _activity_duration, _activity_count
from distance_activity import _distance_total
from duration_activity import _check_duration

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

# years and months to extract data for
YEARS = [2017, 2018, 2019, 2020, 2021, 2022, 2023]
MONTHS = ["SEPTEMBER"]
# MONTHS = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST",
#          "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
TEXT = " "


def process(file_data):
    """Return relevant data from zipfile for years and months
    Args:
        file_data: zip file or object

    Returns:
        dict: dict with summary and DataFrame with extracted data
    """
    results = []
    results_train = []
    results_tram = []
    results_bus = []
    results_subway = []
    results_plane = []
    results_distance = []
    filenames = []

    # Create Geodataframes of the public transport stations and stops
    # and airports in EPSG 4326 and EPSG 32634.
    train_coord_4326, train_coord_32634 = _create_coordinates('input/stations/Train stations.csv')
    bus_coord_4326, bus_coord_32634 = _create_coordinates('input/stations/Bus stops.csv')
    tram_coord_4326, tram_coord_32634 = _create_coordinates('input/stations/Tram stops.csv')
    subway_coord_4326, subway_coord_32634 = _create_coordinates('input/stations/Subway stops.csv')
    plane_coord_4326, plane_coord_32634 = _create_coordinates('input/stations/Airports.csv')
    # Extract info from selected years and months
    with zipfile.ZipFile(file_data) as z_file:
        file_list = z_file.namelist()
        for year in YEARS:
            for month in MONTHS:
                for name in file_list:
                    month_file = f"{year}_{month}.json"
                    if re.search(month_file, name) is not None:
                        filenames.append(month_file)
                        location_history_json = json.loads(z_file.read(name).decode("utf8"))

                        # Count the number of public transport travels
                        train_travel_count = _activity_count(location_history_json, "IN_TRAIN")
                        bus_travel_count = _activity_count(location_history_json, "IN_BUS")
                        tram_travel_count = _activity_count(location_history_json, "IN_TRAM")
                        subway_travel_count = _activity_count(location_history_json, "IN_SUBWAY")
                        plane_travel_count = _activity_count(location_history_json, "FLYING")

                        # Check if the travels meet the maximum speed requirement
                        train_speed_req_count = _check_speed_requirement(location_history_json, "IN_TRAIN", 140)
                        bus_speed_req_count = _check_speed_requirement(location_history_json, "IN_BUS", 100)
                        tram_speed_req_count = _check_speed_requirement(location_history_json, "IN_TRAM", 80)
                        subway_speed_req_count = _check_speed_requirement(location_history_json, "IN_SUBWAY", 80)
                        plane_speed_req_count = _check_speed_requirement(location_history_json, "FLYING", 950)

                        # Check if the start/end locations meet the requirement of being stations
                        tot_no_train_count, tot_tram_station, tot_subway_station, tram_travel, subway_travel, \
                        tot_not_train, tot_no_station_count = _train_check_location(location_history_json,
                                                                                    train_coord_32634, tram_coord_32634,
                                                                                    subway_coord_32634)

                        tot_no_bus_count, no_bus_count = _check_location(location_history_json,
                                                                         bus_coord_32634, "IN_BUS")
                        tot_no_tram_count, no_tram_count = _check_location(location_history_json,
                                                                         tram_coord_32634, "IN_TRAM")
                        tot_no_subway_count, no_subway_count = _check_location(location_history_json,
                                                                             subway_coord_32634, "IN_SUBWAY")
                        tot_no_plane_count = _airport_check_location(location_history_json, plane_coord_32634)

                        # Calculate total distance and count number of missing distance
                        tot_dis, tot_no_dis_count = _activity_distance(location_history_json)

                        # Replace missing distances with the haversine distance
                        # Replace Google Semantic Location History distances with haversine distance if the
                        # difference between these is greater than 5 km
                        tot_hav_dis, no_dis_count = _distance_total(location_history_json)

                        # Check if the duration is longer than 24 hours and count the number of times this is
                        # the case
                        train_dur_count = _check_duration(location_history_json, "IN_TRAIN")
                        tram_dur_count = _check_duration(location_history_json, "IN_TRAM")
                        bus_dur_count = _check_duration(location_history_json, "IN_BUS")
                        subway_dur_count = _check_duration(location_history_json, "IN_SUBWAY")
                        plane_dur_count = _check_duration(location_history_json, "FLYING")

                        results.append({
                            "Year": year,
                            "Month": month,
                            "Times traveled by train": train_travel_count,
                            "Times not a train station": tot_no_train_count,
                            "Times tram stop found": tot_tram_station,
                            "Times subway stop found": tot_subway_station,
                            "Times no other stop found": tot_no_station_count,
                            "Times traveled by train with imputation": train_travel_count - tot_not_train,
                            "Average > maximum speed train": train_speed_req_count,
                            "Times traveled by bus": bus_travel_count,
                            "Times not a bus stop": tot_no_bus_count,
                            "Average > maximum speed bus": bus_speed_req_count,
                            "Times traveled by tram": tram_travel_count,
                            "Times not a tram stop": tot_no_tram_count,
                            "Times traveled by tram with imputation": tram_travel_count + tram_travel - no_tram_count,
                            "Average > maximum speed tram": tram_speed_req_count,
                            "Times traveled by subway": subway_travel_count,
                            "Times not a subway stop": tot_no_subway_count,
                            "Times traveled by subway with imputation": subway_travel_count + subway_travel - no_subway_count,
                            "Average > maximum speed subway": subway_speed_req_count,
                            "Times traveled by plane": plane_travel_count,
                            "Times not an airport": tot_no_plane_count,
                            "Average > maximum speed plane": plane_speed_req_count,
                            "Activity Duration [days]": round(_activity_duration(location_history_json), 3),
                            "Activity Distance [km]": round(tot_dis, 3),
                            "Times distance missing": tot_no_dis_count,
                            "Number of times wrong distance": no_dis_count,
                            "Total distance with haversine distance": round(tot_hav_dis / 1000, 3),
                            "Times train travel > max duration": train_dur_count,
                            "Times tram travel > max duration": tram_dur_count,
                            "Times bus travel > max duration": bus_dur_count,
                            "Times subway travel > max duration": subway_dur_count,
                            "Times plane travel > max duration": plane_dur_count
                        })
                        results_train.append({
                            "Year": year,
                            "Month": month,
                            "Times traveled by train": train_travel_count,
                            "Times not a train station": tot_no_train_count,
                            "Times tram stop found": tot_tram_station,
                            "Times subway stop found": tot_subway_station,
                            "Times no other stop found": tot_no_station_count,
                            "Times traveled by train with imputation": train_travel_count - tot_not_train,
                            "Average > maximum speed train": train_speed_req_count,
                            "Times train travel > max duration": train_dur_count
                        })
                        results_tram.append({
                            "Year": year,
                            "Month": month,
                            "Times traveled by tram": tram_travel_count,
                            "Times not a tram stop": tot_no_tram_count,
                            "Times tram stop found at train": tot_tram_station,
                            "Times traveled by tram with imputation": tram_travel_count + tram_travel - no_tram_count,
                            "Average > maximum speed tram": tram_speed_req_count
                        })
                        results_bus.append({
                            "Year": year,
                            "Month": month,
                            "Times traveled by bus": bus_travel_count,
                            "Times not a bus stop": tot_no_bus_count,
                            "Average > maximum speed bus": bus_speed_req_count,
                            "Times bus travel > max duration": bus_dur_count
                        })
                        results_subway.append({
                            "Year": year,
                            "Month": month,
                            "Times traveled by subway": subway_travel_count,
                            "Times not a subway stop": tot_no_subway_count,
                            "Times subway stop found at train": tot_subway_station,
                            "Times traveled by subway with imputation": subway_travel_count
                                                                        + subway_travel - no_subway_count,
                            "Average > maximum speed subway": subway_speed_req_count,
                            "Times subway travel > max duration": subway_dur_count
                        })
                        results_plane.append({
                            "Year": year,
                            "Month": month,
                            "Times traveled by plane": plane_travel_count,
                            "Times not an airport": tot_no_plane_count,
                            "Average > maximum speed plane": plane_speed_req_count,
                            "Times plane travel > max duration": plane_dur_count,
                        })
                        results_distance.append({
                            "Year": year,
                            "Month": month,
                            "Activity Distance [km]": round(tot_dis, 3),
                            "Times distance missing": tot_no_dis_count,
                            "Number of times wrong distance": no_dis_count,
                            "Total distance with haversine distance": round(tot_hav_dis / 1000, 3)
                        })
                        break

        # Put results in DataFrame
        data_frame = pd.json_normalize(results)

        if os.path.exists("output/results.csv"):
            os.remove("output/results.csv")
        data_frame.to_csv('output/results.csv', index=False, encoding='utf-8')

        data_frame = pd.json_normalize(results_train)
        if os.path.exists("output/results_train.csv"):
            os.remove("output/results_train.csv")
        data_frame.to_csv('output/results_train.csv', index=False, encoding='utf-8')
        data_frame = pd.json_normalize(results_tram)
        if os.path.exists("output/results_tram.csv"):
            os.remove("output/results_tram.csv")
        data_frame.to_csv('output/results_tram.csv', index=False, encoding='utf-8')
        data_frame = pd.json_normalize(results_bus)
        if os.path.exists("output/results_bus.csv"):
            os.remove("output/results_bus.csv")
        data_frame.to_csv('output/results_bus.csv', index=False, encoding='utf-8')
        data_frame = pd.json_normalize(results_subway)
        if os.path.exists("output/results_subway.csv"):
            os.remove("output/results_subway.csv")
        data_frame.to_csv('output/results_subway.csv', index=False, encoding='utf-8')
        data_frame = pd.json_normalize(results_plane)
        if os.path.exists("output/results_plane.csv"):
            os.remove("output/results_plane.csv")
        data_frame.to_csv('output/results_plane.csv', index=False, encoding='utf-8')
        data_frame = pd.json_normalize(results_distance)
        if os.path.exists("output/results_distance.csv"):
            os.remove("output/results_distance.csv")
        data_frame.to_csv('output/results_distance.csv', index=False, encoding='utf-8')

        return {
            "summary": TEXT,
            "data_frames": [
                data_frame.fillna(0)
            ]
        }
