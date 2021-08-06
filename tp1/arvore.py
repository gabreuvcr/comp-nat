from pyclustering.utils.metric import distance_metric, type_metric
from sklearn.metrics.cluster import v_measure_score
from pyclustering.cluster.kmeans import kmeans
from random import randint
from copy import deepcopy
from globais import *

class No:
    def __init__(self, valor, pai=None):
        self.valor = valor
        self.pai = pai
        self.direita = None
        self.esquerda = None
        if (valor in FUNCOES):
            self.tipo = FUNCAO
        else:
            self.tipo = TERMINAL
    
    def profundidade_filhos(self):
        prof_esq = 0
        prof_dir = 0
        if (self.esquerda):
            prof_esq = self.esquerda.profundidade_filhos() + 1
        if (self.direita):
            prof_dir = self.direita.profundidade_filhos() + 1
        return max(prof_dir, prof_esq) 
    
    def nivel(self):
        atual = self
        nivel = 0
        while (atual.pai):
            nivel += 1
            atual = atual.pai
        return nivel
 
class Arvore:
    def __init__(self):
        self.raiz = No(funcao_aleatoria())
        self.fitness = 0

    def calcula_fitness(self):
        X_train_tmp = deepcopy(X_train)
        manhattan_metric = distance_metric(type_metric.USER_DEFINED, func=self.calcula)
        kmeans_instance = kmeans(X_train_tmp, initial_centers_train, metric=manhattan_metric)
        kmeans_instance.process()
        kmeans_clusters = kmeans_instance.get_clusters()
        for i in range(len(kmeans_clusters)):
            X_train_tmp.loc[kmeans_clusters[i], 'pred'] = df_train.iloc[kmeans_clusters[i]].groupby(df_train.columns[-1]).size().idxmax()
        return v_measure_score(df_train[df_train.columns[-1]], X_train_tmp['pred']) 

    def calcula_fitness_teste(self):
        X_test_tmp = deepcopy(X_test)
        manhattan_metric = distance_metric(type_metric.USER_DEFINED, func=self.calcula)
        kmeans_instance = kmeans(X_test_tmp, initial_centers_test, metric=manhattan_metric)
        kmeans_instance.process()
        kmeans_clusters = kmeans_instance.get_clusters()
        for i in range(len(kmeans_clusters)):
            X_test_tmp.loc[kmeans_clusters[i], 'pred'] = df_test.iloc[kmeans_clusters[i]].groupby(df_test.columns[-1]).size().idxmax()
        return v_measure_score(df_test[df_test.columns[-1]], X_test_tmp['pred'])

    def crossover(self, arvore_2):
        filho_1 = deepcopy(self)
        filho_2 = deepcopy(arvore_2)
        no_1, no_2 = None, None
        
        while True:
            no_1 = filho_1.no_aleatorio()
            no_2 = filho_2.no_aleatorio()
            if (filho_1.raiz == no_1 and filho_2.raiz == no_2):
                continue
            if ((no_1.profundidade_filhos() + no_2.nivel() <= TAMANHO_ARVORE) and
                (no_2.profundidade_filhos() + no_1.nivel() <= TAMANHO_ARVORE)):
                break

        if filho_1.raiz == no_1:
            filho_1.raiz = no_2
        elif no_1.pai.direita == no_1:
            no_1.pai.direita = no_2
        elif no_1.pai.esquerda == no_1:
            no_1.pai.esquerda = no_2
        
        if filho_2.raiz == no_2:
            filho_2.raiz = no_1
        elif no_2.pai.direita == no_2:
            no_2.pai.direita = no_1
        elif no_2.pai.esquerda == no_2:
            no_2.pai.esquerda = no_1
        
        no_1.pai, no_2.pai = no_2.pai, no_1.pai
        return filho_1, filho_2

    def mutacao(self):
        filho = deepcopy(self)
        no = filho.no_aleatorio()
        if (no.tipo == TERMINAL):
            no.valor = terminal_aleatorio(no.valor)
        elif (no.tipo == FUNCAO):
            no.valor = funcao_aleatoria(no.valor)
        return filho
    
    def _gera_full_rec(self, atual, tamanho_atual, tamanho_maximo):
        if (tamanho_atual == tamanho_maximo):
            atual.direita = No(terminal_aleatorio(), atual)
            atual.esquerda = No(terminal_aleatorio(), atual)
            return

        atual.direita = No(funcao_aleatoria(), atual)
        atual.esquerda = No(funcao_aleatoria(), atual)
        self._gera_full_rec(atual.direita, tamanho_atual + 1, tamanho_maximo)
        self._gera_full_rec(atual.esquerda, tamanho_atual + 1, tamanho_maximo)
        
    def gera_full(self, tamanho_maximo):
        raiz = self.raiz
        tamanho_atual = 0
        self._gera_full_rec(raiz, tamanho_atual + 1, tamanho_maximo)

    def _gera_grow_rec(self, atual, tamanho_atual, tamanho_maximo):
        if (tamanho_atual == tamanho_maximo):
            atual.direita = No(terminal_aleatorio(), atual)
            atual.esquerda = No(terminal_aleatorio(), atual)
            return
        
        atual.direita  = No(terminal_aleatorio(), atual)
        atual.esquerda = No(funcao_aleatoria(), atual)
        self._gera_grow_rec(atual.esquerda, tamanho_atual + 1, tamanho_maximo)

    def gera_grow(self, tamanho_maximo):
        raiz = self.raiz
        tamanho_atual = 0
        self._gera_grow_rec(raiz, tamanho_atual + 1, tamanho_maximo)

    def no_aleatorio(self):
        atual = self.raiz
        nivel = randint(0, atual.profundidade_filhos())
        while (nivel != 0):
            moeda = randint(0, 1)
            if moeda == 0 and atual.esquerda:
                atual = atual.esquerda
            elif moeda == 1 and atual.direita:
                atual = atual.direita
            elif atual.direita:
                atual = atual.direita
            elif atual.esquerda:
                atual = atual.esquerda
            else:
                break
            nivel -= 1
        return atual

    def _calcula_rec(self, atual, linhas):
        if atual.tipo == FUNCAO:
            valor_direita = self._calcula_rec(atual.direita, linhas)
            valor_esquerda = self._calcula_rec(atual.esquerda, linhas)
            if (atual.valor == '+'):
                return valor_esquerda + valor_direita
            elif (atual.valor == '-'):
                return valor_esquerda - valor_direita
            elif (atual.valor == '*'):
                return valor_esquerda * valor_direita
            elif (atual.valor == '/'):
                if (valor_direita == 0):
                    return valor_esquerda
                return valor_esquerda / valor_direita
        elif atual.tipo == TERMINAL:
            return linhas[atual.valor]

    def calcula(self, linha1, linha2):
        atual = self.raiz
        return abs(self._calcula_rec(atual, linha1.tolist() + linha2.tolist()))
  