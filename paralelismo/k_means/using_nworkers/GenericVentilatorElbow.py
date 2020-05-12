
import matplotlib.pyplot as plt  
import zmq 
import argparse 
from GenericVentilator import GenericVentilator
from ventilator import Ventilator
import numpy as np 
class GenericVentilatorElbow(GenericVentilator):
    chunk_worker = 100
    

    
    def sendInitialData(self):
        super().sendInitialData()
        #Calculando el numero de operaciones que se haran
        #para decirle al sink lo que debe esperar
        opers = self.n_data // self.chunk_worker
        if self.n_data % self.chunk_worker != 0:
            opers += 1

        self.to_sink.send_string(str(opers))

    
    def showResult(self):
        plt.scatter(self.analized_n_clusters, self.distances)
        plt.show()
        plt.scatter(self.analized_n_clusters, self.distorsions)
        plt.vlines(self.optimum_k, np.min(self.distorsions), 
                    np.max(self.distorsions), linestyles = "dashed")
        plt.show()
        name_fig = self.name_dataset.split(".")[0] + "_elbow.png"
        plt.savefig(f"results_elbow/{name_fig}")


    def obtainDistance(self, distorsion, n_cluster):
        #Retorna la distancia de un punto (n_cluster, distorsion) a 
        # la recta inicial (k_ini, distorsion):(k_fin, distorsion) 
        distance = abs(self.A*n_cluster + distorsion + self.C) / np.sqrt(self.A**2 + 1)
        self.distances.append(distance)
        return distance


    def obtainPendiente(self, p1, p2):
        # y2-y1 / x2-x1
        #print(p1, p2)
        return abs((p2[1] - p1[1]) / (p2[0] - p1[0]))

    
    def obtainDistorsion(self, n_cluster):
        #Metodo k_means paralelizado.
        print(f"K_means for {n_cluster} clusters")
        
        ventilator = Ventilator(self.name_dataset, self.has_tags, self.isSparse, 
                                self.dir_fan_kmeans, self.dir_fan_kmeans_for_sink, 
                                self.dir_sink_kmeans, n_cluster, self.distance_metric)
        ventilator.kmeans()
        centroids = ventilator.centroids
        n_data = ventilator.n_data
        i = 0
        while i < n_data:
            self.to_workers.send_json({
                "action" : "distance",
                "n_clusters" : len(centroids),
                "centroids" : centroids,
                "position" : i
            })
            i += self.chunk_worker

        
        distorsion = float(self.from_sink.recv_string())
        print("Distorsion recieved")
        self.from_sink.send(b" ")
        self.analized_n_clusters.append(n_cluster)
        self.distorsions.append(distorsion)
        return distorsion

    def obtainRect(self):
        #Obtiene la recta inicial del menor numero de k al mayor numero de k
        max_distorsion = self.obtainDistorsion(self.n_clusters[0])
        self.init_point = (self.n_clusters[0], max_distorsion)

        min_distorsion = self.obtainDistorsion(self.n_clusters[-1])
        self.end_point = (self.n_clusters[-1], min_distorsion)
         
        # -m 
        self.A = -1 * (min_distorsion - max_distorsion)/(self.n_clusters[-1] - self.n_clusters[0])
        # m*x1 - y1
        self.C = (self.A * -1 *self.n_clusters[0]) - max_distorsion

        self.obtainDistance(max_distorsion, self.n_clusters[0])
        self.obtainDistance(min_distorsion, self.n_clusters[-1])


    def __init__(self, name_dataset, has_tags, my_dir, 
                    my_dir_sink, dir_sink, dir_fan_kmeans, 
                    dir_fan_kmeans_for_sink, dir_sink_k_means, isSparse,  
                    n_clusters_min, n_clusters_max, distance_metric):

        super().__init__(name_dataset, has_tags, isSparse, my_dir, 
                    my_dir_sink, dir_sink, distance_metric)

        self.dir_fan_kmeans = dir_fan_kmeans
        self.dir_fan_kmeans_for_sink = dir_fan_kmeans_for_sink
        self.dir_sink_kmeans = dir_sink_k_means

        self.optimum_k = None
        self.n_clusters =  [i for i in range(n_clusters_min, n_clusters_max+1)]
        self.distances = []
        self.distorsions = []
        self.analized_n_clusters = []

def createConsole():
    console = argparse.ArgumentParser()
    console.add_argument("my_dir", type=str)
    console.add_argument("my_dir2", type=str)
    console.add_argument("dir_sink", type=str)

    console.add_argument("dir_fan_kmeans", type=str)
    console.add_argument("dir_fan_kmeans2", type=str)
    console.add_argument("dir_sink_kmeans", type=str)

    console.add_argument("name_file", type=str)
    console.add_argument("n_clusters_min", type=int)
    console.add_argument("n_clusters_max", type=int)
    console.add_argument("distance_metric", type=str)
    console.add_argument("-t", "--tags", action="store_true")
    console.add_argument("-s", "--isSparse", action="store_true")
    return console.parse_args()