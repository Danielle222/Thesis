# UTRECHT UNIVERSITY
## Department of Information and Computing Science
### Applied Data Science master thesis

### An improved quality pipeline for Google Location History data (placeholder)

First examiner: Erik-Jan van Kesteren

Second examiner: Thijs Carrière

Candidate: Daniëlle Bakker 0187410

## Description project
Digital privacy and data protection has become an important topic resulting in new laws being made.
This includes the right for people to access their own personal data and share this with other parties.
As a responds, companies now give their users the opportunity to download their data as Data Download Package
(DDPs) which users can then donate to research studies. A recent study used the Google Semantic Location History
DDPs to investigate how the COVID-19 pandemic changed travel behavior. The problem is that these DDPs contain
potential quality issues which can influence the conclusion. The aim of this project is to identify these potential
quality issues and take them into account by flagging or data imputation. The result is a python script that checks
if different parts of the data meet set requirements to locate the quality issues. This script will count the number
of errors and use data imputation where possible. This should lead to a more accurate data extraction which would in
turn lead to a better understanding of the travel behaviors. There are still multiple steps needed to make the
extraction as accurate to reality as possible with some perhaps for Google with mobile sensors and algorithms.

## Requirements
[Eyra Port POC](https://github.com/eyra/port-poc)

Python 3.8

Geopandas 0.13.0

Haversine 2.8.0

## Input files
- The file with Google Semantic Location History data
  - port-poc-master/data_extractor/tests/data/Takeout.zip
- Files with coordinates of public transport station and stop location
  - stations/Train stations.csv
  - stations/Bus stops.csv
  - stations/Tram stops.csv
  - stations/Subway stops.csv
  - stations/Airports.csv

## Python scripts
- main.py
  Starts the extraction

__init__.py
Loads all the files and call the different functions

station_activity.py
Checks if start and end location are public transport locations and counts the errors. When not a train station, it
will check if there are tram or subway station instead
    _create_coordinates
    Transforms the public transport stations and stops to EPSG 4326 and EPSG 32634
    _transform_coordinates
    Transforms coordinates of the start or end location
    _check_location
    Checks if start or end location is an airport and counts when not
    _train_check_location
    Checks if start or end location is an train station and counts when not
    _station_different_location
    Checks if start or end location is an tram or subway stop and counts when it is
    _airport_check_location
    Checks if start or end location is an airport and counts when it is

total_activity.py
    _activity_distance
    Get total distance of activities in km
    _activity_duration
    Get total duration of activities
    _activity_count
    Counts how often an activity type was predicted
    _test_time_format
    Add milliseconds to the timestamp when necessary and counts when this is needed
    _test_missing_distance
    Count number of times distance is missing from the activity segment

speed_activity.py
Check if the travels meet the requirement of the average speed being lower than the maximum speed
    _check_speed_requirement
    Counts how often the speed requirement of the activity type is not met
    _average_speed
    Calculates the average speed of an activity
    _test_time_format:
    Add milliseconds to the timestamp when necessary


--Output file--
File containing the results of the extraction
results.csv

