import boto3
import colorama
import json
import tempfile

from arguments import get_args
from utils import *

def download_from_s3(s3_uri: str) -> str:
    print(f'Downloading backup files from s3')
    s3 = boto3.resource('s3')
    bucket_name, data_folder = parse_s3_uri(s3_uri)
    bucket = s3.Bucket(bucket_name)

    temp_path = tempfile.mkdtemp() 
    for obj in bucket.objects.filter(Prefix=data_folder):
        print(obj)
        if obj.key.endswith('/'):
            continue
        
        bucket.download_file(obj.key, f'{temp_path}/{os.path.basename(obj.key)}')

    print(f'Downloaded backup files into: {temp_path}')
    return temp_path

def write_batch_dynamo(table: str, batch_file_path: str):
    dynamo = boto3.client('dynamodb')
    with open(batch_file_path) as bf:
        request_items = {
            table: [{"PutRequest": json.loads(item)} for item in json.load(bf)]
        }

    response = dynamo.batch_write_item(RequestItems=request_items)
    unprocessed = response.get('UnprocessedItems')

    if unprocessed and unprocessed.get(table):
        create_temporary_batch(unprocessed, f'{batch_file_path}.unprocessed')

def create_temporary_batch(items: list, batch_filename: str):
    with open(batch_filename, 'w') as batch_file:
        json.dump(items, batch_file)


def main(args: dict):
    if(args.profile):
        boto3.setup_default_session(profile_name=args.profile)

    data_path = download_from_s3(args.source) if 's3://' in args.source else args.source
    extract_archives_in_dir(data_path)

    batch_index = 1
    items_to_import = []
    for backup_file in get_files_by_extension(data_path, '.json'):
        with open(f'{data_path}/{backup_file}') as f:
            items_to_import += f.readlines()

        # Batch-Write API is restricted to 25 changes so we create temporary batches
        while len(items_to_import) // 25 > 0:
            batch = items_to_import[:25]
            create_temporary_batch(batch, f'{data_path}/{batch_index}.batch')
            items_to_import = items_to_import[25:]
            batch_index += 1

    if(len(items_to_import) > 0):
        # Create last batch out of the remaining items
        create_temporary_batch(items_to_import, f'{data_path}/{batch_index}.batch')

    for batch_file in get_files_by_extension(data_path, '.batch'):
        write_batch_dynamo(args.table, f'{data_path}/{batch_file}')

    if(get_files_by_extension(data_path, '.unprocessed')):
        print(colorama.Fore.RED, f'There are some unprocessed items at path: {data_path}')

    print(colorama.Fore.GREEN, f'Restore sucessful with {batch_index} batch write requests')

if __name__=='__main__':
   args = get_args()
   main(args)