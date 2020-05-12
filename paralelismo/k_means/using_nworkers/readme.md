# Para correrlo 

Cabe recalcar que todos los datasets:
* Deben estar en la carpeta datasets
* Si es un csv, debe tener header 
* Deben tener un archivo que se llame [nombreDataset]_metadata.json que debe contener el numero de datos(n_data), de características (n_features), cuantos archivos tiene (n_files), y, si tiene más de un archivo, cuántos datos tiene por archivo (data_per_file)
## Ventilator
1. Direccion del ventilator para los workers
2. Direccion del ventilator para el sink
3. Direccion del sink
4. Nombre original del dataset (debe estar en la carpeta datasets)
7. Numero de clusters 
8. Opcional: Si el dataset lleva tags se pone -t
9. Tipo de distancia que usara el algoritmo
### python ventilator.py 127.0.0.1:5555 127.0.0.1:5556 127.0.0.1:5557 2c2f.csv 4 [-t] [euclidean|angular]

## Sink 
1. Direccion del sink
2. Direccion correspondiente del ventilator

### python sink.py 127.0.0.1:5557 127.0.0.1:5556

## Worker 

1. Direccion correspondiente del ventilator
2. Direccion del sink 

### python DenseWorker.py 127.0.0.1:5555 127.0.0.1:5557
### python SparseManualWorker.py 127.0.0.1:5555 127.0.0.1:5557


## Si se desea crear un dataset 

1. Nombre del archivo que se generara en datasets 
2. Número de clusters 
3. Número de caracteristicas 
4. Número de muestras
### python createBlobs.py nombre.csv 3 2 1000

# Elbow method 

Este metodo se usa para calcular el k óptimo, lo que hace es sumar la distorsión 
de todos los puntos con respecto a su cluster 

## Para correrlo 

Cabe recalcar que:
* Debe estar corriendo el kmeans paralelizado normal con sus workers y sink

### Ventilator elbow
1. Direccion del ventilator para los workers
2. Direccion del ventilator para el sink
3. Direccion del sink
4. Dirección del ventilator de k means
5. Dirección del ventilator de k means para usar con el sink
6. Dirección del sink de k means
7. Nombre del dataset (debe estar en la carpeta datasets)
8. Número de clusters mínimo
9. Número de clusters máximo
11. Tipo de distancia que usara el metodo k means
12. Opcional: Si el dataset lleva tags se pone -t
13. Opcional: Si el dataset es disperso se pone -s

#### python ventilator_elbow.py 
#### python ventilator_elbow_ternary.py
#### python ventilator_elbow_binary.py 127.0.0.1:6565 127.0.0.1:6566 127.0.0.1:6567 127.0.0.1:5555 127.0.0.1:5556 127.0.0.1:5557 4c2f.csv 2 6 [euclidean|angular]  [-t] [-s]

### Sink  elbow
1. Direccion del sink
2. Direccion correspondiente del ventilator

#### python sink_elbow.py 127.0.0.1:6567 127.0.0.1:6566

### Worker elbow

1. Direccion correspondiente del ventilator
2. Direccion del sink 

#### python worker_elbow.py 127.0.0.1:6565 127.0.0.1:6567
#### python workerElbow_sparseManual.py 127.0.0.1:6565 127.0.0.1:6567