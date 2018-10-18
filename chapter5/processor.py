import cv2


class MotionDetector(object):
    def __init__(self, camera):
        # 初期化処理
        self.camera = camera.start()
        self.background = None

    def get_frame(self):
		# 動体検知処理の呼び出しをおこなう
        # フレームはJPEG画像に変換して戻り値にする
        frame = self.detect()
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def detect(self):
		# 動体検知処理をおこなう
        frame = self.camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.background is None:
            self.background = gray
            return frame
            
        frameDelta = cv2.absdiff(self.background, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        thresh = cv2.erode(thresh, None, iterations=2)
        
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[1]
        
        for c in cnts:
            if cv2.contourArea(c) < 500:
                continue
                
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
        return frame