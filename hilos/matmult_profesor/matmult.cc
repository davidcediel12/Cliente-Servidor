#include "ThreadPool.hh"
#include "matrix.hh"
#include "timer.hh"
#include <cassert>
#include <iostream>
#include <random>
#include <thread>

using namespace std;

/**
 * Classical matrix multiplication
 */

//Puede ser de distintos tipos de dato
template <typename T>

Matrix<T> mult(const Matrix<T>& a, const Matrix<T>& b) {
  //Se asegura de que las matrices puedan ser multiplicadas
  assert(a.numCols() == b.numRows());
  //Inicializa la matriz resultante
  Matrix<T> result(a.numRows(), b.numCols());

  //size_t es un tipo de datos como long
  for (size_t r = 0; r < a.numRows(); r++)
    for (size_t c = 0; c < b.numCols(); c++)
      for (size_t nc = 0; nc < b.numRows(); nc++)
        result.at(r, c) += a.at(r, nc) * b.at(nc, c);
  return result;
}

/**
 * First try to parallel matrix multiplication.
 *
 * To learn:
 *  - Too many threads are bad!
 *  - Threads are not for free
 *  - Just using threads does not make a program faster!
 */
template <typename T>
void computeCell(const Matrix<T>& a, const Matrix<T>& b, size_t ra, size_t cb,
                 T& result) {
  assert(a.numCols() == b.numRows());
  result = 0.0;
  for (size_t nc = 0; nc < b.numRows(); nc++) {
    result += a.at(ra, nc) * b.at(nc, cb);
  }
}

template <typename T>
Matrix<T> mult2(const Matrix<T>& a, const Matrix<T>& b) {
  assert(a.numCols() == b.numRows());
  Matrix<T> result(a.numRows(), b.numCols());

  vector<thread> threads;

  for (size_t r = 0; r < a.numRows(); r++)
    for (size_t c = 0; c < b.numCols(); c++) {
      T& res = result.at(r, c);
      threads.push_back(
          thread(computeCell<T>, cref(a), cref(b), r, c, ref(res)));
    }

  for (thread& t : threads)
    t.join();
  return result;
}

/**
 *  Return naturally, requires futures!
 */
template <typename T>
T computeCell2(const Matrix<T>& a, const Matrix<T>& b, size_t ra, size_t cb) {
  assert(a.numCols() == b.numRows());
  T result = 0.0;
  for (size_t nc = 0; nc < b.numRows(); nc++) {
    result += a.at(ra, nc) * b.at(nc, cb);
  }
  return result;
}

template <typename T>
Matrix<T> mult2a(const Matrix<T>& a, const Matrix<T>& b) {
  assert(a.numCols() == b.numRows());

  vector<future<T>> result;

  for (size_t r = 0; r < a.numRows(); r++)
    for (size_t c = 0; c < b.numCols(); c++) {
      result.emplace_back(
          async(launch::async, computeCell2<T>, cref(a), cref(b), r, c));
    }

  Matrix<T> x(a.numRows(), b.numCols());
  for (size_t r = 0; r < x.numRows(); r++)
    for (size_t c = 0; c < x.numCols(); c++) {
      x.at(r, c) = result[x.numCols() * r + c].get();
    }

  return x;
}

/**
 * Second try to parallel matrix multiplication.
 *
 * To learn:
 *  - Problem knowledge is mandatory
 *  - Context switching needs to be compensated with thread load.
 */
// void computeCol(const Matrix& a, const Matrix& b, size_t col, Matrix& result)
// {
//   assert(a.numCols() == b.numRows());
//   for (size_t r = 0; r < a.numRows(); r++) {
//     for (size_t c = 0; c < a.numRows(); c++) {
//       result.at(r, col) += a.at(r, c) * b.at(c, col);
//     }
//   }
// }
//
// Matrix mult3(const Matrix& a, const Matrix& b) {
//   assert(a.numCols() == b.numRows());
//   Matrix result(a.numRows(), b.numCols());
//
//   vector<thread> threads;
//   for (size_t c = 0; c < b.numCols(); c++)
//     threads.push_back(thread(computeCol, cref(a), cref(b), c, ref(result)));
//
//   for (thread& t : threads)
//     t.join();
//   return result;
// }

/**
 * Third try to parallel matrix multiplication.
 *
 * To learn:
 *  - A pooler does not solve a problem! if the programmer does not know what
 *    concurrency is.
 */
// double computeCell(const Matrix& a, const Matrix& b, size_t ra, size_t cb) {
//   assert(a.numCols() == b.numRows());
//   double result = 0.0;
//   for (size_t nc = 0; nc < b.numRows(); nc++) {
//     result += a.at(ra, nc) * b.at(nc, cb);
//   }
//   return result;
// }
//
// Matrix mult4(const Matrix& a, const Matrix& b) {
//   assert(a.numCols() == b.numRows());
//   Matrix<double> result(a.numRows(), b.numCols());
//   {
//     ThreadPool pool(4);
//     for (size_t r = 0; r < a.numRows(); r++)
//       for (size_t c = 0; c < b.numCols(); c++) {
//         pool.enqueue([&a, &b, r, c]() {
//           return computeCell(a, b, r, c);
//         });
//       }
//   }
//   return result;
// }
//
// Matrix mult5(const Matrix& a, const Matrix& b) {
//   assert(a.numCols() == b.numRows());
//   Matrix result(a.numRows(), b.numCols());
//   {
//     ThreadPool pool(4);
//     for (size_t c = 0; c < b.numCols(); c++)
//       pool.enqueue([&result, &a, &b, c]() { computeCol(a, b, c, result); });
//   }
//   return result;
// }

void test(size_t n) {
  for (size_t i = 10; i < n;) {
    Matrix<double> a(i, i);
    Matrix<double> b(i, i);

    a.fill();
    b.fill();

    cout << i;

    // Timer t;
    // Matrix<double> r = mult(a, b);
    // cout << " - " << t.elapsed();
    //
    // Timer t2;
    // Matrix<double> s = mult2(a, b);
    // cout << " - " << t2.elapsed();
    //
    // Timer t2a;
    // Matrix<double> t = mult2a(a, b);
    // cout << " - " << t2a.elapsed();

    //
    // Timer t3;
    // Matrix u = mult3(a, b);
    // cout << " - " << t3.elapsed();
    //
    // Timer t4;
    // Matrix v = mult4(a, b);
    // cout << " - " << t4.elapsed();
    //
    // Timer t5;
    // Matrix w = mult4(a, b);
    // cout << " - " << t4.elapsed();

    cout << endl;

    i += 10;
  }
}

int main() {
  cout << "Concurrency!!" << endl;
  test(1000);
  //
  // Matrix a(2, 2);
  // a.fill();
  // a.print();
  //
  // Matrix b(2, 2);
  // b.fill();
  // b.print();
  //
  // Matrix c = mult(a, b);
  // Matrix n = mult3(a, b);
  // cout << (c == n) << endl;
  // // Matrix c(2, 2);
  // computeCol(a, b, 0, c);
  // c.print();

  // Matrix asq = mult(a, a);
  // Matrix asq2 = mult2(a, a);
  // cout << (asq == asq2) << endl;
}
