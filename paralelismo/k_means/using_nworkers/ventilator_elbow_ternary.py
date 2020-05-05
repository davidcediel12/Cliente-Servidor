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
        distance = abs(self.A*n_cluster + distorsion + self.C) / np.sqrt(self.A**2 + 1)
        self.distances.append(distance)
        return distance

    def ternarySearch(self, left, right, iters = 0):
        print("Iters", iters)
        if left == right:
            if self.n_clusters[left] not in self.analized_n_clusters:
                self.obtainDistorsion(self.n_clusters[left])

            return self.n_clusters[left] 

        if right - left == 1:
            
            #Analizando las distorsiones
            if self.n_clusters[left] not in self.analized_n_clusters:
                value_left = self.obtainDistorsion(self.n_clusters[left])
                value_left = self.obtainDistance(value_left, self.n_clusters[left])
            else:
                value_left = self.distances[self.analized_n_clusters.index(self.n_clusters[left])]

            

            if self.n_clusters[right] not in self.analized_n_clusters:
                value_right = self.obtainDistorsion(self.n_clusters[right])
                value_right = self.obtainDistance(value_right, self.n_clusters[right])
            else:
                value_right = self.distances[self.analized_n_clusters.index(self.n_clusters[right])]

            
            
            #Hallando el valor optimo de k 
            if value_left > value_right:
                return  self.n_clusters[left]
            else:
                return self.n_clusters[right] 

    
        
        m1 = left + (right-left)//3
        m2 = right - (right-left)//3

        if self.n_clusters[m1] not in self.analized_n_clusters:
            value_m1 = self.obtainDistorsion(self.n_clusters[m1])
            value_m1 = self.obtainDistance(value_m1, self.n_clusters[m1])
        else:
            value_m1 = self.distances[self.analized_n_clusters.index(self.n_clusters[m1])]

        if self.n_clusters[m2] not in self.analized_n_clusters:
            value_m2 = self.obtainDistorsion(self.n_clusters[m2])
            value_m2 = self.obtainDistance(value_m2, self.n_clusters[m2])
        else:
            value_m2 = self.distances[self.analized_n_clusters.index(self.n_clusters[m2])]
       

        # print(values[m1], values[m2])
        if value_m1 <= value_m2:
            return self.ternarySearch(m1+1, right, iters + 1)
        elif value_m1 > value_m2:
            return self.ternarySearch(left, m2 - 1, iters + 1)

    def obtainDistorsion(self, n_cluster):
        #Metodo k_means paralelizado.
        
        
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
        input("Press enter when workers elbow are ready")
        self.analized_n_clusters = []
        self.distorsions = []
        self.sendInitialData()

        self.obtainRect()
        self.optimum_k = self.ternarySearch(0, len(self.n_clusters))
        print("Clusters: \n", self.analized_n_clusters)
        print("Distorsions: \n", self.distorsions)
        print("Distances: \n", self.distances)
        print("OPTIMUM K:", self.optimum_k)
        self.showResult()



    def obtainRect(self):
        max_distorsion = self.obtainDistorsion(self.n_clusters[0])
        

        min_distorsion = self.obtainDistorsion(self.n_clusters[-1])
        
         
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