"""
    Para esta implementacion, cada worker:
    1.Calcula la distancia del los que le llegaron puntos a 
      todos los centroides
    2.Con esta distancia saca el vector de tags y los clusters para
    el numero determinado de puntos 
"""
import zmq
import argparse 
from scipy.spatial import distance
import numpy as np
from sklearn.datasets import make_blobs
import pandas as pd
from os.path import join 
from utils import *
from GenericWorker import DenseWorkerGeneric

class Worker(DenseWorkerGeneric):

    def readPartDataset(self, ini):
        data = pd.read_csv(join("datasets", self.name_dataset), 
                            skiprows=ini, nrows=self.chunk)
        tags = pd.read_csv(join("datasets", "results", self.name_tags), 
                            skiprows=ini, nrows=self.chunk)
                                              
        if self.has_tags:
            values = data.values[:, :-1]
        else:
            values = data.values     
        values = values.astype(float)  

        tags = tags.values
        tags = tags.astype(int)
        return (values, tags)

    
        

    def calculateDistances(self, points, tags, norm_centroids):
        distorsion = 0
        for (p, tag) in zip(points, tags):
            tag = int(tag)
            if self.distance_metric == "euclidean":
                distorsion += distance.euclidean(p, self.centroids[tag])**2
            elif self.distance_metric == "angular":
                distorsion += cosineSimilarity(p, self.centroids[tag], norm_centroids[tag])**2
        return distorsion
    

    def listen(self): 
        print("Ready")
        while True:
            msg = self.from_ventilator.recv_json()
            if msg["action"] == "new_dataset":
                    self.recieveInitialData(msg)
                    
            elif msg["action"] == "distance":
                self.centroids, norm_centroids = self.readCentroids()
                self.n_clusters  = int(msg["n_clusters"])
                self.name_tags = (self.name_dataset.split(".")[0] + 
                            f"_result{self.n_clusters}c.csv")
                ini = msg["position"]
                print("Calculating distorsion")
                points, tags = self.readPartDataset(ini)
                distorsion = self.calculateDistances(points, tags, norm_centroids)
                self.to_sink.send_string(str(distorsion))

if __name__ == "__main__":
    console = argparse.ArgumentParser()
    console.add_argument("dir_ventilator", type = str)
    console.add_argument("dir_sink", type = str)
    args = console.parse_args()

    worker = Worker(args.dir_ventilator, args.dir_sink)
    worker.listen()