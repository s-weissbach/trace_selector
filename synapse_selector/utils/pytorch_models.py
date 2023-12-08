import torch
import numpy as np

from synapse_selector.utils.iglu_cnn import PeakDetectionModel_convout


class torch_cnn_model:
    def __init__(
        self,
    ) -> None:
        self.model = PeakDetectionModel_convout()
        self.weights_loaded = False
        self.preds = []

    def load_weights(self, model_path: str) -> None:
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        self.weights_loaded = True

    def predict(self, arr: np.ndarray, threshold: float = 0.5) -> list[int]:
        # reshape input to (1, 1, length)
        input_tensor = torch.reshape(
            torch.tensor(arr, dtype=torch.float), (1, 1, arr.shape[0])
        )
        self.preds = np.array(self.model(input_tensor).detach().flatten())
        infered_peaks = list(np.argwhere(self.preds > threshold).flatten())
        return infered_peaks

    def update_predictions(self, threshold: float) -> list[int]:
        infered_peaks = list(np.argwhere(self.preds > threshold).flatten())
        return infered_peaks
