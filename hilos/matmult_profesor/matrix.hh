
#ifndef __MATRIX_HH__
#define __MATRIX_HH__


//Libreria para I/O
#include <iostream>
//Libreria para generar numeros aleatorios
#include <random>
//Libreria para vectores 
#include <vector>


//Trayendo cosas ya definidas de la libreria estandar de c
using std::vector;
using std::cout;
using std::endl;
using std::uniform_real_distribution;
using std::random_device;
using std::mt19937;


//Con este template podemos hacer que el vector de datos pueda
//ser de diversos tipos de dato : long, int, double
template <typename T>
class Matrix {
private:
  //Usamos una representacion de vector unico en vez de 
  //vector de vectores para optimizar la cache, ya que 
  //con los vectores de vectores, se sube a la cache datos que 
  //no se van a usar
  vector<T> data;
  //Numero de filas de la matriz
  size_t rows;
  //Numero de columnas
  size_t cols;


//Constructor de la clase matrix
public:
  Matrix(size_t r, size_t c) {
    rows = r;
    cols = c;
    data.resize(r * c, T());
  }
  
  //Getters para el numero de filas y de columnas 
  size_t numRows() const { return rows; }
  size_t numCols() const { return cols; }


  //Metodo que accesar a un dato de la matriz, como esta en un solo
  //vector, debemos hacer el acceso de esta manera
  T at(size_t i, size_t j) const {
    size_t idx = cols * i + j;
    return data[idx];
  }

  //Metodo para accesar a un dato de la matriz pero por referencia, 
  //con esta funcion se puede modificar los valores de la matriz
  T& at(size_t i, size_t j) {
    size_t idx = cols * i + j;
    return data[idx];
  }

  //Retorna si una matriz que le llega al metodo es igual 
  //a la matriz que esta como atributo de la clase
  bool operator==(const Matrix& rhs) const {
    if (rows != rhs.rows)
      return false;
    if (cols != rhs.cols)
      return false;
    //Itera por toda la matriz buscando datos diferentes
    //si llega al final es que son iguales
    for (size_t i = 0; i < data.size(); i++)
      if (data[i] != rhs.data[i])
        return false;
    return true;
  }

  //Usa el acceso por referencia de la funcion 'at'
  //para volver la matriz una matriz identidad
  void identity() {
    for (size_t r = 0; r < rows; r++)
      for (size_t c = 0; c < cols; c++)
        if (r == c)
          at(r, c) = 1.0;
  }


  //Llena la matriz con numeros aleatorios por medio de 
  //una distribucion uniforme
  void fill() {
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> dis(1.0, 2.0);
    for (size_t i = 0; i < data.size(); i++) {
      data[i] = dis(gen);
    }
  }


  //Imprime la matriz, es constante porque no se modifica la matriz
  void print() const {
    //Itera por todas las posiciones de la matriz, usando la funcion 
    //'at' para acceder a dicha posicion 
    for (size_t r = 0; r < rows; r++) {
      for (size_t c = 0; c < cols; c++) {
        cout << " " << at(r, c);
      }
      cout << endl;
    }
    cout << endl;
  }
};

#endif
