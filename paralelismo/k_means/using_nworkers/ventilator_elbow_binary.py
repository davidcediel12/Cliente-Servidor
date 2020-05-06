from sklearn.datasets import make_blobs
import numpy as np
import zmq
import matplotlib.pyplot as plt
import argparse
import time
import pandas as pd 
from os.path import join
import csv 
from ventilator import Ventilator


"""
A diferencia del ventilator elbow normal, este no realiza todas las iteraciones
en el rango dado, sino que hace una busqueda ternaria para asi ahorrar iteraciones 
"""
class VentilatorElbow:
    max_iters = 1000
    chunk_worker = 100
    tolerance = 0.01

    def createSockets(self):
        self.context = zmq.Context()

        self.to_workers = self.context.socket(zmq.PUSH)
        self.to_workers.bind(f"tcp://{self.my_dir}")

        self.to_sink = self.context.socket(zmq.PUSH)
        self.to_sink.connect(f"tcp://{self.dir_sink}")

        self.from_sink = self.context.socket(zmq.REP)
        self.from_sink.bind(f"tcp://{self.my_dir_sink}")

    
    def sendInitialData(self):
        i = 0 
        #Para no enviarle el dataset en cada iteracion, se le envia el nombre
        #que ellos deben abrir 
        while i < self.n_data:
            self.to_workers.send_json({
                "action" : "new_dataset",
                "name_dataset" : self.name_dataset,
                "has_tags" : self.has_tags,
                "chunk" : self.chunk_worker,
                "distance_metric" : self.distance_metric,
            })
            i += self.chunk_worker

        #Calculando el numero de operaciones que se haran
        #para decirle al sink lo que debe esperar
        opers = self.n_data // self.chunk_worker
        if self.n_data % self.chunk_worker != 0:
            opers += 1

        self.to_sink.send_json({
            "iters" : len(self.n_clusters),
            "opers" : opers
        })
        
    def showResult(self):
        plt.scatter(self.analized_n_clusters, self.distances)
        plt.show()
        plt.scatter(self.analized_n_clusters, self.distorsions)
        plt.vlines(self.optimum_k, np.min(self.distorsions), 
                    np.max(self.distorsions), linestyles = "dashed")
        plt.show()
        name_fig = self.name_dataset.split(".")[0] + "_elbow.png"
        plt.savefig(f"results_elbow/{name_fig}")


    def obtainDistance(self, distorsion, n_cluster):
        #Retorna la distancia de un punto (n_cluster, distorsion) a 
        # la recta inicial (k_ini, distorsion):(k_fin, distorsion) 
        distance = abs(self.A*n_cluster + distorsion + self.C) / np.sqrt(self.A**2 + 1)
        self.distances.append(distance)
        return distance

    def obtainPendiente(self, p1, p2):
        # y2-y1 / x2-x1
        #print(p1, p2)
        return abs((p2[1] - p1[1]) / (p2[0] - p1[0]))

    def binarySearch(self, number, distorsion, distance_rect):

        #Hallo las dos pendientes para ver que intervalo analizo primero 
        pendiente_ini = self.obtainPendiente((number, distorsion), self.init_point)
        pendiente_fin = self.obtainPendiente((number, distorsion), self.end_point)


        left = number - (number//2)
        right = number + (number//2)
        
        if left in self.analized_n_clusters and right in self.analized_n_clusters:
            #Ya analice todas las particiones y no tengo para donde moverme
            return number 


        # Elijo que lado voy a explorar primero, con base en las pendientes
        # halladas, me voy por el lado que tenga mas pendiente 
        if pendiente_ini >= pendiente_fin:
            priority_queue = [left, right]
        else:
            priority_queue = [right, left]

        
        #Analizo la primera parte del intervalo, si la distancia a la recta 
        # inicial resulta ser mayor, me voy por ahi, si no, recurro al otro 
        # lado 

        # Si no he hecho k_means para este numero lo hago, si ya lo hice 
        # lo busco en el atributo de la clase 
        if priority_queue[0] not in self.analized_n_clusters:
            distorsion1 = self.obtainDistorsion(priority_queue[0])
        else:
            distorsion1 = self.distorsions[self.analized_n_clusters.index(priority_queue[0])]
        
        
        distance1 = self.obtainDistance(distorsion1, priority_queue[0])

        if distance1 >= distance_rect:
            return self.binarySearch(priority_queue[0], distorsion1, distance1)


        #En caso de que la distancia del primer intervalo sea menor, analizo el 
        #segundo intervalo, si es mayor, nunca se ejecutara esta parte del codigo
        if priority_queue[1] not in self.analized_n_clusters:
            distorsion2 = self.obtainDistorsion(priority_queue[1])
        else:
            distorsion2 = self.distorsions[self.analized_n_clusters.index(priority_queue[1])]
        
        distance2 = self.obtainDistance(distorsion2, priority_queue[1])

        if distance2 >= distance_rect:
            return self.binarySearch(priority_queue[1], distorsion2, distance2)


        #Si llega hasta aqui es porque la distancia a la recta de ambos intervalos 
        # es menor, por lo que la solucion es peor, entonces puedo concluir que el 
        # k optimo es el numero que le llego         
        return number 



    def obtainDistorsion(self, n_cluster):
        #Metodo k_means paralelizado.
        print(f"K_means for {n_cluster} clusters")
        
        ventilator = Ventilator(self.name_dataset, self.has_tags, 
                                "127.0.0.1:5555", "127.0.0.1:5556", 
                                "127.0.0.1:5557", self.n_data, self.n_features, 
                                n_cluster, self.distance_metric)
        ventilator.kmeans()
        centroids = ventilator.centroids
        n_data = ventilator.n_data

        i = 0
        while i < n_data:
            self.to_workers.send_json({
                "action" : "distance",
                "n_clusters" : len(centroids),
                "centroids" : centroids,
                "type_distance" : self.distance_metric,
                "position" : i
            })
            i += self.chunk_worker

        
        distorsion = float(self.from_sink.recv_string())
        print("Distorsion recieved")
        self.from_sink.send(b" ")
        self.analized_n_clusters.append(n_cluster)
        self.distorsions.append(distorsion)
        return distorsion

    
    def elbowMethod(self):
        #Obtiene la distorsion para el k_min y el k_max, luego llama 
        #a binary search para realizar la busqueda
        input("Press enter when workers elbow are ready")
        self.analized_n_clusters = []
        self.distorsions = []
        self.sendInitialData()

        self.obtainRect()
        
        #Hago el k means para la mitad de los datos, como es el primero, siempre
        # se analiza. 
        partition = (self.n_clusters[0] + self.n_clusters[-1]) // 2
        distorsion_ini = self.obtainDistorsion(partition)
        distance_ini = self.obtainDistance(distorsion_ini, partition)

        #Busco el k optimo mediante busqueda binaria
        self.optimum_k = self.binarySearch(partition, distorsion_ini, distance_ini)


        print("Clusters: \n", self.analized_n_clusters)
        print("Distorsions: \n", self.distorsions)
        print("Distances: \n", self.distances)
        print("OPTIMUM K:", self.optimum_k)
        self.showResult()



    def obtainRect(self):
        #Obtiene la recta inicial del menor numero de k al mayor numero de k
        max_distorsion = self.obtainDistorsion(self.n_clusters[0])
        self.init_point = (self.n_clusters[0], max_distorsion)

        min_distorsion = self.obtainDistorsion(self.n_clusters[-1])
        self.end_point = (self.n_clusters[-1], min_distorsion)
         
        # -m 
        self.A = -1 * (min_distorsion - max_distorsion)/(self.n_clusters[-1] - self.n_clusters[0])
        # m*x1 - y1
        self.C = (self.A * -1 *self.n_clusters[0]) - max_distorsion

        self.obtainDistance(max_distorsion, self.n_clusters[0])
        self.obtainDistance(min_distorsion, self.n_clusters[-1])
    

    def __init__(self, name_dataset, has_tags, my_dir, 
                    my_dir_sink, dir_sink, n_data, 
                    n_features, n_clusters_min, 
                    n_clusters_max, distance_metric):

        self.name_dataset = name_dataset
        self.distance_metric = distance_metric
        self.n_data = n_data 
        self.n_features = n_features
        self.n_clusters =  [i for i in range(n_clusters_min, n_clusters_max+1)]
        self.distances = []
        self.has_tags = has_tags
        


        self.my_dir = my_dir
        self.my_dir_sink = my_dir_sink
        self.dir_sink = dir_sink
        self.createSockets()



def createConsole():
    console = argparse.ArgumentParser()
    console.add_argument("my_dir", type=str)
    console.add_argument("my_dir2", type=str)
    console.add_argument("dir_sink", type=str)
    console.add_argument("name_file", type=str)
    console.add_argument("n_data", type=int)
    console.add_argument("n_features", type=int)
    console.add_argument("n_clusters_min", type=int)
    console.add_argument("n_clusters_max", type=int)
    console.add_argument("distance_metric", type=str)
    console.add_argument("-t", "--tags", action="store_true")
    return console.parse_args()

if __name__ == "__main__":
    args = createConsole()
    ventilator_elbow = VentilatorElbow(args.name_file, args.tags,
                            args.my_dir, args.my_dir2, args.dir_sink, 
                            args.n_data, args.n_features,
                            args.n_clusters_min, args.n_clusters_max, 
                            args.distance_metric)
    ventilator_elbow.elbowMethod()