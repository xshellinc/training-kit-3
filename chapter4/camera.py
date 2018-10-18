from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2


class Camera(object):
    def __init__(self,  resolution=(512, 304), framerate=24):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(
        self.rawCapture, format="bgr", use_video_port=True)

        self.frame = None
        self.stopped = False
        
    def start(self):
        # フレームの読み込み処理をスレッドとして開始する
        Thread(target=self.update, args=()).start()
        return self
        
    def update(self):
        # フレームの読み込み処理を行う
        for f in self.stream:
            self.frame = f.array
            self.rawCapture.truncate(0)
            
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()

                return
        
    def read(self):
        # 最新のフレームを返す
        return self.frame
        
    def stop(self):
        # スレッドを終了させる
        self.stopped = True