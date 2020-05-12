"""
    Solo cambia las funciones de distancia y la forma de abrir 
    el dataset, la suma de los puntos ahora tambien es una matriz
    dispersa 
"""
import argparse 
import numpy as np
from utils import *
import time
from GenericWorker import SparseWorkerGeneric
from os.path import join


class SparseManualWorker(SparseWorkerGeneric):

    def calculateTagsAndSum(self, centroids, points, norm_centroids):
        #Calcula la distancia entre unos puntos y todos los centroides, con esto
        #saca  el cluster mas cercano para asi construir el vector de tags y 
        #la suma de los puntos de cada cluster
        #Matriz de tamanio data * centroids
        y = []
        sizes = [0] * self.n_clusters
        sum_points = np.zeros((self.n_clusters, self.n_features))

        init_time = time.time()

        for p in points:
            distance_point = []
            for i, centroid in enumerate(centroids):
                if self.distance_metric == "angular":
                    distance_point.append(cosineSimilaritySparseManual2(p, centroid, norm_centroids[i]))
                elif self.distance_metric == "euclidean":
                    distance_point.append(euclideanDistanceSparseManual2(p, centroid))


            #A partir de las distancias anteriormente calculadas, crea 
            #los tags, ademas de sumar los puntos de cada
            #cluster para que luego el sink los pueda promediar
            index_min = int(np.argmin(distance_point))
            y.append(index_min) #Tags
            sizes[index_min] += 1
            sum_points[index_min] = sumDictAndPoint(sum_points[index_min], p)

        print(f"Time {time.time()-init_time}")

        return (y, np.ndarray.tolist(sum_points), sizes)


if __name__ == "__main__":
    console = argparse.ArgumentParser()
    console.add_argument("dir_ventilator", type = str)
    console.add_argument("dir_sink", type = str)
    args = console.parse_args()

    worker = SparseManualWorker(args.dir_ventilator, args.dir_sink)
    worker.listen()