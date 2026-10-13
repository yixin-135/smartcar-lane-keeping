# -*- coding: utf-8 -*-
import time
import numpy as np
import cv2
from src.scenes.lane_following_threshold import extract_yellow_region,getEdgeImg,roi_mask,process_image,getRLaneLine


def get_x0(img_path):
        imgOri = cv2.imread(img_path)
        small_img = cv2.resize(imgOri, (int(imgOri.shape[1] / 4), int(imgOri.shape[0] / 4)))
        roi_binary = extract_yellow_region(small_img)
        edges = getEdgeImg(roi_binary)

        rows, cols = edges.shape
        points = np.array([[(0, rows), (0, 45), (319, 45), (cols, rows)]])

        roi_edges = roi_mask(edges, points)

        roi_edges = process_image(roi_edges)

        b, slope = getRLaneLine(roi_edges)
        x0 = (int)((45 - b) / slope)
        print('X0 @ y=45:', x0)
        print('slope:', slope)
        print('b:', b)
        print('x0:', x0)


img_path = '/root/syl/car/capture/capture_20260714_101947.jpg'
get_x0(img_path)