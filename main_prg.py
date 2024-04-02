
'''\
This Simple program Demonstrates how to use G-Streamer and capture RTSP Frames in Opencv using Python
- Sahil Parekh
'''

import multiprocessing as mp
import time
import vid_streamv3 as vs
import cv2
import sys

'''
Main class
'''
class mainStreamClass:
    def __init__(self):

        #Current Cam
        self.camProcess = None
        self.cam_queue = None
        self.stopbit = None
        self.active_track = False
        self.camlink = "rtsp://localhost:8554/parque-central-cam-2" #Add your RTSP cam link
        self.framerate = 20
    
    def startMain(self):

        #set  queue size
        self.cam_queue = mp.Queue(maxsize=100)

        #get all cams
        time.sleep(3)

        self.stopbit = mp.Event()
        self.camProcess = vs.StreamCapture(self.camlink,
                             self.stopbit,
                             self.cam_queue,
                            self.framerate)
        self.camProcess.start()

        # calculate FPS
        lastFTime = time.time()
        error_time = 0
        error_count = 0 
        had_error = False
        
        while self.camProcess.is_stream_active() == False:
            print('Waiting for stream to start')
            time.sleep(1)
        print("Stream is active")
        try:
            while True:

                if not self.cam_queue.empty():
                    if had_error:
                        print("Error fixed, was offline for ", time.time() - error_time, "seconds")
                        had_error = False
                    # print('Got frame')
                    cmd, val = self.cam_queue.get()

                    '''
                    #calculate FPS
                    diffTime = time.time() - lastFTime`
                    fps = 1 / diffTime
                    # print(fps)
                    
                    '''
                    lastFTime = time.time()

                    # if cmd == vs.StreamCommands.RESOLUTION:
                    #     pass #print(val)

                    if cmd == vs.StreamCommands.FRAME:
                        if val is not None:
                            cv2.imshow('Cam: ' + self.camlink, val)
                            cv2.waitKey(1)
                elif self.camProcess.is_stream_active() == False:
                    print('Cam is not active')
                    had_error = True
                    error_count += 1
                    error_time = time.time()
                    time.sleep(5)
                    self.restartCamStream()
                    while self.camProcess.is_stream_active() == False:
                        print('Waiting for stream to start')
                        time.sleep(1)

        except KeyboardInterrupt:
            print('Caught Keyboard interrupt')

        except:
            e = sys.exc_info()
            print('Caught Main Exception')
            print(e)

        self.stopCamStream()
        cv2.destroyAllWindows()


    def stopCamStream(self):
        print('in stopCamStream')

        if self.stopbit is not None:
            self.stopbit.set()
            while not self.cam_queue.empty():
                try:
                    _ = self.cam_queue.get()
                except:
                    break
                self.cam_queue.close()

            self.camProcess.join()
    
    def restartCamStream(self):
        print('in restartCamStream')
        self.stopCamStream()
        
        self.stopbit = mp.Event()
        self.cam_queue = mp.Queue(maxsize=100)
        self.camProcess = vs.StreamCapture(self.camlink,
                             self.stopbit,
                             self.cam_queue,
                            self.framerate)
        self.camProcess.start()
    
    def resumeCamStream(self):
        print('in resumeCamStream')
        #unset stopbit


if __name__ == "__main__":
    mc = mainStreamClass()
    mc.startMain()