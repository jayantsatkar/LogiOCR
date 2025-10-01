import cv2
import win32com.client


def list_cameras(max_tested=10):
    available_cameras = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Use DirectShow on Windows for better compatibility
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
        else:
            cap.release()  # Ensure resources are freed
    return available_cameras

def get_camera_names(names_list):
    # Use WMI to query connected video controllers
    wmi = win32com.client.GetObject("winmgmts:")
    cameras = wmi.InstancesOf("Win32_PnPEntity")
    names = []
    for cam in cameras:
        if "camera" in cam.Name.lower() or "webcam" in cam.Name.lower():
            names.append(cam.Name)
    print(names)
    names_list = names
    return names

if __name__ == '__main__':
    cameras = list_cameras()
    print("Available camera indices:", cameras)

