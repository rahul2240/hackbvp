import boto3
from botocore.exceptions import ClientError
import logging

s3_client = boto3.client('s3')

def upload_file(filename, images_path, pdf_path):

    s3_client = boto3.client('s3')

    frames_url = []

    base_path = 'video_change_frames/' + filename + '/'
    

    pdf_s3_path = base_path + 'pdf/' + pdf_path.split("/")[-1]
    
    try:
        response = s3_client.upload_file(pdf_path, 'gradeup-studio', pdf_s3_path)
        pdf_link = "http://cloudfrontvideo.gradeup.co/" + pdf_s3_path
    except ClientError as e:
        print('pdf not uploaded to s3')
        logging.error(e)
    
    return frames_url, pdf_link