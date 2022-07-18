> On a path to avenging his father, Tex Chance manufactured steam-powered robots to capture all the animals of your island to build a powerful army of fused mutated organisms using his powerful Sigma technology.
> You can't let them take away your loyal doggo Julius.
> The robots have been trained to classify all the objects they encounter using the SigmaNet network.
> Can you use your laser pointer to change some of the robot's vision pixels forcing it to misclassify your dog's image?

> Author: **[shazb0t][author-profile]**

## Adverserial machine learning

The neural network of the robots is given in `sigmanet.h5`. From this, we have to learn how to alter their vision / image input to misclassify Julius as anything else.

To fool the robots, we point lasers at 5 pixels on their cameras to modify their colors:

![][laser-coordinates]

Supposedly the decision boundaries of the model are sharp and switching a few pixels can change the decision from a class to another. This is called an "adversarial machine learning" attack.

The input image is 32 by 32:

![][julius.png]

The robot is 99.99% sure Juliues is a dog before the attack:

```python
SIGMA = tf.keras.models.load_model('sigmanet.h5')
julius = tf.image.decode_image(tf.io.read_file('../images/julius.png'), channels=3)
prediction = SIGMA(normalize(julius))

for i in range(len(CLASS_NAMES)):
    print(CLASS_NAMES[i], ': ', '{:%}'.format(float(prediction[0][i])))
# airplane :  0.000000%
# automobile :  0.000007%
# bird :  0.000003%
# cat :  0.001755%
# deer :  0.005456%
# dog :  99.986970%
# frog :  0.000631%
# horse :  0.005166%
# ship :  0.000000%
# truck :  0.000000%
```

Where the normalization scales the color channels to roughly `[-2; 2]`:

```python
def normalize(img):
    __layer = tf.keras.layers.Normalization(axis=-1, mean=MEAN_RGB, variance=STD_RGB**2)
    __image = __layer(img)
    return __image[None, ...]
```

## Adversarial FGSM

Tensorflow has a [great tutorial][tf-tuto] on a technique to fool NN into misclassifying a labrador. Looks like a perfect match!

It generates a perturbation on the original image based on the gradient of a [function that represents the distance from the original class][wiki-cross-entropy]:

```python
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
```

This technique generates pixels with maximum intensity everywhere, thanks to the use of the sign function `tf.sign(__gradient)`.

But we want to differentiate between the gradient values to find the highest slopes and select the corresponding pixels:

```python
def argmax(a, n):
    __a_flat = a.flatten()
    __i_flat = __a_flat.argsort()[-n:] # Find the indices in the 1D array
    __x, __y = np.unravel_index(__i_flat, a.shape) # convert the 1D indices back into coordinates

    return zip(__x, __y) # format as (x, y) tuples
```

```python
norm = tf.norm(perturbations[0], axis=-1).numpy() # as numpy array instead of tensor
most_significant_coordinates = list(argmax(norm, 5))
# [(20, 12), (14, 18), (14, 21), (15, 24), (16, 18)]
```

Aaaand it doesn't work!

```python
interpret(SIGMA(normalize(julius)))
# => predictions for the original image =============
# airplane :  0.000000%
# automobile :  0.000007%
# bird :  0.000003%
# cat :  0.001755%
# deer :  0.005456%
# dog :  99.986970%
# frog :  0.000631%
# horse :  0.005166%
# ship :  0.000000%
# truck :  0.000000%
interpret(SIGMA(normalize(julius) + delta))
# => predictions for the tampered image =============
# airplane :  0.000001%
# automobile :  0.000012%
# bird :  0.000005%
# cat :  0.002182%
# deer :  0.001433%
# dog :  99.979967%
# frog :  0.000273%
# horse :  0.016128%
# ship :  0.000000%
# truck :  0.000001%
```

May-be a single optimisation step is not enough, may-be the pixel values are not relevant?
Most likely the pixel selection is wrong!

## Sparse adversarial attack / "one pixel attack"

### General idea

Rather than generating a complete perturbation image and selecting the most significant pixels a-posteriori, I tried working on 5 pixels from the get-go.

There is a similar attack called the ["one pixel attack"][one-pixel-attack], where a population of images are "improved" step by step.
Each image has only one pixel differing from the original image. The improvements (worse classification from the NN) are made with a evolution algorithm over a set of images.

### "Improving"

What does it mean for an image to be better than the orginal shot of Julius?

The robots will capture any living creature, so we want the NN to classify the image as something inanimate: either an airplane, automobile, ship, or a truck.

In the end, it means that the confidence for **all** animals is lower than the confidence for **any** object.
And an image is better if we move in the direction: the total confidence for all animals lower and the confidence for one object rises.

This can be quantified as a function of the confidence vector returned by the NN:

This transfer in confidence from animal to object is coded as:

```python
def score(confidence: tf.Tensor) -> float:
    return float(
        max([confidence[0][__i] for __i in [0, 1, 8, 9]])
        - sum([confidence[0][__i] for __i in range(2, 8)]))
```

Where `confidence` is the output vector of probabilities given by the NN.

### Differential evolution

So the idea is to start from a random set of perturbations and make those perturbations more and more impactful.

A pertubation is a set of 5 pixels. Each pixel is itself represented by its coordinates and the RGB values:

```python
def random_pixel(width: int, height: int) -> list:
    return [
        random.randint(0, width - 1),
        random.randint(0, height - 1),
        int(random.gauss(128, 127)) % 256,
        int(random.gauss(128, 127)) % 256,
        int(random.gauss(128, 127)) % 256]
```

So that a candidate is a vector of length 25:

```python
def random_candidate(width: int, height: int, pixels: int=5) -> np.ndarray:
    return np.array(itertools.chain.from_iterable(
        [random_pixel(width, height) for _ in range(pixels)]))
```

And then the whole population of candidates is simply an array of N candidates:

```python
def random_population(size: int, width: int, height: int, pixels: int=5) -> np.array:
    return np.array([list(random_candidate(width, height, pixels)) for _ range(size)])
```

[author-profile]: https://app.hackthebox.com/users/32848
[julius]: images/julius.png
[laser-coordinates]: images/laser-coordinates.png
[one-pixel-attack]: https://github.com/Hyperparticle/one-pixel-attack-keras
[sparse-attacks]: https://github.com/fra31/sparse-imperceivable-attacks
[tf-tuto]: https://www.tensorflow.org/tutorials/generative/adversarial_fgsm
[wiki-cross-entropy]: https://en.wikipedia.org/wiki/Cross_entropy#Cross-entropy_loss_function_and_logistic_regression
