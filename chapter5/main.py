from flask import Flask, Response
from camera import Camera
import cv2


app = Flask(__name__)
camera = Camera().start()


def gen(camera):
    while True:
        frame = camera.read()
        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        
@app.route('/stream')
def stream():
    return Response(gen(camera),
                mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
