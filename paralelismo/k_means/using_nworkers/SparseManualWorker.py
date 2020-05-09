"""
    Solo cambia las funciones de distancia y la forma de abrir 
    el dataset, la suma de los puntos ahora tambien es una matriz
    dispersa 
"""
import argparse 
import numpy as np
from utils import *
import time
from GenericWorker import GenericWorker
from os.path import join


class SparseManualWorker(GenericWorker):

    def readPartDataset(self, ini):
        chunk = self.chunk
        if ini + self.chunk > self.n_data:
            chunk = self.n_data - ini

        if self.n_files == 1:
            data = readSparseManual(join("datasets", self.name_dataset), 
                                    ini, chunk)
        else:
            n_part = (ini // self.data_per_file) + 1 
            # print(ini, self.data_per_file, n_part)
            reading_parts = True
            iters = 0
            #Puede que termine de leer un archivo y no haya acabado de leer el 
            #chunk que le corresponde, por lo que esta en un while
            while reading_parts:
                name_part = (self.name_dataset_splited[0] + 
                            f"_{n_part}." + self.name_dataset_splited[1])

                # print("Reading", name_part)
                # print("Ini", ini)
                if iters == 0:
                    #Leyendo el primer archivo
                    skip_rows = ini % self.data_per_file
                    # print("Skip rows", skip_rows)
                    data  = readSparseManual(
                        join("datasets", name_part), skip_rows, chunk)
                else:
                    #Leyendo nuevo archivo
                    data_to_read = np.min([self.n_data-ini, self.chunk-len(data)])
                    # print("Data to read", data_to_read)
                    data.extend(
                        readSparseManual(join("datasets", name_part), 0, data_to_read))
       
                if len(data) < self.chunk and ini + self.chunk < self.n_data:
                    # print("Opening other file to extract data")
                    n_part += 1
                    iters += 1
                else:
                    reading_parts = False

        print("Data readed", len(data))
        return data


    def calculateTagsAndSum(self, centroids, points, norm_centroids):
        #Calcula la distancia entre unos puntos y todos los centroides, con esto
        #saca  el cluster mas cercano para asi construir el vector de tags y 
        #la suma de los puntos de cada cluster
        #Matriz de tamanio data * centroids
        y = []

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
            sum_points[index_min] = sumDictAndPoint(sum_points[index_min], p)

        print(f"Time {time.time()-init_time}")

        return (y, np.ndarray.tolist(sum_points))


if __name__ == "__main__":
    console = argparse.ArgumentParser()
    console.add_argument("dir_ventilator", type = str)
    console.add_argument("dir_sink", type = str)
    args = console.parse_args()

    worker = SparseManualWorker(args.dir_ventilator, args.dir_sink)
    worker.listen()