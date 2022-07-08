import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

################################################################ interpretation

CLASS_NAMES = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
DOG_INDEX = 5

######################################################################### model

SIGMA = tf.keras.models.load_model('sigmanet.h5')

################################################################### input image

julius = tf.image.decode_image(tf.io.read_file('../images/julius.png'), channels=3)

################################################################# preprocessing

MEAN_RGB = np.array([125.307, 122.95, 113.865])
STD_RGB = np.array([62.9932, 62.0887, 66.7048])

def preprocess(img):
    __img = img
    for i in range(3):
        __img[:, :, i] = (__img[:, :, i] - MEAN_RGB[i]) / STD_RGB[i]
    return np.array([__img])

def preprocess(img):
    __layer = tf.keras.layers.Normalization(axis=-1, mean=MEAN_RGB, variance=STD_RGB**2)
    __image = __layer(img)
    return __image[None, ...]

def postprocess(x):
    pass

################################################################### __predictions

def predict(x):
    __confidence = SIGMA(x)[0]
    __index = np.argmax(__confidence)
    return __index, __confidence[__index], CLASS_NAMES[__index]

############################################################# adversarial noise

loss = tf.keras.losses.CategoricalCrossentropy()

def create_adversarial_pattern(image, index, model=SIGMA):
    with tf.GradientTape() as __tape:
        __tape.watch(image)
        __prediction = model(image)
        __loss = loss(index, __prediction)

    # Get the gradients of the loss w.r.t to the input image.
    return __tape.gradient(__loss, image)
    # Get the sign of the gradients to create the perturbation
    # return tf.sign(__gradient)

index = tf.one_hot([DOG_INDEX], len(CLASS_NAMES))
perturbations = create_adversarial_pattern(preprocess(julius), index, SIGMA)

###############################################  most significant perturbations

def argmax(a, n):
    __a_flat = a.flatten()

    # Find the indices in the 1D array
    __i_flat = __a_flat.argsort()[-n:]

    # convert the 1D indices back into coordinates
    __x, __y = np.unravel_index(__i_flat, a.shape)

    # format as (x, y) tuples
    return zip(__x, __y)

norm = tf.norm(perturbations[0], axis=-1).numpy() # as numpy array instead of tensor
most_significant_coordinates = list(argmax(norm, 5))
# most_significant_perturbations = 

####################################################################### display

plt.figure()
plt.imshow(julius)
plt.imshow(perturbations[0])
# plt.imshow(perturbations[0] * 0.5 + 0.5)  # To change [-1, 1] to [0,1]
plt.show()
