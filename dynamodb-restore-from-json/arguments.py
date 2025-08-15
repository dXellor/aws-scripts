import argparse

def get_args() -> dict:
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--table", help="DynamoDb table to import data to", type=str, required=True)
    parser.add_argument("-s", "--source", help="Path to dynamodb exported data. S3 path and local path are both valid values", type=str, required=True)
    parser.add_argument("-p", "--profile", help="AWS CLI profile", type=str)
    #parser.add_argument("-e", "--estimate-cost", help="Estimate cost of this restore procedure in USD, depending on how many items there is to restore", action='store_true')

    return parser.parse_args()