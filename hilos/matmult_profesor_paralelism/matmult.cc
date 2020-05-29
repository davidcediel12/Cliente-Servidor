#include "ThreadPool.hh"
#include "matrix.hh"
#include "timer.hh"
#include <cassert>
#include <iostream>
#include <random>
#include <thread>

using namespace std;

/**
 * First try to parallel matrix multiplication.s
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




void test(size_t n) {
  for (size_t i = 10; i < n;) {
    Matrix<double> a(i, i);
    Matrix<double> b(i, i);

    a.fill();
    b.fill();

    Timer t2;
    Matrix<double> s = mult2(a, b);
    cout << "Time: " << t2.elapsed();

    cout << endl;

    i += 100;
  }
}

int main() {
  cout << "Concurrency edited!!" << endl;

  long i = 100;
  while(i <= 1500){
    cout << "With " << i << " elements" << endl;
    test(i);
    i += 100;
  }

}
