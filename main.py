import sys
import cv2
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from configparser import ConfigParser
from errorLogger import LogError
import socket
import threading
import time

from listcam import list_cameras

class Mainwindow(QMainWindow):
    def __init__(self):
        super(Mainwindow, self).__init__()
        self.setWindowTitle("Video Capture Station")
        loadUi("main.ui", self)
        #self.logger = LogError.GetLogger()

        self.camThread = CameraThread(3)
        self.camThread.frameCaptured.connect(self.update_frame)
        self.camThread.start()

        self.logger = LogError.get_logger()

        self.red_on = True
        self.green_on = False
       
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_leds)
        self.timer.start(1000)  # 1000 ms = 1 sec
        self.start = True

        self.BtnStart.clicked.connect(self.start_action)
        self.BtnStop.clicked.connect(self.stop_action)
        #self.BtnTestConnection.clicked.connect(self.BtnTestConnection)
        self.btnTestConnection.clicked.connect(self.btnTestConnection_clicked)
        self.lblVideo.setText("Please wait while loading camera")
       

       

    def update_frame(self, frame):
        # Show frame in QLabel
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        self.lblVideo.setPixmap(QPixmap.fromImage(img))
    
    def closeEvent(self, event):
        print('Close Event')
        if self.camThread.isRunning():
            self.camThread.stop()
            self.camThread.wait()
        event.accept()

    #    # Video and image capture  
    def start_frames(self):  
        try:
            print('btn clicked')
            cap = cv2.VideoCapture(3)

            if not cap.isOpened():
                print("Cannot open camera")
                exit()
            # self.start =  True
            
            while self.start:
            # Capture frame-by-frame

                print('In While Loop')
                ret, frame = cap.read()
    
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break

                    # Display the resulting frame
                cv2.imshow('Webcam', frame)

                # Press 'q' to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            print('End of While')
               

        except Exception as e:
            print(f"Something went wrong: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()

    # def stop_frames(self):
        print('Stop Frames')
        self.start = False

    def btnTestConnection_clicked(self):

        HOST = self.config.get('Application','PLCIP')
        PORT = int(self.config.get('Application','plc_port'))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 sec timeout

        try:
            sock.connect((HOST, PORT))
            #QMessageBox.information(self, "Success", "Connection is successful")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Connection Status")
            msg.setText(f"Connected successfully to {HOST}:{PORT}")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        except socket.timeout:
            #QMessageBox.critical(self, "Failure", "Connection is successful")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Connection Status")
            msg.setText(f"Failed to connect to {HOST}:{PORT}")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

        except socket.error as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Connection Status")
            msg.setText(f"Failed to connect to {HOST}:{PORT}")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        finally:
            sock.close()

            
    def start_action(self):
        print("Start clicked")

    def stop_action(self):
        print("Stop clicked")

    def config_action(self):
      #self.config_window = ConfigWindow()   # create dialog
      self.config_window.show()  

    def toggle_leds(self):
        """Swap red/green LED states"""
        self.red_on = not self.red_on
        self.green_on = not self.green_on
        self.update_leds()

    def update_leds(self):
        """Update LED colors based on states"""
        self.ledRed.setStyleSheet(
            "background-color: red; border-radius: 12px;" if self.red_on
            else "background-color: grey; border-radius: 12px;"
        )
        self.ledGreen.setStyleSheet(
            "background-color: green; border-radius: 12px;" if self.green_on
            else "background-color: grey; border-radius: 12px;"
        )

class CameraThread(QThread):
    frameCaptured = pyqtSignal(object)

    def __init__(self, cam_index=0):
        super().__init__()
        self.cam_index = cam_index
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.cam_index)
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                self.frameCaptured.emit(frame)   # send frame to UI
        cap.release()

    def stop(self):
        self.running = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = Mainwindow()
    mainwindow.setWindowTitle("Video Capture")
    mainwindow.show()
    app.exec()