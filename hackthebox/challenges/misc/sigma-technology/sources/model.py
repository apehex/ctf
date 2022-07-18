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

JULIUS = tf.image.decode_image(tf.io.read_file('../images/julius.png'), channels=3)

############################################################## image processing

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

def fgsm_pattern(image: tf.Tensor, index: int, model=SIGMA):
    with tf.GradientTape() as __tape:
        __tape.watch(image)
        __prediction = model(image)
        __loss = loss(index, __prediction)

    # Get the gradients of the loss w.r.t to the input image.
    return __tape.gradient(__loss, image)
    # Get the sign of the gradients to create the perturbation
    # return tf.sign(__gradient)

index = tf.one_hot([DOG_INDEX], len(CLASS_NAMES))
perturbations = fgsm_pattern(normalize(JULIUS), index, SIGMA)

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
    return tf.sparse.reorder(
        tf.sparse.SparseTensor(indices=__indices, values=__values, dense_shape=__gradient.shape))

delta = tf.sparse.to_dense(fgsm_most(perturbations))

########################################################## tensor manipulations

def tamper(original: np.ndarray, perturbations: np.ndarray) -> np.ndarray:
    __candidate = original
    for __i in range(0, len(perturbations), 5): # modify the 5 pixels according to the perturbation vector
        for __j in range(3):
            __candidate[int(perturbations[__i]), int(perturbations[__i + 1]), __j] = int(perturbations[__i + 2 + __j])
    return __candidate

#################################################################### evaluation

def score(confidence: tf.Tensor) -> float:
    return float(
        max([confidence[0][__i] for __i in [0, 1, 8, 9]])
        - max([confidence[0][__i] for __i in range(2, 8)]))

def fitness(perturbations: np.ndarray, original: np.ndarray, model=SIGMA) -> float:
    return score(
        confidence=SIGMA(normalize(tamper(original=original, perturbations=perturbations))))

####################################################################### display

def interpret(prediction):
    for i in range(prediction.shape[-1]):
        print(CLASS_NAMES[i], ': ', '{:%}'.format(float(prediction[0][i])))

# plt.figure()
# plt.imshow(JULIUS)
# plt.imshow(perturbations[0])
# # plt.imshow(perturbations[0] * 0.5 + 0.5)  # To change [-1, 1] to [0,1]
# plt.show()

# print("=> predictions for the original image =============")
# interpret(SIGMA(normalize(JULIUS)))
# print("=> predictions for the tampered image =============")
# interpret(SIGMA(normalize(JULIUS) + delta))
