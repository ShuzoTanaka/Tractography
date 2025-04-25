import nibabel as nib
import numpy as np
from dipy.io.streamline import load_tractogram
from dipy.tracking.streamline import values_from_volume
from dipy.viz import window, actor
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# 入力ファイル
tck_path = 'track.tck'
fa_path = 'Takahashi_FA.nii.gz'

# tractogramの読み込み（FA空間でロード）
tractogram = load_tractogram(tck_path, fa_path)
streamlines = list(tractogram.streamlines)

# FAマップ読み込み
fa_img = nib.load(fa_path)
fa_data = fa_img.get_fdata()
affine = fa_img.affine

# クラスタリング
n_clusters = 10
print(f"クラスタリングを{n_clusters}クラスタで実行中...")
kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit([s[0] for s in streamlines])
labels = kmeans.labels_

# クラスタごとのFA正規化と色付け
streamline_colors = []

for cluster_id in range(n_clusters):
    cluster_indices = [i for i, lbl in enumerate(labels) if lbl == cluster_id]
    cluster_fa_means = []

    for i in cluster_indices:
        fa_vals = values_from_volume(fa_data, [streamlines[i]], affine=affine)[0]
        if len(fa_vals) > 0:
            cluster_fa_means.append(np.mean(fa_vals))
        else:
            cluster_fa_means.append(0.0)

    fa_min = np.min(cluster_fa_means)
    fa_max = np.max(cluster_fa_means)
    print(f"Cluster {cluster_id}: Streamlines={len(cluster_indices)}, FA Min={fa_min:.3f}, FA Max={fa_max:.3f}")

    # 色の割り当て
    for fa in cluster_fa_means:
        norm_fa = (fa - fa_min) / (fa_max - fa_min + 1e-6)
        color = plt.cm.jet(norm_fa)[:3]
        streamline_colors.append(color)

# 可視化（streamlinesはすでにFA空間なので変換不要）
stream_actor = actor.line(streamlines, streamline_colors, linewidth = 3.0)
scene = window.Scene()
scene.add(stream_actor)
window.show(scene)
