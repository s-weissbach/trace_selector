import torch.nn.functional as F
import torch
import torch.nn as nn
import pytorch_lightning as pl
import torch.nn.functional as F


class PeakDetectionModel_convout(pl.LightningModule):
    def __init__(self):
        super(PeakDetectionModel_convout, self).__init__()

        # 1D Convolution layers
        self.conv1 = nn.Conv1d(1, 32, kernel_size=5, stride=1, padding=2)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=5, stride=1, padding=2)
        self.conv3 = nn.Conv1d(64, 128, kernel_size=3, stride=1, padding=1)

        # Batch normalization layers
        self.batch_norm1 = nn.BatchNorm1d(32)
        self.batch_norm2 = nn.BatchNorm1d(64)
        self.batch_norm3 = nn.BatchNorm1d(128)

        # Max pooling layers
        self.pool = nn.MaxPool1d(kernel_size=1, stride=1)

        # Output convolutional layer with 1 channel
        self.output_conv = nn.Conv1d(128, 1, kernel_size=1, stride=1)

    def forward(self, x):
        # Input shape: (batch_size, 1, sequence_length)

        # Convolutional layers with batch normalization and relu activation
        x = F.relu(self.batch_norm1(self.conv1(x)))
        x = self.pool(x)
        x = F.relu(self.batch_norm2(self.conv2(x)))
        x = self.pool(x)
        x = F.relu(self.batch_norm3(self.conv3(x)))
        x = self.pool(x)

        # Apply output convolutional layer with 1 channel
        x = self.output_conv(x)

        # Apply sigmoid activation for peak detection
        x = torch.sigmoid(x)

        return x[:, -1, :]  # Squeeze the channel dimension for a 1D output

    def training_step(self, batch, batch_idx):
        data, targets = batch
        outputs = self(data)
        loss = F.binary_cross_entropy(outputs, targets)
        self.log("train_loss", loss, on_step=False, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        data, targets = batch
        outputs = self(data)
        loss = F.binary_cross_entropy(outputs, targets)
        self.log("val_loss", loss, on_step=False, on_epoch=True, prog_bar=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.001)
