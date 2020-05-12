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
from GenericSink import GenericSink, createConsole
class SinkElbow(GenericSink):
    #Clase que funciona para recoger la suma de las distorsiones
    #calculadas por los workers, para asi enviarlos al ventilator
    
    def recieveFirstMessage(self):
        #Numero de tareas paralelizadas para calcular 
        #la distorsion en cada momento que se corre kmeans
        self.opers = int(self.from_ventilator.recv_string())
        print("Recieve first message")

    #Funcion donde le llegara el mensaje del ventilator
    def listen(self):
        print("Ready")
        self.recieveFirstMessage()

        while True:
            #Inicializo la suma, los clusters y los tags
            distorsion = 0
            for oper in range(self.opers):
                distorsion += float(self.from_ventilator.recv_string())

            print("Distorsion:", distorsion)
            print("Sending to fan")
            
            self.to_ventilator.send_string(str(distorsion))
            self.to_ventilator.recv()

if __name__ == "__main__":
    args = createConsole()
    sink = SinkElbow(args.dir_sink, args.dir_ventilator)
    sink.listen()