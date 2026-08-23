import datetime as dt
import numpy as np
import pandas as pd
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline
from sklearn.cluster import kMeans

# for each security:
#   read in data
#   calculate price movements (close to close)
#   append time series to list
# make dataframe from list of time series
# instantiate normalizer, kmeanscluster model
# for i in some range (with step > 1):
#   cluster with i groups
#   calculate silouhette score or some other metric
#   plot on graph
#   analyze with elbow method


normalizer = Normalizer()
cluster_model = KMeans(n_clusters=num_clusters, max_iter=num_iters)
pipeline = make_pipeline(normalizer, cluster_model)


# should take df column of price_movements as input
pipeline.fit()

# takes same input
clusters = pipeline.predict()

results = pd.DataFrame({
    'clusters': clusters,
    'tickers': # list(df.columns)
}).sort_values(by=['clusters'], axis=0)

print(results)
