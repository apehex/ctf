import itertools
import numpy as np
import tensorflow as tf

############################################################# adversarial noise

loss = tf.keras.losses.CategoricalCrossentropy()

def fgsm_pattern(image: tf.Tensor, index: int, model):
    with tf.GradientTape() as __tape:
        __tape.watch(image)
        __prediction = model(image)
        __loss = loss(index, __prediction)

    # Get the gradients of the loss w.r.t to the input image.
    return __tape.gradient(__loss, image)
    # Get the sign of the gradients to create the perturbation
    # return tf.sign(__gradient)

###############################################  most significant perturbations

def argmax(a, n):
    __a_flat = a.flatten()
    __i_flat = __a_flat.argsort()[-n:] # Find the indices in the 1D array
    __x, __y = np.unravel_index(__i_flat, a.shape) # convert the 1D indices back into coordinates

    return zip(__x, __y) # format as (x, y) tuples

def fgsm_most_significant(gradient, count=5):
    __gradient = unpack(gradient) # remove single value dimensions
    __norm = tf.norm(__gradient, axis=-1).numpy() # as numpy array instead of tensor
    __indices = list(itertools.chain.from_iterable([[(__i[0], __i[1], __j) for __j in range(3)] for __i in list(argmax(__norm, count))]))
    __values = [tf.sign(__gradient)[__i].numpy() for __i in __indices]
    return tf.sparse.reorder(
        tf.sparse.SparseTensor(indices=__indices, values=__values, dense_shape=__gradient.shape))
