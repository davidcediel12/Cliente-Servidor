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


class Worker:

    def readPartDataset(self, ini):
        chunk = self.chunk
        if ini + self.chunk > self.n_data:
            chunk = self.n_data - ini
        data = readSparseManual(join("datasets", self.name_dataset), ini, chunk)
        print("Data readed", len(data))
        tags = pd.read_csv(join("datasets", self.name_tags), 
                            skiprows=ini, nrows=self.chunk)
        tags = tags.values
        tags = tags.astype(int)
        return (data, tags)

    def recieveInitialData(self, msg):
        #Por ahora no se usa, ya que como no se cuantos workers tengo
        #no puedo enviar el data set al inicio
        self.name_dataset = msg["name_dataset"]
        self.chunk = msg["chunk"]
        self.n_data = msg["n_data"]
        self.distance_metric = msg["distance_metric"]
        self.has_tags  = msg["has_tags"]
        print("Recieved first message")
        

    def calculateDistances(self, points, tags):
        distorsion = 0

        norm_centroids = [np.linalg.norm(centroid) for centroid in self.centroids]
        #Solo lo codifique para angular porque por ahora no hay datasets sparse 
        #que trabajen con euclidean
        for (p, tag) in zip(points, tags):
            tag = int(tag)
            if self.distance_metric =="angular":
                distorsion += cosineSimilaritySparseManual2(p, self.centroids[tag], 
                                        norm_centroids[tag])**2
            elif self.distance_metric == "euclidean":
                distorsion += euclideanDistanceSparseManual2(p, self.centroids[tag])**2

        return distorsion
    
    
    def listen(self): 
        print("Ready")
        while True:
            msg = self.from_ventilator.recv_json()
            if msg["action"] == "new_dataset":
                    self.recieveInitialData(msg)
                    
            elif msg["action"] == "distance":
                self.centroids = np.asarray(msg["centroids"])
                self.n_clusters  = int(msg["n_clusters"])
                if("/" in self.name_dataset):
                    split_name_dataset = self.name_dataset.split("/") 
                    self.name_tags = join("/".join(split_name_dataset[0:-1]), "results", 
                                        split_name_dataset[-1].split(".")[0] + 
                                        f"_result{self.n_clusters}c.csv")
                else:
                    self.name_tags = join("results", self.name_dataset.split(".")[0] + 
                                        f"_result{self.n_clusters}c.csv")
                ini = msg["position"]
                print("Calculating distorsion")
                points, tags = self.readPartDataset(ini)
                distorsion = self.calculateDistances(points, tags)
                self.to_sink.send_string(str(distorsion))


    def createSockets(self):
        self.context = zmq.Context()

        self.from_ventilator = self.context.socket(zmq.PULL)
        self.from_ventilator.connect(f"tcp://{self.dir_ventilator}")

        self.to_sink = self.context.socket(zmq.PUSH)
        self.to_sink.connect(f"tcp://{self.dir_sink}")

    def __init__(self, dir_ventilator, dir_sink):
        self.dir_ventilator = dir_ventilator
        self.dir_sink = dir_sink
        self.createSockets()


if __name__ == "__main__":
    console = argparse.ArgumentParser()
    console.add_argument("dir_ventilator", type = str)
    console.add_argument("dir_sink", type = str)
    args = console.parse_args()

    worker = Worker(args.dir_ventilator, args.dir_sink)
    worker.listen()