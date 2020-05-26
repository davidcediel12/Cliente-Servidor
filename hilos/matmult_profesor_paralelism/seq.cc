#include <iostream>
#include <vector>
#include <cassert>
#include <random>
#include <thread>
#include "timer.hh"

using namespace std;

class Matrix {
private:
  vector<double> data;
  size_t rows;
public:
  Matrix(size_t n) {
    rows = n;
    data.resize(n  * n, 0.0);
  }

  Matrix(const Matrix& m) {
    rows = m.rows;
    copy(m.data.begin(), m.data.end(), data.begin());
  }

  void fill() {
    default_random_engine generator;
		uniform_real_distribution<double> distribution(1.0,2.0);
		for(int i = 0; i < data.size(); i++){
			data[i] = distribution(generator);
		}
  }

  size_t size() const { return rows; }

  size_t elements() const { return data.size(); }

  double at(const int& row, const int& col) const {
    return data[row * rows + col];
  }

  double& at(const int& row, const int& col) {
    return data[row * rows + col];
  }

  void print() {
    for(int i = 0; i < size(); i++) {
      for (int j = 0; j < size(); j++) {
        cout << " " << at(i, j);
      }
      cout << endl;
    }
    cout << endl;
  }

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
  Matrix m(400);
  m.fill();
  Matrix n(400);
  n.fill();

  //n.print();

  //m.print();
  Timer t;
  Matrix r = m.mult(n);
  cout << t.elapsed() << endl;
}
