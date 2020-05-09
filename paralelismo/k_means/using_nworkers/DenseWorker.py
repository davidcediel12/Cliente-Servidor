"""
    Para esta implementacion, cada worker:
    1.Calcula la distancia del los que le llegaron puntos a 
      todos los centroides
    2.Con esta distancia saca el vector de tags y los clusters para
    el numero determinado de puntos 
"""
import argparse 
from scipy.spatial import distance
import numpy as np
import pandas as pd
from utils import *
from GenericWorker import GenericWorker
from os.path import join
class DenseWorker(GenericWorker):

    def readPartDataset(self, ini):
        if self.n_files == 1:
            data = pd.read_csv(join("datasets", self.name_dataset), 
                                skiprows=ini, nrows=self.chunk)
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
                    data = pd.read_csv(join("datasets", name_part), 
                                        skiprows=skip_rows, nrows=self.chunk).values
                else:
                    #Leyendo nuevo archivo
                    n_rows = self.chunk - data.shape[0]
                    data = np.concatenate((data, pd.read_csv(join("datasets", name_part), 
                                        skiprows=0, nrows=n_rows).values))
                
                if data.shape[0] < self.chunk and ini + self.chunk < self.n_data:
                    print("Opening other file to extract data")
                    print(ini+self.chunk)
                    n_part += 1
                    iters += 1
                else:
                    reading_parts = False
                
                if self.has_tags:
                    data = data[:, :-1] 
        return data


    def calculateTagsAndSum(self, centroids, points, norm_centroids):
        #Calcula la distancia entre unos puntos y todos los centroides
        y = []
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
            sum_points[index_min] += p #Suma de los puntos

        return (y, np.ndarray.tolist(sum_points))
    
    


if __name__ == "__main__":
    console = argparse.ArgumentParser()
    console.add_argument("dir_ventilator", type = str)
    console.add_argument("dir_sink", type = str)
    args = console.parse_args()

    worker = DenseWorker(args.dir_ventilator, args.dir_sink)
    worker.listen()