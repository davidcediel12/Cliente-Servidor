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
            "iters" : (self.n_clusters_max - self.n_clusters_min) + 1,
            "opers" : opers
        })
    

    
    def showResult(self, distorsions):
        plt.plot(self.n_clusters, distorsions)
        plt.vlines(self.optimum_k, distorsions[0], distorsions[-1], linestyles = "dashed")
        plt.show()
        name_fig = self.name_dataset.split(".")[0] + "_elbow.png"
        plt.savefig(f"results_elbow/{name_fig}")


    def obtainDistancesPointRect(self, distorsions):
        # y2-y1/x2-x1
        m = (distorsions[-1] - distorsions[0])/(self.n_clusters[-1] - self.n_clusters[0])

        A = -1*m
        B = 1
        C = m*self.n_clusters[0] - distorsions[0]
        
        distances = []
        for (x, y) in zip(self.n_clusters, distorsions):
            distances.append(abs(A*x + B*y + C) / np.sqrt(A**2 + B**2))
        
        print("Distances\n", distances)
        return distances

    def ternarySearch(self, left, right, values, iters = 0):
        print("Iters", iters)
        if left == right:
            return self.n_clusters[left]

        if right - left == 1:
            if values[left] > values[right]:
                return self.n_clusters[left]
            else:
                return self.n_clusters[right] 

        m1 = left + (right-left)//3
        m2 = right - (right-left)//3
        # print(values[m1], values[m2])
        if values[m1] <= values[m2]:
            return self.ternarySearch(m1+1, right, values, iters + 1)
        elif values[m1] > values[m2]:
            return self.ternarySearch(left, m2 - 1, values, iters + 1)

    def elbowMethod(self):
        #Metodo k_means paralelizado.
        input("Press enter when workers elbow are ready")
        
        distorsions = []
        self.n_clusters = [i for i in range(self.n_clusters_min, self.n_clusters_max +1)]
        self.sendInitialData()
        for n_cluster in self.n_clusters:
            ventilator = Ventilator(self.name_dataset, self.has_tags, 
                                    "127.0.0.1:5555", "127.0.0.1:5556", 
                                    "127.0.0.1:5557", self.n_data, self.n_features, 
                                    n_cluster, self.distance_metric)
            ventilator.kmeans()
            centroids = ventilator.centroids    
            
            i = 0
            while i < self.n_data:
                self.to_workers.send_json({
                    "action" : "distance",
                    "n_clusters" : len(centroids),
                    "centroids" : centroids,
                    "type_distance" : self.distance_metric,
                    "position" : i
                })
                i += self.chunk_worker

            
            distorsions.append(float(self.from_sink.recv_string()))
            print("Distorsion recieved")
            self.from_sink.send(b" ")

        
        #self.obtainOptimumK(distorsions)
        self.optimum_k = self.ternarySearch(0, len(distorsions), self.obtainDistancesPointRect(distorsions))

        #Mostrando resultados
        self.showResult(distorsions)
    
    def __init__(self, name_dataset, has_tags, my_dir, 
                    my_dir_sink, dir_sink, n_data, 
                    n_features, n_clusters_min, 
                    n_clusters_max, distance_metric):

        self.name_dataset = name_dataset
        self.distance_metric = distance_metric
        self.n_data = n_data 
        self.n_features = n_features
        self.n_clusters_min = n_clusters_min
        self.n_clusters_max = n_clusters_max
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