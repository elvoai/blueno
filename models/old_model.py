import os
import scipy
import numpy as np
import pandas as pd
from torch import nn

import torch
from torch.autograd import Variable
from torch.optim import SGD
from torch.nn import BCELoss

import sys
sys.path.append('../')
import transforms


class Flatten(nn.Module):

    def forward(self, x):
        x = x.view(-1)
        return x


# Constants
in_folder = '../data-1521414749'


# Reading in the data
images = []
for filename in sorted(os.listdir(in_folder)):
    if 'csv' in filename:
        continue
    images.append(np.load(in_folder + '/' + filename))

labels = pd.read_csv(in_folder + '/labels.csv', index_col=0)
labels.sort_index(inplace=True)

resized = np.stack([scipy.ndimage.interpolation.zoom(arr, 32 / 200)
                    for arr in images])

normalized = transforms.normalize(resized)

# Create model
model = nn.Sequential(nn.Conv3d(1, 10, 5),
                      nn.ReLU(),
                      nn.Conv3d(10, 20, 5),
                      nn.ReLU(),
                      Flatten(),
                      nn.Linear(276480, 1000),
                      nn.Linear(1000, 2),
                      nn.Softmax(dim=0))
model.train()

optimizer = SGD(model.parameters(), lr=0.01)
criterion = BCELoss()


for iter in range(10):
    for image3d, label in zip(normalized, labels['label'].values):
        image3d = Variable(torch.Tensor(image3d).unsqueeze(0).unsqueeze(0))
        true_label = Variable(torch.Tensor([int(label == 0), int(label == 1)]))
        optimizer.zero_grad()
        pred_label = model(image3d)
        loss = criterion(pred_label, true_label)
        loss.backward()
        optimizer.step()

    print(str(iter) + ', Current loss:', loss)

for image3d in normalized:
    print(model(images))