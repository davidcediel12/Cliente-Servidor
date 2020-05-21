import numpy as np 
import matplotlib.pyplot as plt


k = sorted([1, 690, 345, 173, 87, 44, 130, 65, 195])
# 1 -> 0.008 h
# 690 -> 14.5
# 345 -> 7.6 
# 173 -> 3.8 
# 87 -> 1.6
# 44 -> 1
# 130 -> 3.5
# 65 -> 2.5
# 195 -> 4.5 

times = [0.008, 1, 1.6, 2.5, 3.5, 3.8, 4.5, 7.6, 14.5]

plt.scatter(k, times)
plt.show()
