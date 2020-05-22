#include <iostream>
#include <vector>
#include <cassert>
#include <random>
#include <thread>
#include "timer.hh"

using namespace std;

//Clase matrix mas especifica, sin el template y va a ser cuaddrada
class Matrix {
private:
  vector<double> data;
  size_t rows;

//Constructor al que le llega el numero de filas y de columnas 
public:
  Matrix(size_t n) {
    rows = n;
    //Volvemos el vector del tamanio que lo necesitamos 
    data.resize(n  * n, 0.0);
  }

  //Constructor el que le llega una matriz ya 
  Matrix(const Matrix& m) {
    rows = m.rows;
    copy(m.data.begin(), m.data.end(), data.begin());
  }

  //Llena la matriz con numeros aleatorios los cuales siguen una 
  //distribucion uniforme 
  void fill() {
    default_random_engine generator;
		uniform_real_distribution<double> distribution(1.0,2.0);
		for(int i = 0; i < data.size(); i++){
			data[i] = distribution(generator);
		}
  }

  //Retorna el numero de filas
  size_t size() const { return rows; }

  //Retorna el numero de elementos de la matriz
  size_t elements() const { return data.size(); }

  //Accede a una posicion de la matriz
  double at(const int& row, const int& col) const {
    return data[row * rows + col];
  }

  //Accede a una posicion de la matriz pero por referencia, 
  //con esta funcion se pudene cambiar los valores de esta 
  double& at(const int& row, const int& col) {
    return data[row * rows + col];
  }

  //Imprime la matriz 
  void print() {
    for(int i = 0; i < size(); i++) {
      for (int j = 0; j < size(); j++) {
        cout << " " << at(i, j);
      }
      cout << endl;
    }
    cout << endl;
  }

  //Retorne true si dos matrices son iguales
  bool operator==(const Matrix &rhs) const {
		if(data.size() != rhs.size())
      return false;
		if(rows != rhs.rows)
      return false;

		for(int i = 0; i < data.size(); i++){
			if(data[i] != rhs.data[i])
        return false;
		}
		return true;
	}

  // Single thread matrix multiplication
  Matrix mult(const Matrix& m) {
    Matrix result(m.size());

    for(int r = 0; r < rows; r++ ) {
      for (int c = 0; c < rows; c++) {
        for (int rm = 0; rm < rows; rm++) {
          result.at(r, c) += at(r, rm) * m.at(rm, c);
        }
      }
    }

    return result;
  }
};


int main() {
  //Crea matrices de diversos tamanios para ver el tiempo que se demora 
  //operando 
  long i = 2500;
  while(i <= 5000){
    float prom = 0;
    //Itera 5 veces para realizar el promedio 
    for(int j = 0; j < 1; j++){
      Matrix m(i);
      m.fill();
      Matrix n(i);
      n.fill();
      //n.print();
      //m.print();
      Timer t;
      Matrix r = m.mult(n);
      float t_fin = t.elapsed();
      cout << t_fin << endl;

      prom += t_fin;
      //Para valores de i pequenios tomo mas muestras, si ya es mas grande
      //el espacio entre las muestras es mayor 
    }
    
    prom = prom / 5.0;
    cout << "Promedio para matrices cuadradas de " << 
          i << " elementos: " << prom << endl;

    if(i < 1000)
        i += 100;
    else
      i += 1000;
  }

}
