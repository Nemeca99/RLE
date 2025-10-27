import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
import pyarrow.parquet as pq

PARQUET = 'good_grids.parquet'
CLUSTER_OUT = 'good_grids_with_clusters.parquet'
CSV_OUT = 'good_grids_with_clusters.csv'
SUMMARY_OUT = 'cluster_summary.txt'
N_CLUSTERS = 5  # You can tune this

# Load data
df = pd.read_parquet(PARQUET)

# Feature selection for clustering
features = [
    'delta', 'triad_avg', 'triad_stddev', 'mean_root_deviation',
    'multi_spread', 'single_spread', 'line_balance_score', 'corner_weight'
]
X = df[features].fillna(0).values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Clustering
clustering = AgglomerativeClustering(n_clusters=N_CLUSTERS)
labels = clustering.fit_predict(X_scaled)
df['cluster'] = labels

# Save with cluster labels
df.to_parquet(CLUSTER_OUT)
df.to_csv(CSV_OUT, index=False)

# Cluster summary
with open(SUMMARY_OUT, 'w') as f:
    for c in range(N_CLUSTERS):
        sub = df[df['cluster'] == c]
        f.write(f'Cluster {c}: {len(sub)} grids\n')
        f.write(sub[features].describe().to_string())
        f.write('\n---\n')
print(f"Clustered grids saved to {CLUSTER_OUT}, {CSV_OUT}, summary in {SUMMARY_OUT}")
