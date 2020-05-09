import numpy as np 
import scipy 
from sklearn.metrics.pairwise import cosine_similarity
import json
from math import isnan
"""
La similaridad oscila entre -1 y 1, por lo que no la podemos usar 
como medida de distancia porque viola la propiedad de positividad, 
el angulo oscila entre 0 y pi rad, donde pi rad es totalmente 
diferente y 0 son iguales, por lo que si se puede usar como medida
"""
def cosineSimilarity(point, centroid, norm_centroid):
    point = np.asarray(point)
    centroid = np.asarray(centroid)
    if point.shape[0] != centroid.shape[0]:
        centroid = centroid.T
    #Retorna el angulo (0-180 en rad) entre dos vectores 
    ab = point.dot(centroid)
    norm_a = np.linalg.norm(point)
    result = ab/(norm_a*norm_centroid)
    if result > 1.0:
        result = 1.0
    elif result < -1.0:
        result = -1.0
    return np.arccos(result) 

def cosineSimilaritySparseManual2(point, centroid, norm_centroid):
    norm_point = 0
    ab = 0

    for key in point.keys():
        a = point.get(key, 0)
        b = centroid[int(key)]
        norm_point += a**2
        ab += a*b
    norm_point = np.sqrt(norm_point)
    result =  ab/(norm_centroid*norm_point)
    #Con el punto flotante a veces cuando dos puntos eran iguales daba 
    #1.000000000000000001 y con el arcoseno de eso se tostaba 
    if result > 1.0:
        result = 1.0
    elif result < -1.0:
        result = -1.0
    # if isnan(result):
    #     print(centroid)
    #     print(point)
    #     print(ab, norm_point, norm_centroid)
    #     raise Exception("Bad operations")
    return np.arccos(result) 



def euclideanDistanceSparseManual2(point, centroid):
    centroid = np.asarray(centroid)
    point_np = np.zeros(centroid.shape)
    for key in point.keys():
        point_np[int(key)] = point[key]

    return scipy.spatial.distance.euclidean(point, centroid)

def sumDictAndPoint(p, d):
    #Suma un punto que es una lista normal y otro que esta en forma de 
    #diccionario 
    for key in d.keys():
        p[int(key)] += d[key]
    return p


def readSparseManual(name_dataset, skiprows, chunk):
    #Lee los datos del dataset que es una matriz dispersa hecha con una 
    #lista de directorios
    points = []
    with open(name_dataset, "r") as f:
        for i in range(skiprows):
            f.readline()
        
        for i in range(chunk):
            line = f.readline()
            if line == "":
                break
            points.append(json.loads(line[:-1]))

    return points
            



#### UNUSED FUNCTIONS 


def cuadraticEuclideanDistanceSparseManual(p1, p2):
    all_keys = {**p1, **p2}
    cuadratic_distance = 0
    for key in all_keys.keys():
        a = p1.get(key, 0)
        b = p2.get(key, 0)
        cuadratic_distance += (a-b) ** 2
    return cuadratic_distance



def cosineSimilaritySparseManual(p1, p2):
    all_keys = {**p1, **p2}
    norm_a = 0
    norm_b = 0
    ab = 0
    for key in all_keys.keys():
        a = p1.get(key, 0)
        b = p2.get(key, 0)

        norm_a += a**2
        norm_b += b**2

        ab += a*b
    return np.arccos(ab/(np.sqrt(norm_a*norm_b)))


def sumPointsDict(p1, p2):
    #Suma dos puntos dispersos que estan en forma de diccionario
    new_point = {**p1, **p2}
    for key in new_point.keys():
        a = p1.get(key, 0)
        b = p2.get(key, 0)
        new_point[key] = a+b
    return new_point