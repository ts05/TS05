import Data_load_indata as dl
import Data_load_outdata as dlt
import os
import numpy as np
from tensorflow import keras
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.python.keras.callbacks import TensorBoard
from keras.callbacks import EarlyStopping
from time import time
from keras import backend as K

K.set_image_dim_ordering('th')

current_path = os.getcwd()

DataX = list()
DataY = list()

modelname = input("Input model name to save :: ")
totalepoch = 1000

model = keras.Sequential()
model.add(keras.layers.Conv2D(32, kernel_size=(3,3), input_shape=(10, 10, 1), data_format='channels_last', activation='relu'))
model.add(keras.layers.BatchNormalization())
model.add(keras.layers.MaxPooling2D(pool_size=(2,2)))
model.add(keras.layers.Conv2D(64, kernel_size=(3,3), activation='relu'))
model.add(keras.layers.BatchNormalization())
model.add(keras.layers.MaxPooling2D(pool_size=(2,2)))

model.add(keras.layers.Flatten())
model.add(keras.layers.Dense(2,activation='sigmoid'))

model.summary()

## Data 순서 :: pir만 사용

dl.Data_load("None", DataX, DataY)
dl.Data_load("Human", DataX, DataY)

dlt.Data_load("None", DataX, DataY)
dlt.Data_load("Human", DataX, DataY)

DataX = np.asarray(DataX)
DataY = np.asarray(DataY)
DataX = np.reshape(DataX, (int(DataX.__len__()/4), 4, 100))

x_data =list()

for i in range(len(DataX)):
    x_data.append(DataX[i][0])

x_data = np.asarray(x_data)
x_data = np.reshape(x_data, (-1, 10, 10, 1))

tensorboard = TensorBoard(log_dir="logs/{}".format(time()))

model.compile(optimizer=tf.train.AdamOptimizer(learning_rate=0.001),
              loss='mean_squared_error',
              metrics=['acc'])

X_train, X_test, Y_train, Y_test = train_test_split(x_data, DataY, test_size=0.3, random_state=777, shuffle=True)

#early_stopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=12, verbose=0, mode='auto')
model.fit(X_train, Y_train, epochs=totalepoch, batch_size=256, shuffle='True', validation_data=(X_test, Y_test), verbose=1, callbacks=[tensorboard])

x_validate = X_train[:3000]
y_validate = Y_train[:3000]

results = model.evaluate(x_validate, y_validate)

print("Validate data[loss, accuracy] :: ")
print(results)

print(model.predict_classes(X_test[:1, :], verbose=0))
print('----------------------------------------------')

model_json = model.to_json()

with open("Models/" + modelname + ".json", "w") as json_file :
    json_file.write(model_json)

model.save_weights("Models/" + modelname + ".h5")

print(modelname)
print("Model Saved...!")

print("Train Dataset .. :: ")
print(X_train.shape)
print("Validate Dataset .. :: ")
print(X_test.shape)
