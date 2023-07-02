# UTRECHT UNIVERSITY
## Department of Information and Computing Science
### Applied Data Science master thesis

### Identifying and improving quality issues in Google Semantic Location History DDPs for public transport activities

First examiner: Erik-Jan van Kesteren

Second examiner: Thijs Carrière

Candidate: Daniëlle Bakker 0187410

## Description project
The aim of this project is to identify and improve potential quality issues. 
These scripts will count the number of errors and use data imputation where possible. This will lead to a more accurate 
data extraction which in turn will lead to a better understanding of the travel behaviors.

## Requirements
[Eyra Port POC](https://github.com/eyra/port-poc)

Python 3.8

Geopandas 0.13.0

Haversine 2.8.0

## Input
All files need to be in the input folder
- The file with Google Semantic Location History data
  - input/Takeout.zip
- Files with coordinates of public transport station and stop location
  - input/stations/Train stations.csv
  - input/stations/Bus stops.csv
  - input/stations/Tram stops.csv
  - input/stations/Subway stops.csv
  - input/stations/Airports.csv

## Python scripts
- main.py <br/>
  Starts the extraction

- __init__.py <br/>
  Loads all the files and call the different functions

- total_activity.py <br/>
  Calculates the total distance andduration <br/>
  Count the total number per activity types and missing distances <br/>
  Adds milliseconds to timestamps that don't have this and counts this <br/>
    _activity_distance <br/>
    Get total distance of activities in km <br/>
    _activity_duration <br/>
    Get total duration of activities <br/>
    _activity_count <br/>
    Counts how often an activity type was predicted <br/>
    _test_time_format <br/>
    Adds milliseconds to the timestamp when necessary and counts when this is needed <br/>
    _test_missing_distance <br/>
    Count number of times distance is missing from the activity segment <br/>

- station_activity.py <br/>
  Checks if start and end location are public transport locations and counts the errors. When not a train station, it
  will check if there are tram or subway station instead <br/>
    _create_coordinates <br/>
    Transforms the public transport stations and stops to EPSG 4326 and EPSG 32634 <br/>
    _transform_coordinates <br/>
    Transforms coordinates of the start or end location <br/>
    _check_location <br/>
    Checks if start or end location is an airport and counts when not <br/>
    _train_check_location <br/>
    Checks if start or end location is an train station and counts when not <br/>
    _station_different_location <br/>
    Checks if start or end location is an tram or subway stop and counts when it is <br/>
    _airport_check_location <br/>
    Checks if start or end location is an airport and counts when it is <br/>

- speed_activity.py <br/>
  Check if the travels meet the requirement of the average speed being lower than the maximum speed <br/>
    _check_speed_requirement <br/>
    Counts how often the speed requirement of the activity type is not met <br/>
    _average_speed <br/>
    Calculates the average speed of an activity <br/>
    _test_time_format <br/>
    Adds milliseconds to the timestamp when necessary <br/>

- duration_activity.py <br/>
  Checks if the activity is no longer than 24 hours and counts when this requirement is not met <br/>
    _check_duration <br/>
    Checks if the duration is no longer than 24 hours <br/>
    _test_time_format <br/>
    Adds milliseconds to the timestamp when necessary <br/>

- distance_activity.py <br/>
  Checks if the differences between logged distance and haversine distances is no more than 5km and counts when this requirement is not 
  met <br/>
    _distance_total <br/>
    Calculates the total distances of one month <br/>
    _distance_compare <br/>
    Checks if logged distance is within 5 kilometers of haversine distance and counts the times it is not <br/>
    
## Output
All output can be found in the output folder
- results.csv <br/>
  File containing all the results of the extraction <br/>
- results_train.csv <br/>
  File containing all the results of the train <br/>
- results_tram.csv <br/>
  File containing all the results of the tram <br/>
- results_bus.csv <br/>
  File containing all the results of the bus <br/>
- results_subway.csv <br/>
  File containing all the results of the suwbay <br/>
- results_plane.csv <br/>
  File containing all the results of the plane <br/>
- results_distance.csv <br/>
  File containing all the results about the distance <br/>

## Run scripts
- All the needed input files need to be in the input folder
- All the scripts need to be in the main folder
- Call main.py to run all the scripts
- All the output files can be found in the output folder after the scripts are finished

