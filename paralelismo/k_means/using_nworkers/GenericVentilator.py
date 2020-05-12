import zmq 
import matplotlib.pyplot as plt 
import numpy as np 
import argparse 
from os.path import join 
import json 

class GenericVentilator:
    chunk_worker = 100
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
    
    def obtainDataAndFeatures(self):
        name_metadata = self.name_dataset.split(".")[0] + "_metadata.json"
        with open(join("datasets", name_metadata), "r") as f:
            data = json.loads(f.read())
        self.n_data = data["n_data"]
        self.n_features = data["n_features"]
        self.n_files = data["n_files"]
        self.data_per_file = None
        if self.n_files > 1:
            self.data_per_file = data["data_per_file"]
        else:
            self.data_per_file = self.n_data

    
    def __init__(self, name_dataset, has_tags, isSparse, my_dir, 
                    my_dir_sink, dir_sink, distance_metric):

        self.name_dataset = name_dataset
        self.obtainDataAndFeatures()
        self.distance_metric = distance_metric
        self.has_tags = has_tags
        self.isSparse = isSparse
        self.my_dir = my_dir
        self.my_dir_sink = my_dir_sink
        self.dir_sink = dir_sink
        self.createSockets()
