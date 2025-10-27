import sqlite3
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

DB = 'near_magic_candidates_streamable.sqlite'
TABLE = 'good_grids_nu'
CSV_OUT = 'good_grids_nu_clusters.csv'
PLOT_OUT = 'good_grids_nu_clusters.png'
SUMMARY_OUT = 'good_grids_nu_cluster_summary.txt'
N_CLUSTERS = 7  # You can tune this

# Load data from SQLite
def load_data():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(f'SELECT * FROM {TABLE}', conn)
    conn.close()
    return df

def compute_line_delta_std(grid_str):
    import grid_base36_utils
    grid = grid_base36_utils.base36_to_grid(grid_str)
    lines = [
        grid[0], grid[1], grid[2],
        grid[:,0], grid[:,1], grid[:,2],
        np.array([grid[i,i] for i in range(3)]),
        np.array([grid[i,2-i] for i in range(3)])
    ]
    sums = [int(np.sum(line)) for line in lines]
    return float(np.std(sums))

def main():
    df = load_data()
    # Compute stddev of line deltas for each grid
    df['line_delta_stddev'] = df['grid_base36'].apply(compute_line_delta_std)
    # Features for clustering
    features = ['triad_avg', 'delta', 'single_spread', 'multi_spread', 'line_delta_stddev']
    X = df[features].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # PCA to 2D
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X_scaled)
    # KMeans clustering
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    df['cluster'] = labels
    df['pca_x'] = X_2d[:,0]
    df['pca_y'] = X_2d[:,1]
    # Save CSV
    df.to_csv(CSV_OUT, index=False)
    # Plot
    plt.figure(figsize=(8,6))
    for c in range(N_CLUSTERS):
        sub = df[df['cluster']==c]
        plt.scatter(sub['pca_x'], sub['pca_y'], s=20, label=f'Cluster {c}')
    plt.xlabel('PCA 1')
    plt.ylabel('PCA 2')
    plt.title('good_grids_nu: KMeans Clusters (PCA 2D)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOT_OUT)
    # Cluster summary
    with open(SUMMARY_OUT, 'w') as f:
        f.write('cluster_id,count,avg_delta,percent_repairable\n')
        for c in range(N_CLUSTERS):
            sub = df[df['cluster']==c]
            count = len(sub)
            avg_delta = sub['delta'].mean() if count else 0
            percent_repairable = 100*sub['repairable'].mean() if count else 0
            f.write(f'{c},{count},{avg_delta:.2f},{percent_repairable:.1f}\n')
    print(f"Clustered grids saved to {CSV_OUT}, plot to {PLOT_OUT}, summary in {SUMMARY_OUT}")

if __name__ == '__main__':
    main()
