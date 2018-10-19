from flask import Flask, Response
from camera import Camera
# from processor import MotionDetector
from processor import SingleCounter


app = Flask(__name__)
camera = Camera()
# processor = MotionDetector(camera)
processor = SingleCounter(camera)


def gen(camera):
    while True:
        frame = processor.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
@app.route('/stream')
def stream():
    return Response(gen(processor),
                mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
