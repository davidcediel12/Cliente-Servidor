import numpy as np
from os.path import join 
import json 
import zmq
import pandas as pd 
from utils import *
class GenericWorker:
    #Abstract class para los otros tipos de worker
    #(sparse, sparse manual y dense)
    
    def __init__(self, dir_ventilator, dir_sink):
        self.dir_ventilator = dir_ventilator
        self.dir_sink = dir_sink
        self.createSockets()


    def createSockets(self):
        self.context = zmq.Context()

        self.from_ventilator = self.context.socket(zmq.PULL)
        self.from_ventilator.connect(f"tcp://{self.dir_ventilator}")

        self.to_sink = self.context.socket(zmq.PUSH)
        self.to_sink.connect(f"tcp://{self.dir_sink}")


    def recieveInitialData(self, msg):
        #Por ahora no se usa, ya que como no se cuantos workers tengo
        #no puedo enviar el data set al inicio
        self.name_dataset = msg["name_dataset"]
        self.name_dataset_splited = self.name_dataset.split(".")
        self.n_files = msg["n_files"]
        self.name_file_centroids = (self.name_dataset.split(".")[0] + 
                                                "_centroids.json")
        self.n_clusters = msg["n_clusters"]
        self.n_features = msg["n_features"]
        self.chunk = msg["chunk"]
        self.distance_metric = msg["distance_metric"]
        print("Recieved first message")
        self.has_tags  = msg["has_tags"]
        self.n_data = msg["n_data"]

        if self.n_files > 1:
            self.data_per_file = msg["data_per_file"]


    def readPartDataset(self, ini):
        #Sera sobreescrito por los que la hereden, lo pongo ahi 
        # pa saber que existe
        pass

    def calculateTagsAndSum(self, centroids, points, norm_centroids):
        #Sera sobreescrito por los que la hereden, lo pongo ahi 
        # pa saber que existe
        pass
    

    def readCentroids(self):
        with open(join("datasets", "results", self.name_file_centroids), "r") as f:
            data = json.loads(f.read())
        
        centroids = data["centroids"]
        norm_centroids = data.get("norm_centroids", None)

        return centroids, norm_centroids
        
    
    def listen(self): 
        print("Ready")
        while True:
            msg = self.from_ventilator.recv_json()
            action = msg["action"]
            if action == "new_dataset":
                    self.recieveInitialData(msg)
            elif action == "operate":
                ini = msg["position"]

                print("Calculating distance")
                

                centroids, norm_centroids = self.readCentroids()
                points = self.readPartDataset(ini)
               
                tags, sum_points, sizes = self.calculateTagsAndSum(centroids, points, norm_centroids)

                self.to_sink.send_json({
                    "tags" : tags,
                    "sum_points" : sum_points, 
                    "position" : ini,
                    "sizes" : sizes
                })


class SparseWorkerGeneric(GenericWorker):
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
       
                if len(data) < self.chunk and ini + self.chunk <= self.n_data:
                    #print("Opening other file to extract data")
                    n_part += 1
                    iters += 1
                else:
                    reading_parts = False

        print("Data readed", len(data))
        return data



class DenseWorkerGeneric(GenericWorker):
    def readPartDataset(self, ini):
        if self.n_files == 1:
            data = pd.read_csv(join("datasets", self.name_dataset), 
                                skiprows=ini, nrows=self.chunk).values
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
                
                if data.shape[0] < self.chunk and ini + self.chunk <= self.n_data:
                    #print("Opening other file to extract data")
                    print(ini+self.chunk)
                    n_part += 1
                    iters += 1
                else:
                    reading_parts = False
                
        if self.has_tags:
            data = data[:, :-1] 
        return data