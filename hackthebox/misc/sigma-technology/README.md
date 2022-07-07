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

[author-profile]: https://app.hackthebox.com/users/32848
[julius]: images/julius.png
[laser-coordinates]: images/laser-coordinates.png
