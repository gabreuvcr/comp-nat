import matplotlib.pyplot as plt
import random
import math
import copy

INICIO, FINAL = ('i',), ('f',)

class Formiga:
    def __init__(self, makespan=0):
        self.caminho = []
        self.makespan = makespan

class Colonia:
    def __init__(self, maquinas, tempos, qtd_trab, qtd_maq):
        self.maquinas = maquinas
        self.tempos = tempos
        self.qtd_trab = qtd_trab
        self.qtd_maq = qtd_maq
        qtd_ops = qtd_trab * qtd_maq
        self.formigas = [Formiga() for _ in range(QTD_FORMIGAS)]
        self.custos = [tempos[i // qtd_maq][i % qtd_maq] for i in range(qtd_ops)]
        self.vertices = [(i // self.qtd_maq, i % self.qtd_maq) for i in range(qtd_ops)]
        self.feromonio = [[-1 if i == j else FER_INICIAL for j in range(qtd_ops)] for i in range(qtd_ops + 1)]
        self.grafo = self.cria_grafo()
        self.desirability = self.calcula_desirability()
        self.execucao()
        
    def calcula_desirability(self):
        desirability = []
        for vertice in self.vertices:
            trab, i_maq = vertice
            tempo_finalizar = 0
            while i_maq < self.qtd_maq:
                tempo_finalizar += self.tempos[trab][i_maq]
                i_maq += 1
            desirability.append(tempo_finalizar)
        return desirability

    def cria_grafo(self):
        grafo = {}
        grafo[INICIO], grafo[FINAL]= [], []
        for i in range(self.qtd_trab):
            grafo[INICIO] += [(i, self.maquinas[i][0])]

        for i_vertice in self.vertices:
            trab, maq = i_vertice
            i_maq = self.maquinas[trab].index(maq)
            if i_maq + 1 < self.qtd_maq:
                prox_maq = self.maquinas[trab][i_maq + 1]
                grafo[i_vertice] = [(trab, prox_maq)]
            else:
                grafo[i_vertice] = [FINAL]
            for j_vertice in self.vertices:
                trab_j, maq_j = j_vertice
                if maq == maq_j and i_vertice != j_vertice:
                    grafo[i_vertice] += [(trab_j, maq_j, 'bd')]
        return grafo
    
    def grafo_direcionado(self, caminho):
        grafo_di = copy.deepcopy(self.grafo)
        for vertice in grafo_di:
            copia_adjacentes = grafo_di[vertice][:]
            for adjacente in copia_adjacentes:
                if len(adjacente) == 3:
                    adjacente_di = (adjacente[0], adjacente[1])
                    i_vertice, i_adjacente = caminho.index(vertice), caminho.index(adjacente_di)
                    if i_vertice < i_adjacente:
                        grafo_di[vertice].remove(adjacente)
                        grafo_di[vertice].append(adjacente_di)
                        grafo_di[adjacente_di].remove((vertice[0], vertice[1], 'bd'))
                    else:
                        grafo_di[adjacente_di].remove((vertice[0], vertice[1], 'bd'))
                        grafo_di[adjacente_di].append(vertice)
                        grafo_di[vertice].remove(adjacente)
        return grafo_di
    
    def index(self, trab_maq):
        if trab_maq == INICIO:
            return len(self.feromonio) - 1
        trab, maq = trab_maq
        return trab * self.qtd_maq + self.maquinas[trab].index(maq)
        
    def custo(self, adjacente):
        if adjacente == FINAL:
            return 0
        return self.custos[self.index(adjacente)]

    def calcula_makespan(self, caminho):
        grafo_di = self.grafo_direcionado(caminho)
        tempo = {vertice: -1 for vertice in caminho}
        tempo[INICIO] = tempo[FINAL] = 0
        
        for adjacente in grafo_di[INICIO]:
            tempo[adjacente] = self.custos[self.index(adjacente)]
        for vertice in caminho:
            for adjacente in grafo_di[vertice]:
                custo = self.custo(adjacente)
                if tempo[adjacente] < tempo[vertice] + custo:
                    tempo[adjacente] = tempo[vertice] + custo
        return tempo[FINAL]

    def calcula_probabilidade(self, atual, candidato):
        i_atual = self.index(atual)
        i_candidato = self.index(candidato)
        tij = self.feromonio[i_atual][i_candidato]
        nij = self.desirability[i_candidato]
        return (tij ** ALFA) * (nij ** BETA)

    def proximo(self, proximos, atual):
        somatorio_probs, probs = 0, []
        for i in range(len(proximos)):
            somatorio_probs += self.calcula_probabilidade(atual, proximos[i])
        for i in range(len(proximos)):
            probs.append(self.calcula_probabilidade(atual, proximos[i]) / somatorio_probs)

        escolhido = random.choices(proximos, weights=probs)
        trab, maq = escolhido[0]
        proximos.remove((trab, maq))
        i_maq = self.maquinas[trab].index(maq)
        if i_maq + 1 < self.qtd_maq:
            prox_maq = self.maquinas[trab][i_maq + 1]
            proximos.append((trab, prox_maq))
        return (trab, maq)

    def caminha_formiga(self, formiga):
        proximos = [(trab, self.maquinas[trab][0]) for trab in range(self.qtd_trab)]
        atual = INICIO
        while proximos:
            atual = self.proximo(proximos, atual)
            trab, maq = atual
            formiga.caminho.append((trab, maq))
        formiga.makespan = self.calcula_makespan(formiga.caminho)

    def reseta_formigas(self):
        for formiga in self.formigas:
            formiga.caminho = []
    
    def atualiza_feromonios(self, formiga):
        for i in range(len(self.feromonio)):
            for j in range(len(self.feromonio[i])):
                if self.feromonio[i][j] == -1:
                    continue
                self.feromonio[i][j] *=  1 - TX_EVA

        qtd_feromonio = 1 / formiga.makespan
        for i in range(len(formiga.caminho) - 1):
            i_atual = self.index(formiga.caminho[i])
            i_prox = self.index(formiga.caminho[i + 1])
            self.feromonio[i_atual][i_prox] += qtd_feromonio
        inicio = self.index(INICIO)
        primeiro = self.index(formiga.caminho[0])
        self.feromonio[inicio][primeiro] += qtd_feromonio
        self.reseta_formigas()

    def execucao(self):
        melhor_formiga = Formiga(math.inf)
        y_melhores_makespans = []
        y_medias_makespans = []
        x_iteracoes = [i for i in range(ITERACOES)]
        for _ in range(ITERACOES):
            makespans = []
            for formiga in self.formigas:
                self.caminha_formiga(formiga)
                if formiga.makespan < melhor_formiga.makespan:
                    melhor_formiga.makespan = formiga.makespan
                    melhor_formiga.caminho = formiga.caminho[:]
                makespans.append(formiga.makespan)

            y_medias_makespans.append(sum(makespans)/len(makespans))
            y_melhores_makespans.append(melhor_formiga.makespan)

            self.atualiza_feromonios(melhor_formiga)

        print(f"\nMelhor makespan: {melhor_formiga.makespan}")
        plt.plot(x_iteracoes, y_melhores_makespans, "-b", label="melhor")
        plt.plot(x_iteracoes, y_medias_makespans, "-g", label="media")
        plt.xlabel("iteracoes")
        plt.ylabel("makespan")
        plt.title("la40")
        plt.legend()
        plt.show()


def arquivo_entrada(nome_arquivo):
    try:
        with open(nome_arquivo) as arquivo:
            maquinas, tempos = [], []
            linha = ""
            while not linha or not linha[0].isnumeric():
                linha = arquivo.readline().strip()
            qtd_trab, qtd_maq = [int(num) for num in linha.split()]
            for i, linha in enumerate(arquivo):
                linha_split = [int(num) for num in linha.split()]
                maquinas.append([]), tempos.append([])
                for j in range(0, len(linha_split), 2):
                    maquinas[i] += [linha_split[j]]
                    tempos[i]   += [linha_split[j + 1]]
    except FileNotFoundError:
        print("arquivo nao encontrado")
        exit(1)
    return maquinas, tempos, qtd_trab, qtd_maq

# #ft06
# QTD_FORMIGAS = 100
# ITERACOES = 50
# FER_INICIAL = 0.1
# TX_EVA = 0.1
# ALFA = 1
# BETA = 2

#la01
QTD_FORMIGAS = 100
ITERACOES = 25
FER_INICIAL = 0.01
TX_EVA = 0.25
ALFA = 1
BETA = 5

maquinas, tempos, qtd_trab, qtd_maq = arquivo_entrada("files/la40.txt")
colonia = Colonia(maquinas, tempos, qtd_trab, qtd_maq)
