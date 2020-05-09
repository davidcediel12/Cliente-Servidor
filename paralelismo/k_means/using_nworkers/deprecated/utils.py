def readChunkSparse(n_rows, offset, name_dataset, column_size, dtype=np.float32):
    """
        Lee una parte de la matriz
        Con esta funcion puedo leer un numero de filas de una matriz dispersa sin tener que leer todo el archivo,
        solo lee el numero  de filas que es igual al n_rows, y lo lee desde un offset 
    """
    #El tamanio de cada item 
    data_item_size = dtype().itemsize
    item_size_indices_indptr = 4
    #Abrimos los 3 archivos al tiempo, los datos, los indices y el 
    #indptr(con este se sacan las filas)
    with open(name_dataset + ".data", 'rb') as data_file, \
            open(name_dataset + ".indices", 'rb') as indices_file, \
            open(name_dataset + ".indptr", 'rb') as indptr_file:



        #Muevo el puntero a la posicion deseada 
        indptr_file.seek(item_size_indices_indptr*offset) 

        #indptr_batch es el vector indptr que tiene de tamanio 
        #el n_rows + 1 (porque siempre tiene n+1 filas)
        indptr_with_bad_numbers = np.frombuffer(indptr_file.read(item_size_indices_indptr) + 
                                indptr_file.read(item_size_indices_indptr*n_rows),  dtype=np.int32)
        #Si solo tiene un elemento, ya acabamos el archivo porque recordemos 
        #que data[indptr[i] : indptr[i+1]] = row[i]
        if len(indptr_with_bad_numbers) == 1:
            return
        
        #Como ya lei unos datos y el inptr siempre es ejm:
        # [0 1 3 5], pero esto se refiere a las posiciones de 
        #los datos que tambien estoy leyendo por partes, debo hacer 
        # que el inptr siempre inicie en cero, independientemente si 
        #lo leo en su posicion 5000, por eso le resto first_number_indptr, que es 
        #el ultimo numero del indptr anterior (y el primero de este), asi me
        #aseguro de que empiece en cero 
        indptr_real = indptr_with_bad_numbers - indptr_with_bad_numbers[0]

        #Este numero me servira para saber cuanto debo leer de data
        last_number_indptr = int(indptr_real[-1])
        
        #Muevo el puntero de los archivos para abrir el chunk deseado, este 
        #no se mueve con el offset porque no se a ciencia cierta cuantos datos
        #han pasado a traves de este valor, con el que si se es con el primer
        #valor del indptr
        data_file.seek(data_item_size*indptr_with_bad_numbers[0]) 
        indices_file.seek(item_size_indices_indptr*indptr_with_bad_numbers[0]) 

        #Leo los datos y organizo el shape 
        batch_data = np.frombuffer(data_file.read(
                                    data_item_size * last_number_indptr), dtype=dtype)
        batch_indices = np.frombuffer(indices_file.read(
                                        item_size_indices_indptr * last_number_indptr), dtype=np.int32)

        dimensions = (len(indptr_real)-1, column_size)

        # print("Data", batch_data)
        # print("Indices", batch_indices)
        # print("Dimensions", dimensions)
        # print("Indptr", indptr_with_bad_numbers)
        matrix = scipy.sparse.csr_matrix((batch_data, 
                        batch_indices, indptr_real), shape=dimensions)

        return matrix



def cuadraticEuclideanDistanceSparse(v1, v2):
    return np.sum((v1-v2).power(2))


def cosineSimilarityForSparse(v1, v2):
    #Primera funcion de similaridad de cosenos intentada para los 
    #datos dispersos
    if v1.shape[1] != v2.shape[0]:
        ab = v1.dot(v2.T).toarray()[0][0]
    else:
       ab = v1.dot(v2).toarray()[0][0] 
    norm_a = np.sqrt(np.sum(v1.power(2)))
    norm_b = np.sqrt(np.sum(v2.power(2)))
    angle = np.arccos(ab/(norm_a*norm_b))
    return angle

def cosineSimilarityForSparse2(v1, v2):
    return np.arccos(cosine_similarity(v1, v2)[0][0])