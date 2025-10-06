import argparse

def get_args() -> dict:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-p", "--profile", help="AWS CLI profile", type=str)
    parser.add_argument("-r", "--region", help="AWS Region for Secrets Manager", default="us-east-1", type=str)
    period_group = parser.add_mutually_exclusive_group(required=True)
    period_group.add_argument("-d", "--date", help="Start deleting secrets from this date [YYYY-MM-dd]", type=str)
    period_group.add_argument("-t", "--time", help="Start deleting secrets from this many days ago", type=int)

    return parser.parse_args()