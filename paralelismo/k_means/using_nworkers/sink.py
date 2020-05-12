"""
    1.Recoge los clusters, los tags y la suma
     para cada centroide de los workers
        a. Pega los clusters parciales
        b. Promedia la suma de los puntos para cada centroide

"""

import zmq 
import numpy as np
import argparse
import time
from sklearn.datasets import make_blobs
from os.path import join 
import pandas as pd 
from operator import add
from GenericSink import GenericSink, createConsole


class SinkKMeans(GenericSink):
    #Clase que recoge los resultados de los workers los cuales son 
    #el vector de tags y la suma de los puntos para cada cluster para 
    #asi unirlos 

    def recieveFirstMessage(self):
        #Recibe los datos iniciales para empezar el metodo 
        msg = self.from_ventilator.recv_json()
        self.n_clusters = msg["n_clusters"]
        self.n_data = msg["n_data"]
        self.n_features = msg["n_features"]
        self.opers = msg["opers"]
        self.chunk = msg["chunk"]
        print("Recieve first message")

    def calculateSizeClusters(self, y):
        sizes = [0] * self.n_clusters
        for tag in y:
            sizes[tag] += 1
        return sizes


    def obtainResultsFromWorker(self):
        #Obtiene los resultados de los workers y construye el vector 'y' y 
        #la suma de los puntos de cada cluster

        #Inicializo la suma, los clusters y los tags
        sum_points = np.zeros((self.n_clusters, self.n_features))
        sizes = [0] * self.n_clusters
        y = [0] * self.n_data

        for oper in range(self.opers):
            msg = self.from_ventilator.recv_json()
            y_temp = msg["tags"]
            sum_points_temp = np.asarray(msg["sum_points"])
            sizes_temp = msg["sizes"]
            ini = msg["position"]

            fin = ini + self.chunk
            if fin > self.n_data:
                fin = self.n_data
            y[ini:fin] = y_temp.copy() #Voy armando el vector de tags

            for i in range(self.n_clusters):
                #Sumo los resultados de cada worker
                sum_points[i] = sum_points[i] + sum_points_temp[i]
                sizes[i] = sizes[i] + sizes_temp[i]
        return y, sum_points, sizes


    #Funcion donde le llegara el mensaje del ventilator
    def listen(self):
        print("Ready")
        #Este primer while true me servira para no tener que interrumpir 
        #el sink cada vez que quiero hacer un nuevo k means, asi podra 
        #recibir la data inicial y volver a empezar
        while True:
            self.recieveFirstMessage()

            #Lo meto en un while true porque no se cuantas iteraciones puede 
            #llegar a realizar kmeans, por lo que siempre debe estar 
            #disponible
            end = False
            while not end:
                y, sum_points, sizes = self.obtainResultsFromWorker()

                for i in range(len(sum_points)):
                    sum_points[i] = sum_points[i] / sizes[i]
                    
                print("Sending to fan")
                self.to_ventilator.send_json({
                    "centroids" : np.ndarray.tolist(sum_points),
                    "y" : y,
                    "sizes" : sizes
                })
                end = self.to_ventilator.recv_string() == "end"


if __name__ == "__main__":
    args = createConsole()
    sink = SinkKMeans(args.dir_sink, args.dir_ventilator)
    sink.listen()