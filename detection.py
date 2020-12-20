import cv2
import numpy as np
import time
import queue
from tellocontrol import Drone
import sys
import threading
class Detection:
    drone=Drone()
    q=queue.Queue()
        
    def detect_obj(self,request):
        # Load Yolo
        flag_id=0
        rotate_count=1
        net = cv2.dnn.readNet("/home/bhuvana/workspace/tellodrone-project/yolov3.weights", "/home/bhuvana/workspace/tellodrone-project/yolov3.cfg")
        classes = []
        with open("/home/bhuvana/workspace/tellodrone-project/coco.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))
        # Loading camera
        print("getting")
        
        print("done")
        self.start(rotate_count)
        font = cv2.FONT_HERSHEY_PLAIN
        starting_time = time.time()
        frame_id = 0
        while True:

            flag=0
            if self.q.empty !=True:
                frame=self.q.get()
            
                height, width, channels = frame.shape
                # Detecting objects
                blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
                net.setInput(blob)
                outs = net.forward(output_layers)
                
                # Showing informations on the screen
                class_ids = []
                confidences = []
                boxes = []
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence > 0.2:
                            # Object detected
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)
                            # Rectangle coordinates
                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)
                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)
                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.4, 0.3)
                for i in range(len(boxes)):
                    if i in indexes:
                        x, y, w, h = boxes[i]
                        label = str(classes[class_ids[i]])
                        confidence = confidences[i]
                        color = colors[class_ids[i]]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.rectangle(frame, (x, y), (x + w, y + 30), color, -1)
                        cv2.putText(frame, label + " " + str(round(confidence, 2)), (x, y + 30), font, 3, (255,255,255), 3)
                        
                        if label == request:
                            flag=1
                            flag_id=1
                            print("=========================================================================")
                            print("found the object",request)
                            print("====================================================================")
                self.to_route(rotate_count,flag,flag_id)
                rotate_count=rotate_count+1
                elapsed_time = time.time() - starting_time
                fps = frame_id / elapsed_time
                cv2.putText(frame, "FPS: " + str(round(fps, 2)), (10, 50), font, 3, (0, 0, 0), 3)
                cv2.imshow("Image", frame)
                key = cv2.waitKey(1)
                if key == 27:
                    break
        #cap.release()
        cv2.destroyAllWindows()
    def receive(self,cap):
        frame_id=0
        #cap=self.drone.get_video_capture()
        while True:
            _, frame = cap.read()
            frame_id += 1
            if frame_id%30==0:
                self.q.put(frame)
    def to_route(self,rotate_count,flag,flag_id):
        if flag==0 and flag_id==0:
            if rotate_count%72==0:
                #self.drone.up(20)
                print("^^^^^^^^^^^^^^^^up^^^^^^^^^^^^^")
            else:
                print("rotate")
                self.drone.rotate_clockwise(5)
        if flag==1 and flag_id==1:
            print("^^^^^^^^^^^^^^^^^^^^^^^^^6forward^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            #self.drone.forward(30)
    def start(self,rotate_count):
        if rotate_count==1:
            print("taking off")
            #self.drone.takeoff()
            #self.drone.down(20)
    def get_and_detect(self,request):
        cap=self.drone.get_video_capture()
        receive=threading.Thread(target=self.receive, args=[cap],daemon=True)
        det=threading.Thread(target=self.detect_obj,args=[request])
        receive.start()
        det.start()
if __name__ == "__main__":
    detect=Detection()
    detect.get_and_detect("bottle")