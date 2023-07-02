"""Main program to test google_semantic_location history script"""
from __init__ import process


if __name__ == '__main__':
    result = process("input/Takeout.zip")
    # print("Summary:\n", result["summary"])
    print("Dataframe\n", result["data_frames"])
