"""
    Solo cambia las funciones de distancia y la forma de abrir 
    el dataset, la suma de los puntos ahora tambien es una matriz
    dispersa 
"""
import zmq
import argparse 
from scipy.spatial import distance
from scipy.sparse import csr_matrix, lil_matrix, csc_matrix
import numpy as np
from sklearn.datasets import make_blobs
import pandas as pd
from os.path import join 
from utils import *
import time 
from GenericWorker import GenericWorker
class SparseWorker(GenericWorker):

    def readPartDataset(self, ini):
        if self.n_files == 1:
            data = readChunkSparse(self.chunk, ini, self.name_dataset, 
                                self.n_features, dtype = np.int8)
        else:
            n_part = (ini // self.data_per_file) + 1 
            reading_parts = True
            iters = 0
            #Puede que termine de leer un archivo y no haya acabado de leer el 
            #chunk que le corresponde, por lo que esta en un while
            while reading_parts:
                name_part = (self.name_dataset_splited[0] + 
                            f"_{n_part}." + self.name_dataset_splited[1])

                
                if iters == 0:
                    #Leyendo el primer archivo
                    skip_rows = ini % self.data_per_file
                    data = readChunkSparse(self.chunk, ini, self.name_dataset, 
                                self.n_features, dtype = np.int8)
                else:
                    #Leyendo nuevo archivo
                    n_rows = self.chunk - data.shape[0]
                    data = data.extend(
                        readChunkSparse(
                            np.min([self.chunk-len(data), 
                            self.n_data - (ini+self.chunk)]), #Leo lo que sea mas pequeño
                            ini, self.name_dataset, 
                            self.n_features, dtype = np.int8))
                
                if len(data) < self.chunk and ini + self.chunk < self.n_data:
                    print("Opening other file to extract data")
                    print(ini+self.chunk)
                    n_part += 1
                    iters += 1
                else:
                    reading_parts = False
        return data



    def calculateTagsAndSum(self, centroids, points):
        #Calcula la distancia entre unos puntos y todos los centroides, con esto
        #saca la el cluster mas acercado para asi construir el vector de tags y 
        #la suma de los puntos de cada cluster
        #Matriz de tamanio data * centroids
        y = []
        centroids = csc_matrix(centroids)
        sum_points = lil_matrix((self.n_clusters, self.n_features))
        init_time = time.time()
        for p in (points):
            distance_point = []
            for centroid in centroids:
                if self.distance_metric == "euclidean":
                    distance_point.append(cuadraticEuclideanDistanceSparse(p, centroid))
                elif self.distance_metric == "angular":
                    distance_point.append(cosineSimilarityForSparse(p, centroid))
                    #distance_point.append(cosineSimilarityForSparse2(p, centroid))

            #A partir de las distancias anteriormente calculadas, crea 
            #los tags, ademas de sumar los puntos de cada
            #cluster para que luego el sink los pueda promediar
            index_min = int(np.argmin(distance_point))
            y.append(index_min) #Tags
            sum_points[index_min] += p #Suma de los puntos
        print(f"Time {time.time()-init_time}")
        return  (y, sum_points)
            

if __name__ == "__main__":
    console = argparse.ArgumentParser()
    console.add_argument("dir_ventilator", type = str)
    console.add_argument("dir_sink", type = str)
    args = console.parse_args()

    worker = Worker(args.dir_ventilator, args.dir_sink)
    worker.listen()