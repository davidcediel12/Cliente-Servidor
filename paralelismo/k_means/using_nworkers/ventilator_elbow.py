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
class VentilatorElbow(GenericVentilatorElbow):
    chunk_worker = 100

    def elbowMethod(self):
        input("Press enter when all are ready")
        self.sendInitialData()
        self.obtainRect()
        for n_cluster in self.n_clusters[1:-1]:
            distorsion = self.obtainDistorsion(n_cluster)
            self.obtainDistance(distorsion, n_cluster)

        self.optimum_k = self.analized_n_clusters[np.argmax(self.distances)]
        print("Optimum_k", self.optimum_k)
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