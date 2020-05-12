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
from GenericVentilatorElbow import GenericVentilatorElbow, createConsole

"""
A diferencia del ventilator elbow normal, este no realiza todas las iteraciones
en el rango dado, sino que hace una busqueda ternaria para asi ahorrar iteraciones 
"""
class VentilatorElbow(GenericVentilatorElbow):
    chunk_worker = 100


    def ternarySearch(self, left, right, iters = 0):
        print("Iters", iters)
        if left == right:
            if self.n_clusters[left] not in self.analized_n_clusters:
                self.obtainDistorsion(self.n_clusters[left])

            return self.n_clusters[left] 

        if right - left == 1:
            
            #Analizando las distorsiones
            if self.n_clusters[left] not in self.analized_n_clusters:
                value_left = self.obtainDistorsion(self.n_clusters[left])
                value_left = self.obtainDistance(value_left, self.n_clusters[left])
            else:
                value_left = self.distances[self.analized_n_clusters.index(self.n_clusters[left])]

            

            if self.n_clusters[right] not in self.analized_n_clusters:
                value_right = self.obtainDistorsion(self.n_clusters[right])
                value_right = self.obtainDistance(value_right, self.n_clusters[right])
            else:
                value_right = self.distances[self.analized_n_clusters.index(self.n_clusters[right])]

            
            
            #Hallando el valor optimo de k 
            if value_left > value_right:
                return  self.n_clusters[left]
            else:
                return self.n_clusters[right] 

    
        
        m1 = left + (right-left)//3
        m2 = right - (right-left)//3

        if self.n_clusters[m1] not in self.analized_n_clusters:
            value_m1 = self.obtainDistorsion(self.n_clusters[m1])
            value_m1 = self.obtainDistance(value_m1, self.n_clusters[m1])
        else:
            value_m1 = self.distances[self.analized_n_clusters.index(self.n_clusters[m1])]

        if self.n_clusters[m2] not in self.analized_n_clusters:
            value_m2 = self.obtainDistorsion(self.n_clusters[m2])
            value_m2 = self.obtainDistance(value_m2, self.n_clusters[m2])
        else:
            value_m2 = self.distances[self.analized_n_clusters.index(self.n_clusters[m2])]
       

        # print(values[m1], values[m2])
        if value_m1 <= value_m2:
            return self.ternarySearch(m1+1, right, iters + 1)
        elif value_m1 > value_m2:
            return self.ternarySearch(left, m2 - 1, iters + 1)

    
    def elbowMethod(self):
        input("Press enter when workers elbow are ready")
        self.sendInitialData()

        self.obtainRect()
        self.optimum_k = self.ternarySearch(0, len(self.n_clusters))
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