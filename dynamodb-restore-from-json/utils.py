import gzip
import os
import shutil

def parse_s3_uri(s3_uri: str) -> tuple[str,str]:
    #example uri: s3://bucket-name/dir1/dir2/file.txt
    bucket_name = s3_uri.split('/')[2]
    dir_name = s3_uri.split(f'{bucket_name}/')[1]
    
    return bucket_name, dir_name

def extract_archives_in_dir(path: str):
    for filename in get_files_by_extension(path, '.gz'):
        gz_file_path = os.path.join(path, filename)
        extracted_file_name = filename[:-3]
        extracted_file_path = os.path.join(path, extracted_file_name)
        
        with gzip.open(gz_file_path, 'rb') as f_in:
            with open(extracted_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        os.remove(gz_file_path)

def get_files_by_extension(path: str, ext: str):
    return [file for file in os.listdir(path) if file.endswith(ext)]