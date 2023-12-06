from .iglu_cnn import PeakDetectionModel_convout
import torch
import numpy as np


class torch_cnn_model:
    def __init__(
        self,
        model_path: str = "./models/anomaly_50_conv-out.pth",
        window_len: int = 50,
    ) -> None:
        # load model
        self.model = torch.load(model_path)
        self.model.eval()
        self.window_len = window_len
        self.to_pad = 0

    def predict(self, arr: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        input_tensor = torch.tensor(arr, dtype=torch.float)
        preds = self.model(input_tensor).detach().flatten()
        infered_peaks = np.argwhere(preds > threshold)[0]
        return infered_peaks
