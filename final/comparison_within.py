import numpy as np
import matplotlib.pyplot as plt
   
without = [3.5298070409999998, 7.036246125, 6.479003958, 13.088850833999999]
withh = [1.043926334, 1.2373739589999998, 1.09632834, 1.2589303022]
  
n=4
r = np.arange(n)
width = 0.25
  
  
plt.bar(r, without, color = 'pink',
        width = width, edgecolor = 'black',
        label='Without Indexing')
plt.bar(r + width, withh, color = 'y',
        width = width, edgecolor = 'black',
        label='With Indexing')
  
plt.xlabel("Points, Polygons")
plt.ylabel("Average time (seconds)")
plt.title("Average time for WITHIN n predicate")
  
# plt.grid(linestyle='--')
plt.xticks(r + width/2,['Points500, Poly10','Points1000, Poly10','Points500, Poly15','Points1000, Poly15'])
plt.legend()
  
plt.show()