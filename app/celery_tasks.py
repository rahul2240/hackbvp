import os
import shutil
from app import notes
# from app.celery_config import celery
import requests
import urllib.request
import moviepy.editor as mp 
import logging
from pytube import YouTube
import numpy as np
# import tensorflow as tf
# from tensorflow.keras.models import load_model

FPS = 1


# @celery.task(queue='video_analysis')
def download_video_and_process(video_id, video_url):
	print ("Process video request {}".format(video_url))
	# Download video frames
	video_name = video_url[video_url.index('://') + 3 :].replace('/', '-').replace('?', '-').replace('=', '-')
	video_path = os.path.join(os.getcwd(), 'videos_downloaded', video_name)


	if os.path.exists(video_name):
		print('video already exist')
		return

	if "youtu" in video_url:
		try:
			video_name = video_name.replace('.', '-')
			outpath = os.path.join(os.getcwd(), 'videos_downloaded')
			YouTube(video_url).streams.filter(progressive=True, file_extension='mp4').first().download(filename=video_name, output_path=outpath)
			video_name += ".mp4" 
			video_path = os.path.join(os.getcwd(), 'videos_downloaded', video_name)
		except Exception as e:
			print('Youtube video is not downloading', e)
			return
	else:
		try:
			urllib.request.urlretrieve(video_url, video_path)
		except:
			print('DB Video is not downloading')
			return
	
	frames_dest = os.path.join(os.getcwd(), 'frames', video_name)
	result_dest = os.path.join(os.getcwd(), 'results')

	if not os.path.exists(frames_dest):
		os.makedirs(frames_dest)
	else:
		print ("Duplicate request for video {}".format(video_url))
		return
	
	if not os.path.exists(result_dest):
		os.makedirs(result_dest)
		print('result destination created')

	print ("Video downloaded {}".format(video_url))
	try:
		pdf_link = extract_frames(video_id, video_path, FPS, frames_dest, result_dest) 
	except Exception as e:
		print('video processing failed', e)

	try:
		os.system("rm -rf {}".format(frames_dest))
	except Exception as e:
		print("Unable to delete directory: ", e)


	try:
		os.system('rm {}'.format(video_path))
	except:
		pass

	try:
		os.system('rm {}'.format(video_path[:-3] + "wav"))
	except:
		pass
	
	try:
		shutil.rmtree(frames_dest)
	except:
		pass

    return pdf_link
		

def extract_frames(video_id, video_path, FPS, frames_dest, result_dest):
	print ("extract_frames {}".format(video_path))
	os.system("ffmpeg -ss 00:01:03 -loglevel quiet -stats -i {} -vf fps={} {}/frame%06d.jpg".format(video_path, FPS, frames_dest))
	# Run processing on frames

	# GENERATING CODE STARTS HERE
	print('Sending to generate notes:')
	try:
		pdf_link = notes.start_from_here(video_id, frames_dest, result_dest, 0.92)
		print('Notes Are generated: ')
	except:
		print('notes generation failed')
	return pdf_link
	

