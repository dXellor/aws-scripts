import boto3
import colorama
from datetime import datetime, timezone, timedelta

from arguments import get_args

def compare_last_accessed_date(secret: dict, cutoff_date):
    if 'LastAccessedDate' in secret:
        return secret['LastAccessedDate'] < cutoff_date
    
    return False

def main(args: dict):
    if(args.profile):
        boto3.setup_default_session(profile_name=args.profile)
   
    sm_client = boto3.client('secretsmanager', region_name=args.region)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=args.time) if args.time else datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=timezone.utc) 

    paginator = sm_client.get_paginator('list_secrets')
    deleted_successfully = 0
    for page in paginator.paginate():
        expired_secrets_arns = [secret['ARN'] for secret in filter(lambda secret: compare_last_accessed_date(secret, cutoff_date), page['SecretList'])]
        
        #Unfortunatelly there is no batch delete operation for secrets manager so you have to call delete api for every secret
        for secret_arn in expired_secrets_arns:
            try:
                response = sm_client.delete_secret(
                    SecretId=secret_arn,
                    RecoveryWindowInDays=7
                )
                print(colorama.Fore.WHITE, f"Deleted secret {secret_arn}: scheduled for deletion at {response['DeletionDate']}")
                deleted_successfully += 1
            except:
                print(colorama.Fore.RED, f'Failed to delete secret record with ARN: {secret_arn}')

    print(colorama.Fore.GREEN, f"Successfully scheduled deletion of {deleted_successfully} secrets")

if __name__=='__main__':
   args = get_args()
   main(args)