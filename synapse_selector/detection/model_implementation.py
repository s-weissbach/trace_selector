import torch.nn.functional as F
import torch
import torch.nn as nn


class PeakDetectionModel(nn.Module):
    def __init__(self):
        super(PeakDetectionModel, self).__init__()

        # 1D Convolution layers
        self.conv1 = nn.Conv1d(1, 32, kernel_size=9, stride=1, padding=4)
        self.conv2 = nn.Conv1d(33, 32, kernel_size=7, stride=1, padding=3)
        self.conv3 = nn.Conv1d(33, 32, kernel_size=5, stride=1, padding=2)
        self.conv4 = nn.Conv1d(33, 32, kernel_size=3, stride=1, padding=1)

        # Batch normalization layers
        self.batch_norm1 = nn.BatchNorm1d(32)
        self.batch_norm2 = nn.BatchNorm1d(32)
        self.batch_norm3 = nn.BatchNorm1d(32)
        self.batch_norm4 = nn.BatchNorm1d(32)

        # Output convolutional layer with 1 channel
        self.output_conv = nn.Conv1d(129, 1, kernel_size=1, stride=1)

    def forward(self, x):
        # Input shape: (batch_size, 1, sequence_length)

        # Convolutional layers with batch normalization and relu activation
        x1 = F.relu(self.batch_norm1(self.conv1(x)))
        x2 = F.relu(self.batch_norm2(self.conv2(torch.cat([x, x1], dim=1))))
        x3 = F.relu(self.batch_norm3(self.conv3(torch.cat([x, x2], dim=1))))
        x4 = F.relu(self.batch_norm4(self.conv4(torch.cat([x, x3], dim=1))))

        # Apply output convolutional layer with 1 channel
        out = torch.sigmoid(self.output_conv(
            torch.cat([x, x1, x2, x3, x4], dim=1)))

        return out[:, -1, :]  # Squeeze the channel dimension for a 1D output
