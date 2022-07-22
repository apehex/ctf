import itertools
import numpy as np
import tensorflow as tf

################################################################ interpretation

CLASS_NAMES = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
DOG_INDEX = 5
TARGET_INDEX = 1

######################################################################### model

SIGMA = tf.keras.models.load_model('sigmanet.h5')

################################################################### input image

JULIUS = tf.image.decode_image(tf.io.read_file('../images/julius.png'), channels=3)

############################################################## image processing

MEAN_RGB = np.array([125.307, 122.95, 113.865])
STD_RGB = np.array([62.9932, 62.0887, 66.7048])

def unpack(x):
    return x[0] if x.shape[0] == 1 else x

def normalize(img: np.ndarray, mean: np.ndarray=MEAN_RGB, deviation: np.ndarray=STD_RGB):
    __layer = tf.keras.layers.Normalization(axis=-1, mean=mean, variance=deviation**2)
    return __layer(img)

def denormalize(x, mean=MEAN_RGB, deviation=STD_RGB):
    __mean = tf.broadcast_to(tf.convert_to_tensor(mean, dtype=tf.float32), x.shape)
    __deviation = tf.broadcast_to(tf.convert_to_tensor(deviation, dtype=tf.float32), x.shape)
    return tf.math.round(tf.math.multiply(unpack(x), __deviation) + __mean).astype(int)

########################################################## tensor manipulations

def _tamper(original: np.ndarray, noise: np.ndarray) -> np.ndarray: # individual version
    __candidate = np.copy(original)
    for __pixel in noise:
        for __j in range(3):
            __candidate[int(original.shape[0] * __pixel[0]), int(original.shape[1] * __pixel[1]), __j] = int(256. * __pixel[2 + __j])
    return __candidate.astype(int)

def tamper(original: np.ndarray, perturbations: np.ndarray) -> np.ndarray: # batch version
    __candidates = np.zeros(shape=(perturbations.shape[0], *original.shape), dtype=int)
    for __i in range(perturbations.shape[0]):
        __candidates[__i] = _tamper(original=original, noise=perturbations[__i])
    return __candidates

#################################################################### evaluation

def score(confidence: tf.Tensor) -> float:
    return (
        confidence[:, TARGET_INDEX] # misclassify as a car
        - confidence[:, DOG_INDEX]) # TODO!!

def fitness(perturbations: np.ndarray, original: np.ndarray, model=SIGMA) -> float:
    return score(
        confidence=model.predict_on_batch(normalize(tamper(original=original, perturbations=perturbations))))

####################################################################### display

def interpret(prediction):
    for i in range(prediction.shape[-1]):
        print(CLASS_NAMES[i], ': ', '{:%}'.format(float(prediction[0][i])))
