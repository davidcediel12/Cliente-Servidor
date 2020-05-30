#include <iostream>
#include <thread>
#include "timer.hh"
#include "matrix.hh"
#include <vector>
#include <cassert>

using namespace std;

/*
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
    Matrix<T> result(a.numRows(), b.numCols());
    for(int i = 0; i < a.numRows(); i++)
        computeRow(a, b, i, result);
    return result;
}

template <typename T>
T computeCell(const Matrix<T>& a, const Matrix<T>& b, int i, int j){
    T result = 0.0;
    for(int k = 0; k < b.numRows(); k++){
        result += a.at(i, k) * b.at(k, j);
    }
    return result;
}

// En esta aproximacion sera lo mismo que la multiplicacion normal, 
// solo que hare otra funcion en el que se calcule una celda
template <typename T> 
Matrix<T> matrixMultByCell(const Matrix<T>& a, const Matrix<T>& b){
    assert(a.numCols() == b.numRows());
    Matrix<T> result(a.numRows(), b.numCols());
    
    for(int i = 0; i < a.numRows(); i++){
        for(int j = 0; j < b.numCols(); j++){
            result.at(i, j) = computeCell(a, b, i, j);;
        }
    }
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