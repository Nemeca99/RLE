import sqlite3
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

DB = 'near_magic_candidates_streamable.sqlite'
TABLE = 'good_grids_wide'
CSV_OUT = 'good_grids_wide_clusters.csv'
PLOT_OUT = 'good_grids_wide_clusters.png'
SUMMARY_OUT = 'good_grids_wide_cluster_summary.txt'
N_CLUSTERS = 7  # You can tune this

# Load data from SQLite
def load_data():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(f'SELECT * FROM {TABLE}', conn)
    conn.close()
    return df

def compute_line_delta_std(grid_str):
    # grid_str: base36 string, decode to 3x3 grid
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
    df['line_delta_std'] = df['grid_base36'].apply(compute_line_delta_std)
    # Features for clustering
    features = ['triad_avg', 'delta', 'single_spread', 'multi_spread', 'line_delta_std']
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
    plt.title('good_grids_wide: KMeans Clusters (PCA 2D)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOT_OUT)
    # Cluster summary
    with open(SUMMARY_OUT, 'w') as f:
        for c in range(N_CLUSTERS):
            sub = df[df['cluster']==c]
            f.write(f'Cluster {c}: {len(sub)} grids\n')
            f.write(f'  Avg delta: {sub["delta"].mean():.2f}\n')
            f.write(f'  Avg triad_avg: {sub["triad_avg"].mean():.2f}\n')
            f.write(f'  Avg single_spread: {sub["single_spread"].mean():.2f}\n')
            f.write(f'  Avg multi_spread: {sub["multi_spread"].mean():.2f}\n')
            f.write(f'  Avg line_delta_std: {sub["line_delta_std"].mean():.2f}\n')
            f.write(f'  % repairable: {100*sub["repairable"].mean():.1f}\n')
            f.write('---\n')
    print(f"Clustered grids saved to {CSV_OUT}, plot to {PLOT_OUT}, summary in {SUMMARY_OUT}")

if __name__ == '__main__':
    main()
