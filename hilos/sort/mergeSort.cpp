#include <iostream>
#include <thread>
#include "timer.hh"

#include <vector>
#include <cassert>
#include <future>
#include <random>


using namespace std;

template<typename T>
vector<T> subVector(vector<T> const &v, int m, int n) {
   auto first = v.begin() + m;
   auto last = v.begin() + n;
   vector<T> vector(first, last);
   return vector;
}


vector<double> fill(int elements){
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> dis(1.0, 100.0);
    vector<double> result;
    time_t t;
    srand((unsigned) time(&t));
    for(int i = 0; i < elements; i++){
        result.push_back(dis(gen));
    }
    return result;
}

template<typename T>
void print(vector<T> anArray){
    cout << "[";
    for(int i = 0; i < anArray.size(); i++)
        cout << anArray[i] << " ";
    cout << "]" << endl;
}

template <typename T>
void merge2(vector<T>& array, const vector<T>& left, const vector<T>& right){
    int i = 0;
    int j = 0;
    int k = 0;
    
    while (i < left.size() && j < right.size()){
        if(left[i] < right[j]){
            array[k] = left[i];
            i++;
        }else {
            array[k] = right[j];
            j++;
        }
        k++;     
    }

    //Cuando llega aqui es porque uno de los dos vectores se acabo, 
    // por lo que podemos pegar el otro derecho 
    while(i < left.size()){
        array[k] = left[i];
        k++;
        i++;
    }

    while(j < right.size()){
        array[k] = right[j];
        j++;
        k++;
    }
}



/* 
*   A la funcion merge le llega el vector partido en dos por mid, 
*   cada parte esta ordenada, aqui se mezclan, si hay un elemento 
*   de la parte izquierda mayor a uno de la parte derecha se swappean, 
*   si es menor, se sigue con el otro elemento 
*/
template <typename T>
void merge(vector<T>& array, int i_left, int i_right, int mid){
    int i = 0;
    int j = 0;
    int k = i_left;
    

    vector<T> left = subVector(array, i_left, mid);
    vector<T> right = subVector(array, mid, i_right);
    while (i < left.size() && j < right.size()){
        if(left[i] < right[j]){
            array[k] = left[i];
            i++;
        }else {
            array[k] = right[j];
            j++;
        }
        k++;     
    }

    //Cuando llega aqui es porque uno de los dos vectores se acabo, 
    // por lo que podemos pegar el otro derecho 
    while(i < left.size()){
        array[k] = left[i];
        k++;
        i++;
    }

    while(j < right.size()){
        array[k] = right[j];
        j++;
        k++;
    }
}



template<typename T>
void mergeSort(vector<T>& anArray, int left, int right){

    if(right - left == 1)
        return;
    else{
        int middle = (left + right) / 2;
        mergeSort(anArray, left, middle);
        mergeSort(anArray, middle, right);
        merge(anArray, left, right, middle);
    }
}

template<typename T>
void mergeSortThread(vector<T>& anArray, int left, int right){

    if(right - left == 1)
        return;
    else{
        int middle = (left + right) / 2;

        if(right - left > 0.15 * (double) anArray.size()){
            thread t1(mergeSortThread<T>, ref(anArray), left, middle);
            thread t2(mergeSortThread<T>, ref(anArray), middle, right);
            t1.join();
            t2.join();
        }
        else{
            mergeSort(anArray, left, middle);
            mergeSort(anArray, middle, right);
        }
        merge(anArray, left, right, middle);
    }
}





void findBestTolerance(){
    double i = 0.01;
    double min_mean = 1000000;
    double best_tolerance;
    vector<double> myArray = fill(100000);
    while(i < 1){
        double mean = 0;
        for(int j = 0; j < 15; j++){
            vector<double> myArray2 = myArray;
            Timer t;
            mergeSortThread(myArray2, 0, myArray.size());
            mean += t.elapsed();
        }
        mean = mean/15;
        if(mean < min_mean){
            min_mean = mean;
            best_tolerance = i;
        }
        cout << "Tolerance " << i << " time: " << mean << endl;
        i += 0.01;
    }
    cout << "Best tolerance: " << best_tolerance << " with time " << min_mean << endl;
}
/*
*   Compara los tiempos de diferentes aproximaciones, 
*   sin hilos, hilos dentro del merge segun una tolerancia
*   y unicamente dos hilos 
*/
void comparisson(){

    int i = 1000;
    while(i < 100000){
        vector<double> myArray;
        vector<double> myArray2;
        vector<double> myArray3;

        cout << i << " ";
        myArray = myArray2 = myArray3 = fill(i);

        Timer t1;
        mergeSort(myArray, 0, myArray.size());
        cout << t1.elapsed() << " ";

        Timer t2;
        mergeSortThread(myArray2, 0, myArray2.size());
        cout << t2.elapsed() << " ";



        Timer t3;
        vector<double> sub1 = subVector(myArray3, 0, myArray3.size()/2);
        vector<double> sub2 = subVector(myArray3, myArray3.size()/2, myArray3.size());


        thread th1(mergeSort<double>, ref(sub1), 0, sub1.size());
        thread th2(mergeSort<double>, ref(sub2), 0, sub2.size());
        th1.join();
        th2.join();
        merge2(myArray3, sub1, sub2);
        cout << t3.elapsed() << " " << endl;

        // if(myArray == myArray2 && myArray == myArray3 && myArray2 == myArray3)
        //     cout << "True" << endl;
        // else
        //     cout << "False" << endl;
        i += 1000;
    }
}


void temp(){
    vector<double> myArray = fill(10);
    vector<double> myArray2 = myArray;
    print(myArray);
    mergeSort(myArray, 0, myArray.size());
    print(myArray);
    print(myArray2);
}
int main(){
    comparisson();
    //findBestTolerance();
    //temp();
}
