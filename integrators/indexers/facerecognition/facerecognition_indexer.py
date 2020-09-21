# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/indexers.FaceRecognitionIndexer.ipynb (unless otherwise specified).

__all__ = ['FaceRecognitionIndexer', 'IPhoto', 'show_images']

# Cell
from ...data.schema import *
from ...data.basic import *
from ...data.itembase import *
from ...pod.client import PodClient
from ..indexer import IndexerBase, get_indexer_run_data, IndexerData, test_registration
from .. import *
from ...imports import *
import pycountry, requests
import reverse_geocoder as rg

# Cell
from insightface.model_zoo.face_recognition import arcface_r100_v1
from insightface.model_zoo.face_detection   import retinaface_r50_v1
from insightface.model_zoo.face_genderage   import genderage_v1
from insightface.app.face_analysis          import FaceAnalysis
from insightface.utils import face_align


from matplotlib.pyplot import imshow
from matplotlib import patches
from matplotlib.collections import PatchCollection

import cv2
import matplotlib.pyplot as plt
import math

# Cell
class FaceRecognitionIndexer(IndexerBase):
    """Recognizes photos from faces."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recognition_model = arcface_r100_v1()
        self.recognition_model.prepare(-1);
        self.detection_model = retinaface_r50_v1()
        self.detection_model.prepare(-1);

    def compare(self, img1, img2):
        sim = round(float(self.recognition_model.compute_sim(img1, img2)), 2)
        return sim

    def predict_boundingboxes(self, iphoto):
        boxes, landmarks = self.detection_model.detect(iphoto.data)
        return boxes, landmarks


# Cell
class IPhoto(Photo):

    def __init__(self, file=None, *args, **kwargs):
        super().__init__(file=file, *args, **kwargs)
        self.data = cv2.imread(str(file)) if file is not None else None

    def show(self):
        fig,ax = plt.subplots(1)
        fig.set_figheight(15)
        fig.set_figwidth(15)
        ax.axis('off')
        imshow(self.data[:,:,::-1])

    def draw_boxes(self, boxes):
        print(f"Plotting {len(boxes)} face boundingboxes")
        fig,ax = plt.subplots(1)
        fig.set_figheight(15)
        fig.set_figwidth(15)
        ax.axis('off')

        # Display the image
        ax.imshow(self.data[:,:,::-1])

        ps = []
        # Create a Rectangle patch
        for b in boxes:
            rect = self.box_to_rect(b)
            ax.add_patch(rect)
            ps.append(rect)
        plt.show()

    def get_crops(self, boxes, landmarks=None):
        crops = []
        if landmarks is None:
            print("you are getting unnormalized crops, which are lower quality for recognition")
        for i, b in enumerate(boxes):
            b = [max(0, int(x)) for x in b]

            if landmarks is not None:
                crop = face_align.norm_crop(self.data, landmark = landmarks[i])
            else:
                crop = self.data[b[1]:b[3], b[0]:b[2], :]
            crops.append(crop)
        return crops

    def plot_crops(self, boxes, landmarks=None):
        crops = self.get_crops(boxes, landmarks)
        show_images(crops, cols=3)

    @staticmethod
    def box_to_rect(box):
        x = box[0]
        y = box[1]
        w = box[2]-box[0]
        h = box[3]-box[1]
        return patches.Rectangle((x,y),w,h, linewidth=2,edgecolor='r',facecolor='none')


# Cell
def show_images(images, cols = 3, titles = None):
    assert((titles is None) or (len(images) == len(titles)))
    n_images = len(images)
    if titles is None: titles = ["" for i in range(1,n_images + 1)]
    fig = plt.figure()
    for n, (image, title) in enumerate(zip(images, titles)):
        a = fig.add_subplot(int(np.ceil(n_images/float(cols))), cols , n + 1)
        a.axis('off')
        if image.ndim == 2:
            plt.gray()
        plt.imshow(image[:,:,::-1])
        a.set_title(title)
    fig.set_size_inches(np.array(fig.get_size_inches()) * n_images)
    plt.show()