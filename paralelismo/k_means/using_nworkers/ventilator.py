import numpy as np
import zmq
import matplotlib.pyplot as plt
import argparse
import time
import pandas as pd 
from os.path import join
import csv 
import scipy.sparse as sparse
from matplotlib.colors import TABLEAU_COLORS
import json
import math
"""
En esta aproximacion, el ventilator:
1.Instancia los centroides
2.Llama a los workers como instanciar el dataset
3.Los activa enviandoles la operacion y 
    a.Los puntos para los que deben calcular la distancia a 
    todos los clusters, junto con los centroides

4.Recibe 
    a.Los clusters
    b.La posicion de los centroides
    c.Los tags
"""

class Ventilator:
    max_iters = 100000
    chunk_worker = 10000
    tolerance = 0.1

    def createSockets(self):
        self.context = zmq.Context()

        self.to_workers = self.context.socket(zmq.PUSH)
        self.to_workers.bind(f"tcp://{self.my_dir}")

        self.to_sink = self.context.socket(zmq.PUSH)
        self.to_sink.connect(f"tcp://{self.dir_sink}")

        self.from_sink = self.context.socket(zmq.REP)
        self.from_sink.bind(f"tcp://{self.my_dir_sink}")

    def closeSockets(self):
        self.to_workers.unbind(f"tcp://{self.my_dir}")
        self.to_sink.disconnect(f"tcp://{self.dir_sink}")
        self.from_sink.unbind(f"tcp://{self.my_dir_sink}")

    def readPartDataset(self, i):
        #Lee una parte del dataset desde un 'i' dado, 
        #si ya no existen mas datos indica que no hay mas que hacer
        data = pd.read_csv(join("datasets", self.name_dataset), 
                            skiprows=i, nrows=self.chunk_worker)
        if self.has_tags:
            values = data.values[:, :-1]
        else:
            values = data.values        
        reading = values.shape[0] == self.chunk_worker
        return values, reading 


    def writeCentroids(self):
        # Guardamos los centroides y su norma en un archivo 
        # para que los workers puedan trabajar con el 
        norm_centroids = [np.linalg.norm(centroid) for centroid in self.centroids]
        with open(join("datasets", "results", self.name_file_centroids), "w") as f:
            f.write(json.dumps({
                "centroids" : self.centroids,
                "norm_centroids" : norm_centroids
            }))
            
    def obtainLine(self, index):
        n_file = (index // self.data_per_file) + 1
        skip_rows = index % self.data_per_file
        name_splited = self.name_dataset.split(".")
        name_part = name_splited[0] + f"_{n_file}." + name_splited[1]
        with open(join("datasets", name_part), "r") as f:
            for _ in range(skip_rows):
                f.readline()
            line = f.readline()
        return line 

    def createCentroids(self):
        #Creamos los centroides de manera aleatoria en el rango de cada 
        #caracteristica
        print("Creating centroids")
        self.centroids = []
        indexes_for_build_centroids = []

        #Elijo el indice de los puntos que serviran como centroides 
        for cluster in range(self.n_clusters):
            print(f"Cluster {cluster}")
            number = np.random.randint(1, high=self.n_data-1)
            while number in indexes_for_build_centroids:
                number = np.random.randint(1, high=self.n_data-1)
            indexes_for_build_centroids.append(number)

        #Leo el dataset para llegar a los centroides que necesito
        for index_point in indexes_for_build_centroids:
            if self.n_files == 1:
                with open(join("datasets", self.name_dataset), "r") as f:
                    for _ in range(index_point):
                        f.readline()
                    value = f.readline()
            else:
                value = self.obtainLine(index_point)

            if "netflix2" in self.name_dataset:
                #Si entra aqui es porque cada punto  del dataset es un diccionario
                centroid = [0] * self.n_features
                value = json.loads(value[:-1])
                for key in value.keys():
                    centroid[int(key)] = value[key]
                value = centroid.copy()
            else:
                #Si no, seran datos densos
                value = np.fromstring(value, sep = ",")
                if self.has_tags:
                    value = value[:-1]
                value = np.ndarray.tolist(value)

            self.centroids.append(value)
            self.writeCentroids()

    def showResult(self):
        #Si tiene dos caracteristicas, abre el dataset por partes y lo 
        #muestra solo al final 

        colors = []
        for color in list(TABLEAU_COLORS):
            colors.append(color.split(":")[-1])
        print(colors)
        reading = True 
        i = 0
        while reading:
            data, reading = self.readPartDataset(i)
            
            mini_clusters = []
            for _ in range(self.n_clusters):
                mini_clusters.append([])

            if reading:
                for j, p in enumerate(data):
                    mini_clusters[self.y[i + j]].append(p)

                for index, mini_cluster in enumerate(mini_clusters):
                    if len(mini_cluster) != 0:
                        color = colors[index % len(colors)]
                        data_stacked = np.stack(mini_cluster)
                        plt.scatter(data_stacked[:, 0], data_stacked[:, 1], c = color)

            i += self.chunk_worker

        for c in self.centroids:
            plt.scatter(c[0], c[1], c = "black", marker = "D")
        
        plt.show()
            
    def sendInitialData(self):
        i = 0 
        #Para no enviarle el dataset en cada iteracion, se le envia el nombre
        #que ellos deben abrir 
        while i < self.n_data:
            data = {
                "action" : "new_dataset",
                "name_dataset" : self.name_dataset,
                "n_clusters" : self.n_clusters,
                "n_features" : self.n_features,
                "has_tags" : self.has_tags,
                "chunk" : self.chunk_worker,
                "distance_metric" : self.distance_metric,
                "n_files" : self.n_files,
                "n_data" : self.n_data,
            }
  
            if self.n_files > 1:
                data["data_per_file"] = self.data_per_file

            self.to_workers.send_json(data)
            i += self.chunk_worker

        #Calculando el numero de operaciones que se haran
        #para decirle al sink lo que debe esperar
        opers = self.n_data // self.chunk_worker
        if self.n_data % self.chunk_worker != 0:
            opers += 1

        self.to_sink.send_json({
            "n_clusters" : self.n_clusters,
            "n_features" : self.n_features, 
            "n_data" : self.n_data, 
            "opers" : opers,
            "chunk" : self.chunk_worker,
        })

    def sendCalculateDistance(self):
        #Los workers calculan la distancia de un numero determinado
        # de puntos punto a todos los  cluster
        i = 0
        while i < self.n_data:
            self.to_workers.send_json({
                "action" : "operate",
                "position" : i
                
            })
            i += self.chunk_worker
    
    def writeTags(self):
        #Escribe el vector y en un nuevo csv 
        
        name_result = join("datasets", "results", 
                        (self.name_dataset.split(".")[0] +
                        f"_result{self.n_clusters}c.csv"))
        print("Saved in", name_result)
        with open(name_result, 'w') as f:
            f.write("tag\n")
            for tag in self.y:
                f.write(str(tag)+"\n")
            

    def kmeans(self):
        #Metodo k_means paralelizado.
        
        i = 3
        while i > 0:
            print(f"Starting in {i} sec")
            time.sleep(1)
            i -= 1


        #Creo los centroides a partir de un punto aleatorio del dataset
        self.createCentroids()

        self.sendInitialData()
        

        self.y =  np.zeros(self.n_data, dtype = np.int8)
        changing = True
        iters = 0
        while changing and iters < self.max_iters:
            init_time = time.time()
            iters += 1
            print("Iters", iters)
            print("Operating")

            self.sendCalculateDistance()

            #Del sink recibo los tags, los clusters y los 
            #centroides
            print("Waiting result from sink")
            result = self.from_sink.recv_json()
            

            size_clusters = result["sizes"]
            y_new = result["y"]
            self.centroids = result["centroids"]

           
            print(f"Iter time: {(time.time()-init_time) /60}")

            falses = np.equal(self.y, np.asarray(y_new))
            falses = np.sum(np.where(falses == False, 1, 0))
            #Si ningun punto ha cambiado de cluster paro de iterar
            if falses/self.n_data < self.tolerance:
                changing = False
                self.from_sink.send_string("end")
            else:
                self.from_sink.send_string("continue")
                if np.min(size_clusters) == 0:
                    #No deberia entrar a este if pero lo pongo por si cualquier
                    #cosa
                    print("EMPTY CLUSTER")
                    self.createCentroids()
                self.y = y_new.copy()
        print("Sizes", sorted(size_clusters))
        print("END")
        self.writeTags()

        if self.n_features == 2:
            self.showResult()
        
        self.closeSockets()
    

    def obtainDataAndFeatures(self):
        name_metadata = self.name_dataset.split(".")[0] + "_metadata.json"
        with open(join("datasets", name_metadata), "r") as f:
            data = json.loads(f.read())
        self.n_data = data["n_data"]
        self.n_features = data["n_features"]
        
        self.data_per_file = None
        if self.n_files > 1:
            self.data_per_file = data["data_per_file"]

    def __init__(self, name_dataset, n_files, has_tags, my_dir, 
                    my_dir_sink, dir_sink, 
                    n_clusters, distance_metric):

        self.name_dataset = name_dataset
        self.n_files = n_files
        self.obtainDataAndFeatures()
        self.name_file_centroids = (self.name_dataset.split(".")[0] + 
                                    "_centroids.json")
        self.distance_metric = distance_metric
        self.n_clusters = n_clusters
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
    console.add_argument("n_files", type=int)
    console.add_argument("n_clusters", type=int)
    console.add_argument("distance_metric", type=str)
    console.add_argument("-t", "--tags", action="store_true")
    return console.parse_args()

if __name__ == "__main__":
    args = createConsole()
    ventilator = Ventilator(args.name_file, args.n_files, args.tags, 
                            args.my_dir, args.my_dir2, args.dir_sink, 
                            args.n_clusters, args.distance_metric)
    ventilator.kmeans()