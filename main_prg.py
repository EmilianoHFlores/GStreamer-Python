
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
        
        # recovery
        # time in seconds waiting for stream to start
        self.timeout = 60
    
    def startMain(self):

        #get all cams
        time.sleep(3)

        #start cam stream
        self.startCamStream()
        print('Waiting for stream to start...')
        self.waitForStream(timeout=self.timeout)

        # calculate FPS
        lastFTime = time.time()
        error_time = 0
        error_count = 0 
        had_error = False
        
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
                    if not had_error:
                        error_time = time.time()
                        had_error = True
                        error_count += 1
                    time.sleep(5)
                    self.stopCamStream()
                    self.startCamStream()
                    print("Waiting for stream to restart...")
                    self.waitForStream(timeout=self.timeout)

        except KeyboardInterrupt:
            print('Caught Keyboard interrupt')

        except:
            e = sys.exc_info()
            print('Caught Main Exception')
            print(e)

        self.stopCamStream()
        cv2.destroyAllWindows()


    def stopCamStream(self):
        # print('in stopCamStream')

        if self.stopbit is not None:
            self.stopbit.set()
            while not self.cam_queue.empty():
                try:
                    _ = self.cam_queue.get()
                except:
                    break
                self.cam_queue.close()

            self.camProcess.join()
    
    def startCamStream(self):
        #set  queue size
        self.cam_queue = mp.Queue(maxsize=100)
        self.stopbit = mp.Event()
        self.camProcess = vs.StreamCapture(self.camlink,
                             self.stopbit,
                             self.cam_queue,
                            self.framerate)
        self.camProcess.start()
        
    def waitForStream(self, timeout=30):
        startTime = time.time()
        while self.camProcess.is_stream_active() == False and time.time() - startTime < timeout:
            time.sleep(2)
        if time.time() - startTime >= timeout:
            return False
        return True


if __name__ == "__main__":
    mc = mainStreamClass()
    mc.startMain()