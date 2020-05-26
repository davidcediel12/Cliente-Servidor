#ifndef __MATRIX_HH__
#define __MATRIX_HH__

#include <iostream>
#include <random>
#include <vector>

using std::vector;
using std::cout;
using std::endl;
using std::uniform_real_distribution;
using std::random_device;
using std::mt19937;

template <typename T>
class Matrix {
private:
  vector<T> data;
  size_t rows;
  size_t cols;

public:
  Matrix(size_t r, size_t c) {
    rows = r;
    cols = c;
    data.resize(r * c, T());
  }

  size_t numRows() const { return rows; }
  size_t numCols() const { return cols; }

  T at(size_t i, size_t j) const {
    size_t idx = cols * i + j;
    return data[idx];
  }

  T& at(size_t i, size_t j) {
    size_t idx = cols * i + j;
    return data[idx];
  }

  bool operator==(const Matrix& rhs) const {
    if (rows != rhs.rows)
      return false;
    if (cols != rhs.cols)
      return false;
    for (size_t i = 0; i < data.size(); i++)
      if (data[i] != rhs.data[i])
        return false;
    return true;
  }
  void identity() {
    for (size_t r = 0; r < rows; r++)
      for (size_t c = 0; c < cols; c++)
        if (r == c)
          at(r, c) = 1.0;
  }

  void fill() {
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> dis(1.0, 2.0);
    for (size_t i = 0; i < data.size(); i++) {
      data[i] = dis(gen);
    }
  }

  void print() const {
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
