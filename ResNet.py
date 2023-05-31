import torch
import torch.nn as nn
import torch.nn.functional as F

COLUMN = 8
WIDTH = 8

class ResNet(nn.Module):
    def __init__(self, numResBlocks, numHidden, device) -> None:
        super().__init__()
        
        self.device = device
        self.startBlock = nn.Sequential(
            nn.Conv2d(8, numHidden, kernel_size=8, padding=1),
            nn.BatchNorm2d(numHidden),
            nn.ReLU()
        )
        
        self.backBone = nn.ModuleList(
            [ResBlock(numHidden) for i in range(numResBlocks)]
        )
       
        self.policyHead = nn.Sequential(
            nn.Conv2d(numHidden, 32, kernel_size=8, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(32 * COLUMN * WIDTH, COLUMN*WIDTH)
        ) 
        
        self.valueHead = nn.Sequential(
            nn.Conv2d(numHidden, 8, kernel_size=8, padding=1),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(8*WIDTH*COLUMN, 1),
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