from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from random import choice
import pandas as pd

POPULACAO = 12
NUM_GERACOES = 10

TORNEIO = 5
PROP_CROSSOVER = 0.9
PROP_MUTACAO = 0.05
ELITISMO = True

TAMANHO_ARVORE = 7
TERMINAL = 0
FUNCAO = 1
FUNCOES = ['+', '-', '*', '/']
TERMINAIS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

def terminal_aleatorio(terminal_atual=''):
    while True:
        terminal = choice(TERMINAIS)
        if (terminal_atual != terminal):
            break
    return terminal

def funcao_aleatoria(funcao_atual=''):
    while True:
        funcao = choice(FUNCOES)
        if (funcao_atual != funcao):
            break
    return funcao

# arquivo, K = 'files/glass', 7
arquivo, K = 'files/breast_cancer', 2

df_train = pd.read_csv(f'{arquivo}_train.csv')
X_train = df_train.drop(df_train.columns[-1], axis = 1)
initial_centers_train = kmeans_plusplus_initializer(X_train, K).initialize()

df_test = pd.read_csv(f'{arquivo}_test.csv')
X_test = df_test.drop(df_test.columns[-1], axis = 1)
initial_centers_test = kmeans_plusplus_initializer(X_test, K).initialize()
