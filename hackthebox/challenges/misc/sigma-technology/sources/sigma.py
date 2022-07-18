import evolution as ev
import functools as ft
import matplotlib.pyplot as plt
import model as ml
import tensorflow as tf

############################################### setup for the specific use case

clip = ft.partial(ev.clip, width=32, height=32)
# fitness = ft.partial(ml.fitness, original=ml.JULIUS.numpy(), model=ml.SIGMA)
def fitness(perturbations): # somehow the partial evaluation of a Tensorflow function fails
	return ml.fitness(perturbations=perturbations, original=ml.JULIUS.numpy(), model=ml.SIGMA)

########################################################################## fgsm

index = tf.one_hot([ml.DOG_INDEX], len(ml.CLASS_NAMES))
perturbations = fgsm_pattern(normalize(JULIUS), index, SIGMA)
delta = tf.sparse.to_dense(fgsm_most(perturbations))

##################################################################### one pixel

population_0 = ev.random_population(128, 32, 32, 5)
population_64 = ev.evolve(population_0, 64, fitness, clip)

scores_0 = [fitness(__c) for __c in population_0]
scores_64 = [fitness(__c) for __c in population_64]

best_candidate_0 = population_0[scores_0.index(max(scores_0))]
best_candidate_64 = population_64[scores_64.index(max(scores_64))]

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
