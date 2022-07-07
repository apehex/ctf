import numpy as np
from tensorflow.keras.models import load_model

class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

class SigmaNet:
    def __init__(self):
        self.name = 'sigmanet'
        self.model_filename = 'sigmanet.h5'
        try:
            self._model = load_model(self.model_filename)
            print('Successfully loaded', self.name)
        except (ImportError, ValueError, OSError):
            print('Failed to load', self.name)

    def color_process(self, imgs):
        if imgs.ndim < 4:
            imgs = np.array([imgs])
        imgs = imgs.astype('float32')
        mean = [125.307, 122.95, 113.865]
        std = [62.9932, 62.0887, 66.7048]
        for img in imgs:
            for i in range(3):
                img[:, :, i] = (img[:, :, i] - mean[i]) / std[i]
        return imgs

    def predict(self, img):
        processed = self.color_process(img)
        return self._model.predict(processed)

    def predict_one(self, img):
        confidence = self.predict(img)[0]
        predicted_class = np.argmax(confidence)
        return class_names[predicted_class]