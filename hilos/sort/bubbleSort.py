import random

#Swappeo posicion a posicion asegurandome que en cada iteracion 
#ordeno un elemento, la lista se ordena desde el final hasta el 
#principio
def bubble(array): 
    #Este end es la ultima posicion que quedara bloqueada porque 
    # se habra organizado, lo empiezo en 1 porque hago la comparacion
    # con j+1, por lo que se saldria del rango   
    end = 1
    #Uso esta variable para que no itere de mas si la lista ya esta ordenada
    swapped = True
    i = 0
    while i <  len(array) and swapped:
        swapped = False
        for j in range(len(array) - end):
            if array[j] > array[j+1]:
                temp = array[j]
                array[j] = array[j+1]
                array[j+1] = temp
                swapped = True
        end += 1
        i += 1
    return array

if __name__ == "__main__":
    l = [random.randint(0, 100) for i in range(20)]
    print(bubble(l))