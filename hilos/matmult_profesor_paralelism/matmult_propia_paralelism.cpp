#include <iostream>
#include <thread>
#include "timer.hh"
#include "matrix.hh"
#include <vector>
#include <cassert>
#include <future>

using namespace std;

/*
*   Las funciones son las mismas que en el secuencial, pero agregandole 
*   hilos 
*   Multiplicacion de matrices propia, haciendo 3 enfoques:
*       a.Multiplicacion normal 
*       b.Se calcula cada celda en una funcion aparte
*       c.Se calcula cada fila en una funcion aparte
*/


template <typename T> 
void computeRow(const Matrix<T>& a, const Matrix<T>& b, int i, Matrix<T>& result){
    for(int j = 0; j < b.numCols(); j++){
        for(int k = 0; k < b.numRows(); k++){
            result.at(i, j) += a.at(i, k)* b.at(k, j);
        }
    }
}


template <typename T> 
Matrix<T> matrixMultByRow(const Matrix<T>& a, const Matrix<T>& b){
    assert(a.numCols() == b.numRows());
    vector<thread> threads;
    Matrix<T> result(a.numRows(), b.numCols());
    for(int i = 0; i < a.numRows(); i++)
        threads.push_back(
            //Le mando <T> en el constructor del hilo
            thread(computeRow<T>, cref(a), cref(b), i, ref(result)));

    
    //Debo hacer el for con '&' para acceder a la referencia del hilo 
    for(thread& t : threads)
        t.join();

    return result;
}

template <typename T>
void computeCell(const Matrix<T>& a, const Matrix<T>& b, int i, int j, Matrix<T>& result){
    for(int k = 0; k < b.numRows(); k++){
        result.at(i, j) += a.at(i, k) * b.at(k, j);
    }
}

// En esta aproximacion sera lo mismo que la multiplicacion normal, 
// solo que hare otra funcion en el que se calcule una celda
template <typename T> 
Matrix<T> matrixMultByCell(const Matrix<T>& a, const Matrix<T>& b){
    assert(a.numCols() == b.numRows());
    Matrix<T> result(a.numRows(), b.numCols());
    vector<thread> threads;
    for(int i = 0; i < a.numRows(); i++){
        for(int j = 0; j < b.numCols(); j++){
            //Le mando a y b como referencias constantes, y result como una referencia 
            threads.push_back(
                //Le mando <T> en el constructor del hilo 
                thread (computeCell<T>, cref(a), cref(b), i, j, ref(result)));
        }
    }
    //Debo hacer el for con '&' para acceder a la referencia del hilo 
    for(thread& t : threads)
        t.join();
    return result;
}

// Uso 'template typename T' para que la funcion pueda recibir
// varios tipos de matrices (int, double, float, etc)
// Le mando la referencia para que no ocupe tanto espacio, y es constante
// porque no tenemos que modificar las matrices 
template <typename T> 
Matrix<T> matrixMult(const Matrix<T>& a, const Matrix<T>& b){
    assert(a.numCols() == b.numRows());
    Matrix<T> result(a.numRows(), b.numCols());
    
    for(int i = 0; i < a.numRows(); i++){
        for(int j = 0; j < b.numCols(); j++){
            for(int k = 0; k < b.numRows(); k++){
                result.at(i, j) += a.at(i, k)* b.at(k, j);
            }
        }
    }
    return result;
}


int main(){
    for(int i = 10; i < 200; i += 10){
        cout << i << " ";
        Matrix<int> a(i, i);
        Matrix<int> b(i, i);
        a.fill();
        b.fill();
        //Multiplicacion normal 
        Timer t1;
        Matrix<int> result = matrixMult(a, b);
        cout << t1.elapsed() << " ";
        //Calculando en una funcion aparte celda a celda
        Timer t2;
        Matrix<int> result2 = matrixMultByCell(a, b);
        cout << t2.elapsed() << " ";
        //Calculando en una funcion aparte fila a fila 
        Timer t3;
        Matrix<int> result3 = matrixMultByRow(a, b);
        cout << t3.elapsed() << endl;
    } 
    
}