import torch.nn.functional as F
import torch
import torch.nn as nn


class PeakDetectionModel_convout(nn.Module):
    def __init__(self):
        super(PeakDetectionModel_convout, self).__init__()

        # 1D Convolution layers
        self.conv1 = nn.Conv1d(1, 16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv1d(32, 64, kernel_size=3, stride=1, padding=1)
        self.conv4 = nn.Conv1d(64, 128, kernel_size=3, stride=1, padding=1)

        # Batch normalization layers
        # self.batch_norm1 = nn.BatchNorm1d(16)
        # self.batch_norm2 = nn.BatchNorm1d(32)
        # self.batch_norm3 = nn.BatchNorm1d(64)
        # self.batch_norm4 = nn.BatchNorm1d(128)

        # Output convolutional layer with 1 channel
        self.output_conv = nn.Conv1d(128, 1, kernel_size=1, stride=1)

    def forward(self, x):
        # Input shape: (batch_size, 1, sequence_length)

        # Convolutional layers with batch normalization and relu activation
        # x = F.relu(self.batch_norm1(self.conv1(x)))
        # x = F.relu(self.batch_norm2(self.conv2(x)))
        # x = F.relu(self.batch_norm3(self.conv3(x)))
        # x = F.relu(self.batch_norm4(self.conv4(x)))

        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))

        # Apply output convolutional layer with 1 channel
        x = self.output_conv(x)

        # Apply sigmoid activation for peak detection
        x = torch.sigmoid(x)

        return x[:, -1, :]  # Squeeze the channel dimension for a 1D output
