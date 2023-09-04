# script for activity recognition

import torch
from matplotlib import pyplot as plt
import numpy as np
import pandas

model = torch.hub.load('ultralytics/yolov5', 'custom', path = 'yolov5/runs/train/exp/weights/last.pt', force_reload = True)
activityImg = "/home/generic/Emm/captures/img-1.png"

results = model(activityImg)

print(results.pandas().xyxy[0].name[0])
