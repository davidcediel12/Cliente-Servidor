import random
def merge(l1, l2):
    i = j = 0
    result = []
    #Itero sobre las dos listas para mezclarlas, de ahi viene 
    #el nombre de merge sort, cuando acabe de recorrer una lista, 
    #acabo el ciclo y pego lo que faltaba de la otra lista
    while i < len(l1) and j < len(l2):
        if l1[i] <= l2[j]:
            result.append(l1[i])
            i += 1
        else:
            result.append(l2[j])
            j += 1
    
    if i == len(l1):
        result.extend(l2[j:])
    else:
        result.extend(l1[i:])
    return result


#Parto a la lista a medios y llamo a la misma funcion hasta que
#quede un solo elemento, luego voy ordenando listas pequeñas 
def mergeSort(array):
    if len(array) == 1:
        return array

    middle = len(array) // 2
    
    l1 = mergeSort(array[:middle])
    l2 = mergeSort(array[middle:])

    return merge(l1, l2)


if __name__ == "__main__":
    #l = [random.randint(0, 100) for i in range(20)]
    l = [75, 46, 12, 41, 75, 72, 67, 44, 78, 74, 55, 84, 14, 91, 97, 75, 2 ,11, 94, 87 ]
    print(l)
    print(mergeSort(l))
