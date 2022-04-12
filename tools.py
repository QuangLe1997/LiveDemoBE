# import datetime
# from _thread import start_new_thread
#
#
# # Define a function for the thread
# def load_video(thread_name, url):
#     import cv2
#
#     print(thread_name)
#     while True:
#         try:
#             cap = cv2.VideoCapture(url)
#             i = 0
#             while cap.isOpened():
#                 ret, frame = cap.read()
#                 rtmp_time = datetime.datetime.utcnow().timestamp()
#                 if not ret:
#                     break
#                 cv2.imwrite(f"hsl/Hls_{i}_{rtmp_time}.jpg", frame)
#                 i += 1
#         except Exception:
#             print(f"{thread_name} waitting")
#
#
# if __name__ == "__main__":
#
#     try:
#         start_new_thread(
#             load_video,
#             (
#                 "Thread-1",
#                 "http://42.119.139.251:8080/stream/ai-live/playlist.m3u8",
#             ),
#         )
#         start_new_thread(
#             load_video,
#             (
#                 "Thread-2",
#                 "rtmp://42.119.139.251:1935/stream/ai-live",
#             ),
#         )
#     except Exception:
#         print("Errr")
import datetime
from threading import Thread

import cv2

hls_time = None
rtmp_time = None


def get_hls(hls):
    print("Start hls")
    global hls_time
    while True:
        try:
            cap = cv2.VideoCapture(hls)
            if cap.isOpened():
                hls_time = datetime.datetime.utcnow().timestamp()
                return
        except Exception:
            print(f"HLS waitting")


def get_rtmp(rtmp):
    print("Start rtmp")
    global rtmp_time
    while True:
        try:
            cap = cv2.VideoCapture(rtmp)
            if cap.isOpened():
                rtmp_time = datetime.datetime.utcnow().timestamp()
                return
        except Exception:
            print(f"RTMP waitting")


thread1 = Thread(
    name="gethls",
    target=get_hls,
    args=("http://42.119.139.251:8080/stream/ai-live/playlist.m3u8",),
    daemon=True,
)
thread2 = Thread(
    name="getrtmp",
    target=get_rtmp,
    args=("rtmp://42.119.139.251:1935/stream/ai-live",),
    daemon=True,
)

#
# class MyThread(Thread):
#     """docstring for myThread"""
#
#     def __init__(self, name, url, data):
#         super(MyThread, self).__init__()
#         self.name = name
#         self.url = url
#
#     def run(self):
#         print("san sang chay" + self.name)
#         waiting = True
#         while True:
#             try:
#                 cap = cv2.VideoCapture(self.url)
#                 if cap.isOpened():
#                     data = datetime.datetime.utcnow().timestamp()
#
#             except Exception:
#                 if not waiting:
#                     break
#                 print(f"{self.name} waitting")

alls = [
    "person",
    "bicycle",
    "car",
    "motorbike",
    "aeroplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "backpack",
    "umbrella",
    "handbag",
    "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "sofa",
    "pottedplant",
    "bed",
    "diningtable",
    "toilet",
    "tvmonitor",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
]

if __name__ == "__main__":
    import pandas as pd

    df = pd.read_csv("tess2.csv", sep="\t", lineterminator="\r", index_col=0)
    print(df.columns)
    print(df.head(5))
    # print(df)
    group_data = df.groupby(["Make"]).groups  # sum function
    group_data.all().to_csv('./ex.csv')
    print(group_data)
