"""CNN Q-Network for MiniGrid."""
import torch
import torch.nn as nn


class QNetwork(nn.Module):
    """CNN-based Q-Network for MiniGrid observations.

    Architecture:
        Input (3, 7, 7)
        -> Conv2d(3, 16, k=2) -> ReLU -> (16, 6, 6)
        -> Conv2d(16, 32, k=2) -> ReLU -> (32, 5, 5)
        -> Conv2d(32, 64, k=2) -> ReLU -> (64, 4, 4)
        -> Flatten -> (1024)
        -> Linear(1024, 128) -> ReLU
        -> Linear(128, n_actions)

    Total params: ~140k
    """

    def __init__(self, obs_shape, n_actions):
        super().__init__()
        c, h, w = obs_shape

        self.conv = nn.Sequential(
            nn.Conv2d(c, 16, kernel_size=2),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=2),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=2),
            nn.ReLU(),
        )

        # Compute flattened size
        dummy = torch.zeros(1, c, h, w)
        conv_out_size = self.conv(dummy).view(1, -1).shape[1]

        self.fc = nn.Sequential(
            nn.Linear(conv_out_size, 128),
            nn.ReLU(),
            nn.Linear(128, n_actions),
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)
