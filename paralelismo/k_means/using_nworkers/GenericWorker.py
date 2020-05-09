import numpy as np
from os.path import join 
import json 
import zmq
from math import ceil 

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
               
                tags, sum_points = self.calculateTagsAndSum(centroids, points, norm_centroids)

                self.to_sink.send_json({
                    "tags" : tags,
                    "sum_points" : sum_points, 
                    "position" : ini
                })
