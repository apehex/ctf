> On a path to avenging his father, Tex Chance manufactured steam-powered robots to capture all the animals of your island to build a powerful army of fused mutated organisms using his powerful Sigma technology.
> You can't let them take away your loyal doggo Julius.
> The robots have been trained to classify all the objects they encounter using the SigmaNet network.
> Can you use your laser pointer to change some of the robot's vision pixels forcing it to misclassify your dog's image?

> Author: **[shazb0t][author-profile]**

## Adverserial machine learning

The neural network of the robots is given in `sigmanet.h5`. From this, we have to learn how to alter their vision / image input to misclassify Julius as anything else.

To fool the robots, we point lasers at 5 pixels on their cameras to modify their colors:

![][laser-coordinates]

Supposedly the decision boundaries of the model are sharp and switching single pixels can change the decision from a class to another. This is called an "adversarial machine learning" attack.

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

But we want to differentiate between the gradient values to find the highest and select the corresponding pixels:

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
SIGMA(normalize(julius))
SIGMA(normalize(julius) + 0.2 * perturbations)
```

## Sparse adversarial attack / "one pixel attack"

Rather than generating a complete image and selecting the most significant pixels a-posteriori, I tried working on 5 pixels from the get-go.

[author-profile]: https://app.hackthebox.com/users/32848
[julius]: images/julius.png
[laser-coordinates]: images/laser-coordinates.png
[sparse-attacks]: https://github.com/fra31/sparse-imperceivable-attacks
[tf-tuto]: https://www.tensorflow.org/tutorials/generative/adversarial_fgsm
[wiki-cross-entropy]: https://en.wikipedia.org/wiki/Cross_entropy#Cross-entropy_loss_function_and_logistic_regression
