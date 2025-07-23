import numpy as np
from sklearn.cluster import KMeans
import time

X = np.random.rand(5500, 3)
model = KMeans(n_clusters=3, random_state=0, n_init=1, max_iter=100, algorithm='elkan')

start = time.time()
model.fit(X)
end = time.time()

print(f'KMeans took {end - start:.4f} seconds')
