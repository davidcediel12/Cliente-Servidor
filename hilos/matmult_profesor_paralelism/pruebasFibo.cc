#include <iostream>
#include <future>
#include <thread>
#include "timer.hh"
#include <map>

/*
*   Prueba de paralelimso con la serie de Fiboncacci, se evaluan dos 
*   enfoques de paralelismo y se analizan los resultados. 
*/
using namespace std;


/*
* En esta funcion creo un hilo por cada llamado reccursivo, por lo que 
* se crearian 2^n hilos (Exceso de hilos)
*/
double fibonacci2(int n){
    if(n < 2) return 1.0;
    else{
        
        future<double> f1 = async(launch::async, fibonacci2, n-1);
        future<double> f2 = async(launch::async, fibonacci2, n-2);
        return f1.get() + f2.get();
    }
}


/*
* Funcion sin hilos, la usare en un hilo pero llamandola desde el main
*/
double fibonacci(int n){
    if(n < 2) return 1.0;
    else return fibonacci(n-1) + fibonacci(n-2);
}

/*
* Comparo los tiempos de las dos implementaciones, se puede observar que
* es mucho mejor paralelizar solo el primer llamado, porque 
    1.Se crean demasiados hilos si se hace un hilo por cada llamado
    2.Para calcular fibonacci(n) debo saber los valores de fibonacci(n-1)
    y de fibonacci(n-2), existe una dependencia de valores, no es atractivo
    paralelizar este tipo de funciones
*/
int main(){
    //Calculo fibonacci desde 1 hasta 50 y comparo tiempos
    for(int i = 5; i < 50; i++){
        cout << "F(" << i << ")->";
        Timer t;
        future<double> r1 = async(launch::async, fibonacci, i);
        r1.get();
        cout << "T1: "<< t.elapsed() << " ";

        Timer t2;
        double r2 = fibonacci2(i);
        cout << "T2: " << t2.elapsed() << endl;
    }
}