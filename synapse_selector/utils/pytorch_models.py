from .iglu_cnn import PeakDetectionModel_convout
import torch
import numpy as np


class torch_cnn_model:
    def __init__(
        self,
        model_path: str = "/Users/stephanweissbach/Desktop/synapse_selector_detect/models/anomaly_50_conv-out.pth",
        window_len: int = 50,
    ) -> None:
        self.model = torch.load(model_path)
        self.model.eval()
        self.window_len = window_len

    def prepare_numpy_array(self, arr: np.ndarray):
        to_pad = self.window_len - (len(arr) % self.window_len)
        arr = np.pad(arr, (0, to_pad), mode="constant")
        second_dim = len(arr) // 50
        arr = arr.reshape(second_dim, 1, 50)
        return arr

    def predict(self, arr: np.ndarray)