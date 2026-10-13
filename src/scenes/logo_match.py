import cv2
import numpy as np
import os

class TemplateMatcher:
    def __init__(self, template_dir='/home/HwHiAiUser/Car/src/scenes/templates', match_threshold=0.7, nms_threshold=0.9):
        self.templates = {}
        self.match_threshold = match_threshold
        self.nms_threshold = nms_threshold

        # 加载模板
        for name in ['left_1','left_2', 'left_3','right_1','right_2','right_3','turnaround_1','turnaround_2']:
            path = os.path.join(template_dir, f'{name}.jpg')
            template = cv2.imread(path, 0)
            template = cv2.resize(template,(0,0),fx=0.25,fy=0.25) #为加快模型匹配速度，将模板缩放为原来的1/4
            if template is None:
                print(f"[Warning] Template loading failed:{path}")
            else:
                self.templates[name] = template

    def filter_boxes(self, boxes):
        count = {}

        for b in boxes:
            c = b[4]
            count[c] = count.get(c, 0) + 1
        max_class = max(count, key=lambda k: count[k])
        max_boxes = [b for b in boxes if b[4] == max_class]
        best_box = max_boxes[0]
        for b in max_boxes[1:]:
            if b[5] > best_box[5]:
                best_box = b
        return [best_box]

    def infer(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = []

        for label, template in self.templates.items():
            label = label.split('_')[0]
            h, w = template.shape
            res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= self.match_threshold)

            boxes = []
            scores = []

            for pt in zip(*loc[::-1]):
                x1, y1 = pt
                x2, y2 = x1 + w, y1 + h
                boxes.append([x1, y1, x2, y2])
                scores.append(res[pt[1], pt[0]])

            keep_idxs = self.nms(boxes, scores, self.nms_threshold)
            for i in keep_idxs:
                x1, y1, x2, y2 = boxes[i]
                score = scores[i]
                results.append([x1, y1, x2, y2, label, score])
        if len(results) > 1:
              results = self.filter_boxes(results)
        print(f'------------------{results}-------------------')

        return results

    def nms(self, boxes, scores, threshold):
        if not boxes:
            return []
        boxes = np.array(boxes)
        scores = np.array(scores)

        x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            iou = inter / (areas[i] + areas[order[1:]] - inter)

            inds = np.where(iou <= threshold)[0]
            order = order[inds + 1]

        return keep