# -*- coding: utf-8 -*-
"""model_recom.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15qVTzMqbPLDuiwImksaNKikVmy0uXsWo
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import time


#loading embeddings and mappings
data = np.load('word_embeddings.npy', mmap_mode='r')
with open('mappings.json') as f:
  map_ = json.load(f)
data_set = zip(list(map_.values()),data)

#Convert to dict for mappings and word_emb to combine
dict_emb = {}
for k,v in data_set:
  dict_emb[k] = v

#Read csv dataframe
pydf = pd.read_csv('CodeNetDataFrame.csv',header=True)
pydf['vectors'] = pydf['clean_docstring_tokens'].apply(lambda x: np.mean([dict_emb[word] for word in x.split() if word in dict_emb],axis=0))

#Data Cleaning and Preparation for training 
df = pydf[pydf['vectors'].apply(lambda x: x.shape == (100,))]
array = [df['vectors'].iloc[i] for i in range(len(df))]
X = np.array(array)

#Applying K-Means Algorithm
k_start = 10
k_end = 25

K = range(k_start,k_end)
dist_from_cluster_centres = []

for no_clusters in K:
    kmeans = KMeans(n_clusters=no_clusters, random_state=0).fit(X)
    dist_from_cluster_centres.append(kmeans.inertia_)

#Plotting the Elbow Line for getting the best K value to be used to cluster all the images
plt.plot(K,dist_from_cluster_centres)
plt.show()

#Training to the optimized Cluster
max_ = max(dist_from_cluster_centres)
num_clusters = k_start + dist_from_cluster_centres.index(max_)
km = KMeans(n_clusters=num_clusters,random_state=42)
km.fit(X)
clusters = km.labels_.tolist()

#NLP Part to input the human query with code snippet
from scipy.spatial.distance import cosine

query = str(input('Enter human query\n'))

def tokenize(text):
    # obtains tokens with a least 1 alphabet
    pattern = re.compile(r'[A-Za-z]+[\w^\']*|[\w^\']*[A-Za-z]+[\w^\']*')
    return ' '.join(pattern.findall(text.lower()))

def convertToVector(x):
  return np.mean([dict_emb[word] for word in x.split() if word in dict_emb],axis=0)


def getResults(c,vec):
  sub_df = df[df['labels'] == c][['code','vectors','docstring']]
  sub_df['cosine_score'] = sub_df['vectors'].apply(lambda x: 1-cosine(x,vec))
  sub_df.sort_values(by='cosine_score',ascending=False,inplace=True)
  return sub_df.iloc[0:5]

df['labels'] = clusters
q = tokenize(query)
query_vec = convertToVector(q)
query_cluster = km.predict([query_vec])
print(query_cluster[0])
recom = getResults(query_cluster[0],query_vec)
print('------------------------Code Recommendor----------------------------')
recom[['code','docstring']]
