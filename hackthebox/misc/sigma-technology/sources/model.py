import itertools
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

def unpack(x):
    return x[0] if x.shape[0] == 1 else x

def normalize(img):
    __layer = tf.keras.layers.Normalization(axis=-1, mean=MEAN_RGB, variance=STD_RGB**2)
    __image = __layer(img)
    return __image[None, ...]

def denormalize(x, mean=MEAN_RGB, deviation=STD_RGB):
    __mean = tf.broadcast_to(tf.convert_to_tensor(mean, dtype=tf.float32), [32, 32, 3])
    __deviation = tf.broadcast_to(tf.convert_to_tensor(deviation, dtype=tf.float32), [32, 32, 3])
    return tf.math.round(tf.math.multiply(unpack(x), __deviation) + __mean)

################################################################### __predictions

def predict(x):
    return SIGMA(x)[0]
    # __index = np.argmax(__confidence)
    # return __index, __confidence[__index], CLASS_NAMES[__index]

############################################################# adversarial noise

loss = tf.keras.losses.CategoricalCrossentropy()

def fgsm_pattern(image, index, model=SIGMA):
    with tf.GradientTape() as __tape:
        __tape.watch(image)
        __prediction = model(image)
        __loss = loss(index, __prediction)

    # Get the gradients of the loss w.r.t to the input image.
    return __tape.gradient(__loss, image)
    # Get the sign of the gradients to create the perturbation
    # return tf.sign(__gradient)

index = tf.one_hot([DOG_INDEX], len(CLASS_NAMES))
perturbations = fgsm_pattern(normalize(julius), index, SIGMA)

###############################################  most significant perturbations

def argmax(a, n):
    __a_flat = a.flatten()
    __i_flat = __a_flat.argsort()[-n:] # Find the indices in the 1D array
    __x, __y = np.unravel_index(__i_flat, a.shape) # convert the 1D indices back into coordinates

    return zip(__x, __y) # format as (x, y) tuples

def fgsm_most(gradient, count=5):
    __gradient = unpack(gradient) # remove single value dimensions
    __norm = tf.norm(__gradient, axis=-1).numpy() # as numpy array instead of tensor
    __indices = list(itertools.chain.from_iterable([[(__i[0], __i[1], __j) for __j in range(3)] for __i in list(argmax(__norm, count))]))
    __values = [tf.sign(__gradient)[__i].numpy() for __i in __indices]
    return tf.sparse.SparseTensor(indices=__indices, values=__values, dense_shape=__gradient.shape)

# most_significant_perturbations = 

####################################################################### display

def interpret(prediction):
    for i in range(prediction.shape[-1]):
        print(CLASS_NAMES[i], ': ', '{:%}'.format(float(prediction[0][i])))

plt.figure()
plt.imshow(julius)
plt.imshow(perturbations[0])
# plt.imshow(perturbations[0] * 0.5 + 0.5)  # To change [-1, 1] to [0,1]
plt.show()
