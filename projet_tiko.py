# -*- coding: utf-8 -*-
"""Projet_TIKO.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PPVYB2S_FUZgD28nqkjVOhH1W4s2y6sl
"""

#DEZIPPER 
!unzip 'dataset.zip'

!unzip 'datasetFISH.zip'

"""

```
# This is formatted as code
```

# Prepare Data"""

import os
import pandas as pd
from torchvision.io import read_image
import glob
from torchvision.transforms import Compose, Resize, RandomHorizontalFlip, RandomVerticalFlip, RandomRotation, Normalize, ToTensor
from torch.utils.data import Dataset, DataLoader
import torch
import numpy as np
import torch.optim as optim
import torch.nn as nn

class CustomImageDataset(Dataset):
    def __init__(self, mode ,img_dir, transform=None):
        #set of image files
        self.img_dir = img_dir 
        #mode is either 'train' or 'val' or 'test'
        self.mode = mode 
        #transformations of images 
        self.transform = transform  
        #get all folders in directory
        folder_mode = os.path.join(img_dir, mode)
        self.list_image = glob.glob(folder_mode +"/**/*.jpg")
        self.list_label = [image.split("/")[-2] for image in self.list_image]
        unique_label = np.unique(self.list_label)
        self.correspondance_label_identifiant= {label:i for i,label in enumerate(unique_label)}

    def __len__(self):
        return len(self.list_label)

    def __getitem__(self, idx):
        image = read_image(self.list_image[idx]).float()
        label = torch.tensor(self.correspondance_label_identifiant[self.list_label[idx]])
        if self.transform:
            image = self.transform(image)
        return image, label

import glob
from skimage.io import imread
list_tmp=[]
list_std=[]
for image in glob.glob("/dataset2/**/**/*.jpg"):
    im=imread(image)
    list_tmp.append( im.mean(axis=(0,1)))
    list_std.append( im.std(axis=(0,1)))
list_tmp=np.array(list_tmp)
list_std=np.array(list_std)
print(list_tmp.mean(0),list_std.mean(0))

#get mu and std for the normalization
training_data = CustomImageDataset('train', 'dataset')

#train_dataloader = DataLoader(training_data, batch_size, shuffle=True)
#test_dataloader = DataLoader(test_data, batch_size, shuffle=True)
#val_dataloader = DataLoader(val_data, batch_size, shuffle=True)

mu, std = get_mu_std(training_data)

transform = Compose([
                     # Image Smallest size = 276 
                     #Resize((276,276)),
                     #RandomHorizontalFlip(),
                     #RandomRotation((-180,180)),
                    # RandomVerticalFlip(), 
                    # Normalize((99.3, 109.6, 98.8), (45.1, 44.5, 42.5)) #for full iNaturalis data
                     Totensor(),
                     Normalize((100.17197179, 116.51144719, 103.37440195), (33.75782695, 34.56523636, 32.56752923)) #for filtred iNaturalis dataset 
])

training_data = CustomImageDataset('train', 'dataset', transform=transform)
test_data = CustomImageDataset('test', 'dataset', transform=transform)
val_data = CustomImageDataset('val', 'dataset', transform=transform)
print('AAA', len(training_data))
print('BBB', len(val_data))
batch_size= 20

train_dataloader = DataLoader(training_data, batch_size, shuffle=True)
test_dataloader = DataLoader(test_data, batch_size, shuffle=True)
val_dataloader = DataLoader(val_data, batch_size, shuffle=True)

def get_mu_std(dataset):
    ######################################
    # START code block: write code below
    ######################################
    mu, std = None, None

    nb_data = len(dataset)
    im,_ = dataset[0]
    image = np.asarray(im)
    size_im = image.shape[0]


    sum= np.zeros(3)
    sumSq = np.zeros(3)

    total = size_im*size_im*nb_data

    for i in range (nb_data):
      img,_ = dataset[i]
      img_array = np.asarray(img)/255

      sum += np.sum(img_array, (0,1))
      sumSq += np.sum(img_array**2, (0,1))

    mu = sum/total
    std= np.sqrt((sumSq/total - mu**2) * (total/(total-1)))

    ######################################
    # END code block
    ######################################
    return mu, std

training_data.__getitem__(3)

"""Define the Neural Network

Define Criterion for Loss and Optimizer

Training Time !

# For our **own model**
"""

import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5) # 3 channels because RGB image
        self.BN1 = nn.BatchNorm2d(6)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.BN2 = nn.BatchNorm2d(16)
        self.conv3 = nn.Conv2d(16, 32, 5)
        self.BN3 = nn.BatchNorm2d(32)
        self.conv4 = nn.Conv2d(32, 32, 5)
        self.BN4 = nn.BatchNorm2d(32)
        self.conv5 = nn.Conv2d(32, 32, 5)
        self.BN5 = nn.BatchNorm2d(32)
        self.fc1 = nn.Linear(512, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 14)

    def forward(self, x):
        x = self.BN1(self.conv1(x))
        x = self.pool(F.relu(x))
        x = self.BN2(self.conv2(x))
        x = self.pool(F.relu(x))
        x = self.BN3(self.conv3(x))
        x = self.pool(F.relu(x))
        x = self.BN4(self.conv4(x))
        x = self.pool(F.relu(x))
        x = self.BN5(self.conv5(x))
        x = self.pool(F.relu(x))
        # flatten all dimensions except batch, transform x (an array) into a list of pixel (1-dimensional)
        # for Linear layers
        x = torch.flatten(x, 1) 
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

if torch.cuda.is_available():
  device = "cuda"
  net = Net().to(device)
else:
  net = Net()

criterion = nn.CrossEntropyLoss() 
#For optimization, SGD with momentum to adjust parameters
lr = 1e-3
momentum = 0.9
#optimizer = optim.SGD(net.parameters(), lr, momentum) 
optimizer = optim.Adam(net.parameters(), lr)

#Compute accuray and loss for a model (neural network), criterion is the loss we have defined
def evaluate(model, criterion, dataloader):
  correct = 0
  total = 0

  # since we're not training, we don't need to calculate the gradients for our outputs
  # It will reduce memory consumption for computations
  loss = 0
  total_loss = 0
  with torch.no_grad():
      for data in dataloader:
        
          images, labels = data
          images = images.to(device)
          labels = labels.to(device)

          # calculate outputs by running images through the network
          outputs = model(images)
          # the class with the highest energy is what we choose as prediction
          _, predicted = torch.max(outputs, 1) #torch.max(a tensor, 1) return 2 tensors values and indice
          total += labels.size(0)
          correct += (predicted == labels).sum().item()
          #loss += criterion(outputs, labels).item()
          loss += criterion(outputs, labels).item()/labels.size(0)
          #total_loss += 1

  #loss /= total_loss
  accuracy = correct / total
  return loss, accuracy

#For our model
import time
import matplotlib.pyplot as plt
import numpy as np

nb_epoch = 15
Accuracies = []
Loss_train = []
Loss_val = []

start = time.time()
for epoch in range(nb_epoch):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(train_dataloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data
        inputs = inputs.to(device)
        labels = labels.to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # plot statistics
        running_loss += loss.item()
        if i % 5 == 4:    # print every 5 iterations
            Loss_train.append(running_loss / 5)
            loss_val, accuracy = evaluate(net, criterion, val_dataloader)
            Loss_val.append(loss_val)
            Accuracies.append(accuracy)
            
            print('accuracy ', accuracy, 'loss_train ', Loss_train[-1], 'loss_val ', loss_val)
            running_loss = 0.0

plt.figure()
plt.plot( Accuracies, '-', label= 'Accuracy on val data')
plt.legend(loc = 'upper right')
plt.xlabel("Iterations")

plt.figure()
plt.plot(Loss_train, '-', label='Loss on train data')
plt.plot(Loss_val, '-', label= 'Loss on val data')
plt.legend(loc = 'upper right')
plt.xlabel("Iterations")

plt.show()

print('Finished Training ; Corresponding Time :', time.time()-start,'s' )

"""# For PRE TRAINED **VGG16**"""

#A partir du modele pré-entrainé vgg16 (Attention : dimension de l'output)

import torchvision

device = 'cuda'
net2 = torchvision.models.vgg16(pretrained=True)
net2 = net2.to(device)

criterion = nn.CrossEntropyLoss() 
#For optimization, SGD with momentum to adjust parameters
lr = 1e-3
momentum = 0.9
#optimizer = optim.SGD(net.parameters(), lr, momentum) 
optimizer = optim.Adam(net2.parameters(), lr)

def evaluate_vgg16(model, criterion, dataloader):
  correct = 0
  total = 0

  # since we're not training, we don't need to calculate the gradients for our outputs
  # It will reduce memory consumption for computations
  loss = 0
  total_loss = 0

  with torch.no_grad():
      for data in dataloader:
        
          images, labels = data
          images = images.to(device)
          labels = labels.to(device)

          # calculate outputs by running images through the network
          outputs = model(images)[:, :23]
          # the class with the highest energy is what we choose as prediction
          _, predicted = torch.max(outputs, 1) #torch.max(a tensor, 1) return 2 tensors values and indice
          total += labels.size(0)
          correct += (predicted == labels).sum().item()

          loss += criterion(outputs, labels).item()
          total_loss += 1

  loss /= total_loss
  accuracy = correct / total
  return loss, accuracy

#For PRE TRAINED VGG16

import matplotlib.pyplot as plt
import time

nb_epoch = 15
Accuracies = []
Loss_train = []
Loss_val = []
start =time.time()
for epoch in range(nb_epoch):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(train_dataloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data
        inputs = inputs.to(device)
        labels = labels.to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net2(inputs)[:, :14]
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # plot statistics
        running_loss += loss.item()
        if i % 5 == 4:    # print every 5 iterations
            Loss_train.append(running_loss / 5)
            loss_val, accuracy = evaluate_vgg16(net2, criterion, val_dataloader)
            Loss_val.append(loss_val)
            Accuracies.append(accuracy)
            print('accuracy ', accuracy, 'loss_train ', Loss_train[-1], 'loss_val ', loss_val)
            running_loss = 0.0

plt.figure()

plt.plot(Accuracies, '-', label= 'Accuracy on validation data')
plt.legend(loc = 'upper right')
plt.xlabel(f"Iteration with {nb_epoch} echochs")
plt.figure()

plt.plot(Loss_train, '-', label='Loss on train data')
plt.plot(Loss_val, '-', label= 'Loss on val data')
plt.xlabel(f"Iteration with {nb_epoch} echochs")
plt.title("Performances with Pre-trained VGG16 Model")
plt.legend(loc = 'upper right')

plt.show()

print('Finished Training; Corresponding Time: ', time.time()-start, 's')

plt.figure()
plt.plot(Accuracies, '-', label= 'Accuracy on validation data')
plt.figure()
plt.plot(Loss_train, '-', label='Loss on train data')
plt.plot(Loss_val, '-', label= 'Loss on val data')
plt.ylim([0, 3])
plt.xlabel(f"Iteration with {nb_epoch} echochs")
plt.title("Performances with Pre-trained VGG16 Model")
plt.legend(loc = 'center right')

plt.show()

"""Display image and prediction for test data and print score"""

import torchvision
def imshow(inp, title=None):
    """Imshow for Tensor."""
    inp = inp.cpu()
    
    inp = inp.numpy().transpose((1, 2, 0))
    
    mean = np.array([100.17197179, 116.51144719, 103.37440195])
    std = np.array([33.75782695, 34.56523636, 32.56752923])
    inp = std * inp + mean
   
    #inp = np.clip(inp, 0, 1)
    #inp*255/inp.max()
    plt.imshow((inp*255/inp.max()).astype(int))

    if title is not None:
        plt.title(title)

# Get a batch of test data
inputs, classes = next(iter(test_dataloader))
inputs = inputs.to(device)
classes = classes.to(device)

# Make a grid from batch
out = torchvision.utils.make_grid(inputs[:8])
#Truth
imshow(out)
plt.show()
#Prediction
outputs = net(inputs)
_, predicted = torch.max(outputs, 1)
print('Truth: ', ' '.join('%5s' % test_data.list_label[x] for x in classes[:8]))
print('Predicted: ', ' '.join('%5s' % test_data.list_label[predicted[j]] for j in range(8)))

print("Loss and accuracy evaluate on test data are: ",evaluate(net, criterion, test_dataloader))

"""Save the trained model for mobile app"""

net2.eval()

#input for example
input_tensor = torch.rand(1,3,276,276)
input_tensor = input_tensor.to(device)

script_model = torch.jit.trace(net2,input_tensor)
script_model.save("mobile_net2.pt")

#Save model 
trained_model = 'model_net2.pth'
torch.save(net2.state_dict(), trained_model)

?torch.rand()