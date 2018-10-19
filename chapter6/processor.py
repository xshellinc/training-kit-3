import cv2
import time


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
        

class SingleCounter(object):
    def __init__(self, camera):
        # 初期化処理
        self.camera = camera.start()
        self.background = None
        self.height = None
        self.width = None
        self.track_time = time.time()
        self.track_list = []
        self.timeout = 0.5
        self.total_up = 0
        self.total_down = 0
        
    def get_frame(self):
        # detectメソッドを呼び出し、
        # 受け取ったフレームをJPEG画像に変換する
        frame = self.detect()
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
        
    def detect(self):
        # 人数カウントの処理を行う
        frame = self.camera.read()
        
        if self.height is None or self.width is None:
            self.height, self.width = frame.shape[:2]
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.background is None:
            self.background = gray
            return frame
            
        frameDelta = cv2.absdiff(self.background, gray)
        thresh = cv2.threshold(frameDelta, 50, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        thresh = cv2.erode(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[1]
                                    
        biggest_area = 800
        motion_found = False
        for c in cnts:
            found_area = cv2.contourArea(c)
            if found_area > biggest_area:
                motion_found = True
                biggest_area = found_area
                (x, y, w, h) = cv2.boundingRect(c)
                cx = int(x + w / 2)
                cy = int(y + h / 2)
                
        if motion_found:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), 2)
            
            elapsed = time.time() - self.track_time
            if elapsed >= self.timeout:
                track_list = []
                
            self.track_time = time.time()
            self.track_list.append(cy)
            
        border_y = self.height // 2
        if len(self.track_list) > 1:
            latest = self.track_list[-1]
            oldest = self.track_list[0]
    
            if oldest > border_y and latest < border_y:
                self.total_up += 1
                self.track_list = []
            elif oldest < border_y and latest > border_y:
                self.total_down += 1
                self.track_list = []
                
        cv2.line(frame, (0, border_y), (self.width, border_y),
                    (0, 255, 255), 2)        
        cv2.putText(frame, "Up: {}".format(self.total_up), (10, self.height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, "Down: {}".format(self.total_down), (10, self.height - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                        
        return frame
