from sklearn.datasets import make_blobs
import numpy as np
import zmq
import matplotlib.pyplot as plt
import argparse
import time
import pandas as pd 
from os.path import join
import csv 
from ventilator import Ventilator
import json
from GenericVentilatorElbow import GenericVentilatorElbow, createConsole

"""
A diferencia del ventilator elbow normal, este no realiza todas las iteraciones
en el rango dado, sino que hace una busqueda ternaria para asi ahorrar iteraciones 
"""
class VentilatorElbow(GenericVentilatorElbow):
    chunk_worker = 100
    
    def binarySearch(self, number, distorsion, distance_rect):

        #Hallo las dos pendientes para ver que intervalo analizo primero 
        pendiente_ini = self.obtainPendiente((number, distorsion), self.init_point)
        pendiente_fin = self.obtainPendiente((number, distorsion), self.end_point)


        left = number - (number//2)
        right = number + (number//2)
        
        if left in self.analized_n_clusters and right in self.analized_n_clusters:
            #Ya analice todas las particiones y no tengo para donde moverme
            return number 


        # Elijo que lado voy a explorar primero, con base en las pendientes
        # halladas, me voy por el lado que tenga mas pendiente 
        if pendiente_ini >= pendiente_fin:
            priority_queue = [left, right]
        else:
            priority_queue = [right, left]

        
        #Analizo la primera parte del intervalo, si la distancia a la recta 
        # inicial resulta ser mayor, me voy por ahi, si no, recurro al otro 
        # lado 

        # Si no he hecho k_means para este numero lo hago, si ya lo hice 
        # lo busco en el atributo de la clase 
        if priority_queue[0] not in self.analized_n_clusters:
            distorsion1 = self.obtainDistorsion(priority_queue[0])
            distance1 = self.obtainDistance(distorsion1, priority_queue[0])
        else:
            distorsion1 = self.distorsions[self.analized_n_clusters.index(priority_queue[0])]
            distance1 = self.distances[self.analized_n_clusters.index(priority_queue[0])]
        
        

        if distance1 >= distance_rect:
            return self.binarySearch(priority_queue[0], distorsion1, distance1)


        #En caso de que la distancia del primer intervalo sea menor, analizo el 
        #segundo intervalo, si es mayor, nunca se ejecutara esta parte del codigo
        if priority_queue[1] not in self.analized_n_clusters:
            distorsion2 = self.obtainDistorsion(priority_queue[1])
            distance2 = self.obtainDistance(distorsion2, priority_queue[1])
        else:
            distorsion2 = self.distorsions[self.analized_n_clusters.index(priority_queue[1])]
            distance2 = self.distances[self.analized_n_clusters.index(priority_queue[1])]
        
        

        if distance2 >= distance_rect:
            return self.binarySearch(priority_queue[1], distorsion2, distance2)


        #Si llega hasta aqui es porque la distancia a la recta de ambos intervalos 
        # es menor, por lo que la solucion es peor, entonces puedo concluir que el 
        # k optimo es el numero que le llego         
        return number 


    
    def elbowMethod(self):
        #Obtiene la distorsion para el k_min y el k_max, luego llama 
        #a binary search para realizar la busqueda
        input("Press enter when workers elbow are ready")
        self.sendInitialData()

        self.obtainRect()
        
        #Hago el k means para la mitad de los datos, como es el primero, siempre
        # se analiza. 
        partition = (self.n_clusters[0] + self.n_clusters[-1]) // 2
        distorsion_ini = self.obtainDistorsion(partition)
        distance_ini = self.obtainDistance(distorsion_ini, partition)

        #Busco el k optimo mediante busqueda binaria
        self.optimum_k = self.binarySearch(partition, distorsion_ini, distance_ini)


        print("Clusters: \n", self.analized_n_clusters)
        print("Distorsions: \n", self.distorsions)
        print("Distances: \n", self.distances)
        print("OPTIMUM K:", self.optimum_k)
        self.showResult()
        self.closeSockets()



if __name__ == "__main__":
    args = createConsole()
    ventilator_elbow = VentilatorElbow(args.name_file, args.tags,
                            args.my_dir, args.my_dir2, args.dir_sink, 
                            args.dir_fan_kmeans, args.dir_fan_kmeans2, 
                            args.dir_sink_kmeans, args.isSparse, 
                            args.n_clusters_min, args.n_clusters_max, 
                            args.distance_metric)
    ventilator_elbow.elbowMethod()