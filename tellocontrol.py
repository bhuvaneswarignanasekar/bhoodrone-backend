import threading 
import socket
import sys
import time
import platform
import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import numpy as np
import queue
import multiprocessing
class Drone:
    
    is_connected=False
    q=queue.Queue()
    VS_UDP_IP = '0.0.0.0'
    VS_UDP_PORT = 11111
    STATE_UDP_PORT = 8890
    #video capture object
    
    cap=None
    stream_on = False

    def __init__(self):

        self.host = ''
        self.port = 9000
        self.locaddr = (self.host,self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tello_address = ('192.168.10.1', 8889)
        self.sock.bind(self.locaddr)
        self.connect()
        self.streamon()
        self.battery()
        
        #self.get_video_capture()
    
    
    def command(self,command):
        
        self.msg=command
        self.is_connected="true"
        self.msg = self.msg.encode(encoding="utf-8") 
        while True:
            sent = self.sock.sendto(self.msg, self.tello_address)
            print("Message sent to Tello"+str(self.msg))
            data, server = self.sock.recvfrom(1518)
            message=data.decode(encoding="utf-8")
            print(message)
            if message=="error motor stops":
                continue
            else:
                return sent
                break
                
            
        
    
    def connect(self):
        """connect to tello """
        return self.command("command")
    
    def takeoff(self):
        """tello auto takeoff"""
        
        return self.command("takeoff")
    
    def land(self):
        """tello auto land"""
        
        return self.command("land")
    
    def battery(self):
        """tello battery check"""
        
        return self.command("battery?")
    
    def streamon(self):
        """video streaming is on"""
        
        return self.command("streamon")
    
    def streamoff(self):
        """video streaming is off"""
        
        return self.command("streamoff")
    
    def rotate_clockwise(self, degree):
        """tello rotate clockwise degree 1-3600"""
        
        return self.command("cw"+' '+str(degree))
    
    def rotate_anticlockwise(self,degree):
        """tello rotate anticlockwise degree 1-3600"""
        
        return self.command("ccw"+' '+str(degree))
    
    def emergency(self):
        """emergency land - shut down all motors"""
        
        return self.command("emergency")
    
    def right(self,dist):
        """move right - can move 20-500 cm"""
        
        return self.command("right"+' '+str(dist))
    
    def left(self,dist):
        """move left - can move 20-500 cm"""
        return self.command("left"+' '+str(dist))
    
    def forward(self,dist):
        """move forward - can move 20-500 cm"""
        return self.command("forward"+' '+str(dist))
    
    def backward(self,dist):
        """move backward - can move 20-500 cm"""
        return self.command("back"+' '+str(dist))
    
    def flip_right(self):
        """flip to right"""
        return self.command("flip r")
    
    def flip_left(self):
        """flip to left"""
        return self.commnad("flip l")
    
    def up(self,dist):
        
        return self.command("up"+' '+str(dist))
    
    def down(self,dist):
        
        return self.command("down"+' '+str(dist))
    def get_udp_video_address(self):
            
        return 'udp://@' + self.VS_UDP_IP + ':' + str(self.VS_UDP_PORT) 
    
    
    def get_video_capture(self):
        """Get the VideoCapture object from the camera drone
        Returns:
            VideoCapture
        """
        frame_id=1
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.get_udp_video_address())
            while(True):
                 # Capture frame-by-frame
                _, frame =self.cap.read()
                frame_id += 1
                if frame_id%30==0:
                    self.q.put(frame)
                cv2.imshow('frame',frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # When everything done, release the capture
            cap.release()
            cv2.destroyAllWindows()
        #return self.cap
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
    def to_route(self,rotate_count,flag,flag_id):
        if flag==0 and flag_id==0:
            if rotate_count%72==0:
                #self.drone.up(20)
                print("^^^^^^^^^^^^^^^^up^^^^^^^^^^^^^")
            else:
                print("rotate")
                #self.drone.rotate_clockwise(5)
        if flag==1 and flag_id==1:
            print("^^^^^^^^^^^^^^^^^^^^^^^^^6forward^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            #self.drone.forward(30)
    def start(self,rotate_count):
        if rotate_count==1:
            print("taking off")
            #self.drone.takeoff()
            #self.drone.down(20)
        
     
if __name__ == "__main__":
    t=Drone()
    #t.land()
    receive=threading.Thread(target=t.get_video_capture)
    #det=multiprocessing.Process(target=t.detect_obj,args=["bottle"])
    receive.start()
    #det.start()
    
    