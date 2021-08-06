from random import sample, random
import matplotlib.pyplot as plt
from arvore import Arvore
from time import time
from globais import *

class Populacao:
    def __init__(self):
        self.individuos = []

    def melhor_individuo(self):
        melhor = self.individuos[0]
        for ind in self.individuos:
            if ind.fitness > melhor.fitness:
                melhor = ind
        return melhor

    def pior_individuo(self):
        pior = self.individuos[0]
        for ind in self.individuos:
            if ind.fitness < pior.fitness:
                pior = ind
        return pior
    
    def media_individuos(self):
        soma = 0
        for ind in self.individuos:
            soma += ind.fitness
        return soma / len(self.individuos)

    def populacao_inicial(self):
        num_individuos = int((POPULACAO / (TAMANHO_ARVORE - 1)) / 2)
        for i in range(2, TAMANHO_ARVORE + 1):
            for j in range(num_individuos):
                full = Arvore()
                full.gera_full(i)
                full.fitness = full.calcula_fitness()
                self.individuos.append(full)

                grow = Arvore()
                grow.gera_grow(i)
                grow.fitness = grow.calcula_fitness()
                self.individuos.append(grow)

    def torneio(self):
        individuos_torneio = sample(self.individuos, TORNEIO)
        vencedor = individuos_torneio[0]
        for ind in individuos_torneio:
            if ind.fitness > vencedor.fitness:
                vencedor = ind
        return vencedor

    def nova_populacao(self):
        melhores, piores, mutacoes = 0, 0, 0
        if ELITISMO:
            elite = self.melhor_individuo()
            nova_pop = [elite]
        else:
            nova_pop = []
        while len(nova_pop) < POPULACAO:
            vencedor_1, vencedor_2 = self.torneio(), self.torneio()
            prop_mut_1, prop_mut_2, prop_cross = random(), random(), random()
            if PROP_MUTACAO >= prop_mut_1:
                filho_1 = vencedor_1.mutacao()
                filho_1.fitness = filho_1.calcula_fitness()
                nova_pop.append(filho_1)
                if (filho_1.fitness > vencedor_1.fitness):
                    mutacoes += 1
            if PROP_MUTACAO >= prop_mut_2:
                filho_2 = vencedor_2.mutacao()
                filho_2.fitness = filho_2.calcula_fitness()
                nova_pop.append(filho_2)
                if (filho_2.fitness > vencedor_2.fitness):
                    mutacoes += 1
            if PROP_CROSSOVER >= prop_cross:
                filho_1, filho_2 = vencedor_1.crossover(vencedor_2)
                filho_1.fitness = filho_1.calcula_fitness()
                filho_2.fitness = filho_2.calcula_fitness()
                media_pais = (vencedor_1.fitness + vencedor_2.fitness) / 2  
                nova_pop.append(filho_1)
                nova_pop.append(filho_2)                              
                if filho_1.fitness > media_pais:
                    melhores += 1
                elif filho_1.fitness < media_pais:
                    piores += 1
                if filho_2.fitness > media_pais:
                    melhores += 1
                elif filho_2.fitness < media_pais:
                    piores += 1
        self.individuos = nova_pop
        return melhores, piores, mutacoes

    def informacoes(self, gen, tempo, melhores=0, piores=0, mutacoes=0, mt=0, pt=0, mut=0):
        melhor = self.melhor_individuo()
        pior = self.pior_individuo()
        media = self.media_individuos()
        print(f"Geração {gen}:\nMelhor: {melhor.fitness}\nPior: {pior.fitness}")
        print(f"Media: {media}\nFilhos melhores que os pais: {melhores}")
        print(f"Filhos piores que os pais: {piores}\nMutacoes boas: {mutacoes}")
        print(f"Total filhos melhores que os pais: {mt}\nTotal filhos piores que os pais: {pt}")
        print(f"Total mutações melhores que os pais: {mut}")
        print(f"Tempo: {tempo:.2f} segundos\n")
    
    def plota_dados(self, y_melhores, y_piores, y_medias, x_geracoes):
        plt.plot(x_geracoes, y_melhores, "-b", label="melhor")
        plt.plot(x_geracoes, y_medias, "-g", label="media")
        plt.plot(x_geracoes, y_piores, "-r", label="pior")
        plt.xlabel("gerações")
        plt.ylabel("fitness")
        plt.legend()
        plt.show()

    def regressao_simbolica(self):
        y_melhores, y_piores, y_medias, x_geracoes = [], [], [], []
        for i in range(0, NUM_GERACOES + 1):
            x_geracoes.append(i)

        start = time()
        self.populacao_inicial()
        tempo = time() - start
        melhor = self.melhor_individuo()
        gen = 0
        melhores_t, piores_t, mutacoes_t = 0, 0, 0

        y_melhores.append(self.melhor_individuo().fitness)
        y_piores.append(self.pior_individuo().fitness)
        y_medias.append(self.media_individuos())
        
        self.informacoes(gen, tempo)

        while gen < NUM_GERACOES and melhor.fitness < 1:
            start = time()
            melhores, piores, mutacoes = self.nova_populacao()
            tempo = time() - start
            melhor = self.melhor_individuo()
            gen += 1
            melhores_t += melhores
            piores_t += piores
            mutacoes_t += mutacoes

            y_melhores.append(self.melhor_individuo().fitness)
            y_piores.append(self.pior_individuo().fitness)
            y_medias.append(self.media_individuos())

            self.informacoes(gen, tempo, melhores, piores, mutacoes, melhores_t, piores_t, mutacoes_t)
        
        self.plota_dados(y_melhores, y_piores, y_medias, x_geracoes)
        return melhor
