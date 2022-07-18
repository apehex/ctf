import evolution as ev
import functools
import model as ml

############################################### setup for the specific use case

clip = functools.partial(ev.clip, width=32, height=32)
# fitness = functools.partial(ml.fitness, original=ml.JULIUS.numpy(), model=ml.SIGMA)
def fitness(perturbations): # somehow the partial evaluation of a Tensorflow function fails
	return ml.fitness(perturbations=perturbations, original=ml.JULIUS.numpy(), model=ml.SIGMA)
def fitness(perturbations):
	return ml.score(
        confidence=ml.SIGMA(ml.normalize(ml.tamper(original=ml.JULIUS.numpy(), perturbations=perturbations))))

########################################################################## fgsm

##################################################################### one pixel

population_0 = ev.random_population(128, 32, 32, 5)
population_32 = ev.evolve(population_0, 32, fitness, clip)

scores_0 = [fitness(__c) for __c in population_0]
scores_32 = [fitness(__c) for __c in population_32]

best_candidate_0 = population_0[scores_0.index(max(scores_0))]
best_candidate_32 = population_32[scores_32.index(max(scores_32))]
