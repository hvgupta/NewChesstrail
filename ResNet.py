import torch
import torch.nn as nn
import torch.nn.functional as F
from game import *

IMGCOLUMN = 9
IMGWIDTH = 9

class ResNet(nn.Module):
    def __init__(self, numResBlocks, numHidden, device) -> None:
        super().__init__()
        
        self.device = device
        self.startBlock = nn.Sequential(
            nn.Conv2d(3, numHidden, kernel_size=9, padding=4),
            nn.BatchNorm2d(numHidden),
            nn.ReLU()
        )
        
        self.backBone = nn.ModuleList(
            [ResBlock(numHidden) for i in range(numResBlocks)]
        )
       
        self.policyHead = nn.Sequential(
            nn.Conv2d(numHidden, 452, kernel_size=9, padding=4),
            nn.BatchNorm2d(452),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(452 * IMGCOLUMN * IMGWIDTH, 3288)
        ) 
        
        self.valueHead = nn.Sequential(
            nn.Conv2d(numHidden, 32, kernel_size=9, padding=4),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(32*IMGCOLUMN*IMGWIDTH, 1),
            nn.Tanh()
        )
        self.to(device)
    
    def forward(self,x):

        x = self.startBlock(x)
        for resBlock in self.backBone:
            x = resBlock(x)
        policy = self.policyHead(x)
        value = self.valueHead(x)
        return policy, value

class ResBlock(nn.Module):
    def __init__(self, num_hidden) -> None:
        super().__init__()
        
        self.conv1 = nn.Conv2d(num_hidden, num_hidden, kernel_size= 3, padding= 1)
        self.bn1 = nn.BatchNorm2d(num_hidden)
        self.conv2 = nn.Conv2d(num_hidden,num_hidden, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(num_hidden)
        
    def forward(self,x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x += residual
        x = F.relu(x)
        return x