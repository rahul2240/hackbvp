from flask import jsonify, request
from app import app
from app import celery_tasks
import collections



@app.route('/video', methods=['POST'])
def process_video():

    video_id = request.form['video_id']
    video_url = request.form['video_url']
    print("hello {}".format( video_id))
    task1 = celery_tasks.download_video_and_process(video_id, video_url)
    output = {}
    output['link'] = task1
    return jsonify(output)


@app.route('/health', methods=['GET'])
def get_health():
    return jsonify(status='OK')