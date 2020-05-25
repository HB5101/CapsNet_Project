import idx2numpy
import matplotlib.pyplot as plt
%matplotlib inline
import numpy as np
import seaborn as sns

from keras.utils import to_categorical

#loading training dataset
fileX = '/content/train-images.idx3-ubyte'          #file location
X_train_img = idx2numpy.convert_from_file(fileX)    #X_train_img.shape=(60000, 28, 28)

#loading training labels
fileY="/content/train-labels.idx1-ubyte"
Y_train = idx2numpy.convert_from_file(fileY)

y_train = to_categorical(Y_train.astype('float32'))  #y_train.shape=(60000, 10)

#loading test image
fileXt = "/content/t10k-images.idx3-ubyte"
Xt_test_img = idx2numpy.convert_from_file(fileXt)

x_test = Xt_test_img.reshape(-1, 28, 28, 1).astype('float32')  #x_test.shape=(10000, 28, 28, 1)

#loading Test label
fileYt = "/content/t10k-labels.idx1-ubyte"
Y_test = idx2numpy.convert_from_file(fileYt)

y_test = to_categorical(Y_test.astype('float32'))     #y_test.shape=(10000, 10)

x_train = X_train_img.reshape(-1, 28, 28, 1).astype('float32')        #x_train.shape=(60000, 28, 28, 1)

#EDA of training dataset: 

length=np.zeros((10,1))
kj=[]
for i in Y_train:
    length[i]=length[i]+1
for i in range(len(length)):
    kj.append([i,length[i][0]])
labels=dict(kj) 
plt.figure(figsize = (10, 5))
sns.barplot(x = list(labels.keys()), y = list(labels.values()), palette = 'Set3')
plt.ylabel('Label')
plt.xlabel('Count of Samples/Observations')
for i in range(len(length)):
    per=(length[i][0]/sum(length)[0])*100
    print("% of the total data: "+str(i)+" ==> "+str(per)+" %")
    
#data between 0-1
x_train=x_train/255
x_test=x_test/255


