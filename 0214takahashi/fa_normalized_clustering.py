import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from dipy.io.streamline import load_trk
from dipy.io.streamline import load_tck
from dipy.tracking.streamline import set_number_of_points
from dipy.tracking.streamline import transform_streamlines
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D
import os

# --- 設定 ---
tck_path = "track.tck"
fa_path = "Takahashi_FA.nii.gz"
num_points = 20     # ストリームラインのリサンプリング点数
n_clusters = 66     # クラスタ数（前回取得）

# --- ストリームライン読み込み＆特徴抽出 ---
streams_obj = load_tck(tck_path, reference=fa_path)
streamlines = list(streams_obj.streamlines)

# 各ストリームラインを同じ数の点にリサンプリング
resampled_streams = set_number_of_points(streamlines, num_points)

# 特徴ベクトルに変換（flatten）
features = [s.flatten() for s in resampled_streams]

# --- クラスタリング ---
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
labels = kmeans.fit_predict(features)

# --- FAマップ読み込み ---
fa_img = nib.load(fa_path)
fa_data = fa_img.get_fdata()
affine = fa_img.affine

# --- ストリームラインをボクセル空間へ変換 ---
streamlines_vox = list(transform_streamlines(resampled_streams, np.linalg.inv(affine)))

# --- 可視化の準備 ---
colors = plt.cm.tab20(np.linspace(0, 1, n_clusters))
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# --- 各クラスタでFA正規化＆描画 ---
for i in range(n_clusters):
    cluster_indices = np.where(labels == i)[0]
    fa_vals = []
    for idx in cluster_indices:
        sl = streamlines_vox[idx]
        sl_fa_vals = []
        for point in sl:
            x, y, z = np.round(point).astype(int)
            if 0 <= x < fa_data.shape[0] and 0 <= y < fa_data.shape[1] and 0 <= z < fa_data.shape[2]:
                fa = fa_data[x, y, z]
                if not np.isnan(fa):
                    sl_fa_vals.append(fa)
        if sl_fa_vals:
            mean_fa = np.mean(sl_fa_vals)
            fa_vals.append((idx, mean_fa))

    # 正規化
    if fa_vals:
        fa_array = np.array([val for _, val in fa_vals])
        fa_norm = (fa_array - fa_array.min()) / (fa_array.max() - fa_array.min() + 1e-6)

        # 描画（FA値を色に反映）
        for (idx, _), norm_val in zip(fa_vals, fa_norm):
            sl = resampled_streams[idx]
            ax.plot(sl[:, 0], sl[:, 1], sl[:, 2], color=plt.cm.plasma(norm_val), linewidth=1)

# 軸ラベル
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title("クラスタごとのFA正規化表示")

plt.show()
