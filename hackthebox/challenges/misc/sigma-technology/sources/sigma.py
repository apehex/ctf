import evolution as ev
# import fgsm
import matplotlib.pyplot as plt
import model as ml
import numpy as np
import tensorflow as tf

############################################### setup for the specific use case

def fitness(perturbations): # somehow the partial evaluation of a Tensorflow function fails
	return ml.fitness(perturbations=perturbations, original=ml.JULIUS, model=ml.SIGMA)

########################################################################## fgsm

# index = tf.one_hot([ml.DOG_INDEX], len(ml.CLASS_NAMES))
# perturbations = fgsm.fgsm_pattern(ml.normalize(ml.JULIUS), index, ml.SIGMA)
# delta = tf.sparse.to_dense(fgsm.fgsm_most_significant(perturbations))

##################################################################### one pixel

population_i = ev.random_population(size=1024, pixels=5)
population_f = ev.evolve(population=population_i, generations=256, fitness=fitness)

scores_i = fitness(population_i)
scores_f = fitness(population_f)

best_candidates_i = population_i.take(indices=np.argsort(scores_i)[-16:], axis=0)
best_candidates_f = population_f.take(indices=np.argsort(scores_f)[-16:], axis=0)

best_images_i = ml.tamper(original=ml.JULIUS, perturbations=best_candidate_i)
best_images_f = ml.tamper(original=ml.JULIUS, perturbations=best_candidate_f)

####################################################################### display

# plt.figure()
# plt.imshow(JULIUS)
# plt.imshow(perturbations[0])
# # plt.imshow(perturbations[0] * 0.5 + 0.5)  # To change [-1, 1] to [0,1]
# plt.show()

# print("=> predictions for the original image =============")
# interpret(SIGMA(normalize(JULIUS)))
# print("=> predictions for the tampered image =============")
# interpret(SIGMA(normalize(JULIUS) + delta))
