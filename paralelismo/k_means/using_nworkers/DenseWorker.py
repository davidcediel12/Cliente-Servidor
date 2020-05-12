"""
    Para esta implementacion, cada worker:
    1.Calcula la distancia del los que le llegaron puntos a 
      todos los centroides
    2.Con esta distancia saca el vector de tags y los clusters para
    el numero determinado de puntos 
    3.Suma los puntos que corresponden a cada cluster 
"""
import argparse 
from scipy.spatial import distance
import numpy as np
import pandas as pd
from utils import *
from GenericWorker import DenseWorkerGeneric
from os.path import join
class DenseWorker(DenseWorkerGeneric):

    def calculateTagsAndSum(self, centroids, points, norm_centroids):
        #Calcula la distancia entre unos puntos y todos los centroides
        y = []
        sizes = [0] * self.n_clusters
        #Inicializo la suma de los puntos vacios
        sum_points = np.zeros((self.n_clusters, self.n_features))
        for p in (points):
            distance_point = []
            for i, centroid in enumerate(centroids):
                if self.distance_metric == "euclidean":
                    distance_point.append(distance.euclidean(p, centroid))
                elif self.distance_metric == "angular":
                   distance_point.append(cosineSimilarity(p, centroid, norm_centroids[i]))
            
            #A partir de las distancias anteriormente calculadas, crea 
            #los clusters y los tags, ademas de sumar los puntos de cada
            #cluster para que luego el sink los pueda promediar
            index_min = int(np.argmin(distance_point))
            y.append(index_min) #Tags
            sizes[index_min] += 1
            sum_points[index_min] += p #Suma de los puntos

        return (y, np.ndarray.tolist(sum_points), sizes)
    
    


if __name__ == "__main__":
    console = argparse.ArgumentParser()
    console.add_argument("dir_ventilator", type = str)
    console.add_argument("dir_sink", type = str)
    args = console.parse_args()

    worker = DenseWorker(args.dir_ventilator, args.dir_sink)
    worker.listen()