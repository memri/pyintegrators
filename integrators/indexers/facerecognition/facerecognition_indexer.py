# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/indexers.FaceRecognitionIndexer.ipynb (unless otherwise specified).

__all__ = ['FaceRecognitionIndexer']

# Cell
from ...data.schema import *
from ...data.basic import *
from ...data.itembase import *
from ...pod.client import PodClient
from ..indexer import IndexerBase, get_indexer_run_data, IndexerData, test_registration
from .. import *
from ...imports import *
from .photo import *
from fastprogress.fastprogress import progress_bar

# Cell
from insightface.model_zoo.face_recognition import arcface_r100_v1
from insightface.model_zoo.face_detection   import retinaface_r50_v1
from insightface.model_zoo.face_genderage   import genderage_v1
from insightface.app.face_analysis          import FaceAnalysis
from insightface.utils import face_align

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

    def get_embedding(self, img, normalized=True):
        x = img.data if isinstance(img, IPhoto) else img
        return self.recognition_model.get_embedding(x).flatten()

    def get_crops(self, photos):
        crop_photos = []
        for i, photo in enumerate(progress_bar(photos)):
            boxes, landmarks = self.predict_boundingboxes(photo)
            crop_photos += [IPhoto.from_np(c) for c in photo.get_crops(boxes, landmarks)]
        return crop_photos