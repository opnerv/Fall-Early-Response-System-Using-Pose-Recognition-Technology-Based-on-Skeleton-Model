from flask import Flask, send_file, jsonify, request
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import threading
import time
import random

app = Flask(__name__)
folder_n = "/home/jwh21680/project"
latest_file = None
last_modified = 0

class Imhd(FileSystemEventHandler):
    def on_created(self, event):
        global latest_file, last_modified
        if not event.is_directory:
            latest_file = event.src_path

def get_value():
    data = request.json
    print("Received data:", data)

    return data

@app.route('/')
def index():
    return '''
        <h1>Real-time HEART RATE: <span id="value"></span></h1>
        <img id="image" src="" alt="Image">

        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        <script>
            function updateValue() {
                $.ajax({
                    url: '/get_value',
                    success: function(data) {
                        $('#value').text(data.value);
                    }
                });
            }

            function updateImage() {
                var timestamp = new Date().getTime();  // 현재 시간을 밀리초 단위로 가져옴
                var imageUrl = '/get_image?' + timestamp;  // 이미지 URL에 무작위 쿼리 매개변수 추가
                $('#image').attr('src', imageUrl);
            }

            $(document).ready(function() {
                updateValue();
                updateImage();
                setInterval(updateValue, 1000);  // 1초마다 업데이트
                setInterval(updateImage, 1000);  // 1초마다 업데이트
            });
        </script>
    '''

@app.route('/get_image')
def send_image():
    if latest_file is not None:
        return send_file(latest_file, mimetype='image/jpeg')
    else:
        return "No image yet."

@app.route('/get_value')
def send_value():
    data = get_value()
    return jsonify({'value': data})

if __name__ == '__main__':
    event_handler = Imhd()
    observer = Observer()
    observer.schedule(event_handler, folder_n, recursive=True)
    observer.start()
    app.run(host='0.0.0.0', port=3200, debug=True)
