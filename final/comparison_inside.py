import numpy as np
import matplotlib.pyplot as plt
   
without = [3.173104459, 6.257062209, 3.379003958, 6.7088850833999999]
withh = [0.6271322500000001, 1.1573739589999998, 0.713632834, 1.398489792]
  
n=4
r = np.arange(n)
width = 0.25
  
  
plt.bar(r, without, color = 'purple',
        width = width, edgecolor = 'black',
        label='Without Indexing')
plt.bar(r + width, withh, color = 'g',
        width = width, edgecolor = 'black',
        label='With Indexing')
  
plt.xlabel("Points, Polygons")
plt.ylabel("Average time (seconds)")
plt.title("Average time for INSIDE predicate")
  
# plt.grid(linestyle='--')
plt.xticks(r + width/2,['Points500, Poly10','Points1000, Poly10','Points500, Poly15','Points1000, Poly15'])
plt.legend()
  
plt.show()