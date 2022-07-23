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

JULIUS = tf.image.decode_image(tf.io.read_file('../images/julius.png'), channels=3).numpy()

############################################################## image processing

MEAN_RGB = np.array([125.307, 122.95, 113.865])
STD_RGB = np.array([62.9932, 62.0887, 66.7048])

def unpack(x):
    return x[0] if x.shape[0] == 1 else x

def normalize(img: np.ndarray, mean: np.ndarray=MEAN_RGB, deviation: np.ndarray=STD_RGB):
    __layer = tf.keras.layers.Normalization(axis=-1, mean=mean, variance=deviation**2)
    return __layer(img).numpy()

def denormalize(x, mean=MEAN_RGB, deviation=STD_RGB):
    __mean = tf.broadcast_to(tf.convert_to_tensor(mean, dtype=tf.float32), x.shape)
    __deviation = tf.broadcast_to(tf.convert_to_tensor(deviation, dtype=tf.float32), x.shape)
    return tf.math.round(tf.math.multiply(unpack(x), __deviation) + __mean).astype(int)

########################################################## tensor manipulations

def pixels(perturbations: np.ndarray) -> np.ndarray:
    return np.multiply(
        perturbations,
        np.array([32, 32, 256, 256, 256])).astype(int)

def _tamper(original: np.ndarray, noise: np.ndarray) -> np.ndarray: # individual version
    __candidate = np.copy(original)
    for __pixel in noise:
        for __j in range(3):
            __candidate[__pixel[0], __pixel[1], __j] = __pixel[2 + __j]
    return __candidate.astype(int)

def tamper(original: np.ndarray, perturbations: np.ndarray) -> np.ndarray: # batch version
    __candidates = np.zeros(shape=(perturbations.shape[0], *original.shape), dtype=int)
    for __i in range(perturbations.shape[0]):
        __candidates[__i] = _tamper(original=original, noise=perturbations[__i])
    return __candidates

#################################################################### evaluation

def score(confidence: np.ndarray) -> np.ndarray:
    return (
        confidence.take(indices=[0], axis=-1).max(axis=-1) # misclassify as an airplane
        - confidence.take(indices=list(range(2, 8)), axis=-1).sum(axis=-1))

def fitness(perturbations: np.ndarray, original: np.ndarray, model=SIGMA) -> float:
    return score(
        confidence=model.predict_on_batch(
            normalize(tamper(
                original=original,
                perturbations=pixels(perturbations)))))

####################################################################### display

def interpret(predictions):
    __p = unpack(predictions)
    for i in range(__p.shape[-1]):
        print(CLASS_NAMES[i], ': ', '{:%}'.format(float(__p[i])))
