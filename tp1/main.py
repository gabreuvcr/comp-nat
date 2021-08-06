from populacao import Populacao
from time import time

pop = Populacao()
start = time()
melhor_ind = pop.regressao_simbolica()
print(f"Tempo total: {time() - start}")
fitness_teste = melhor_ind.calcula_fitness_teste()
print(f"Fitness do teste: {fitness_teste}")
