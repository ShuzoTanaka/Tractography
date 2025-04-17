import nibabel as nib
from dipy.tracking.streamline import set_number_of_points, length
from dipy.segment.clustering import QuickBundles
import matplotlib.pyplot as plt
import numpy as np

# .tck 読み込み
tck_file = nib.streamlines.load("track.tck")
streamlines = list(tck_file.streamlines)

# ストリームラインの resample（クラスタリングのため）
streamlines_resampled = set_number_of_points(streamlines, 20)

# クラスタリング（距離のしきい値を設定：小さいほど細かく分類）
qb = QuickBundles(threshold=10.0)
clusters = qb.cluster(streamlines_resampled)

print(f"クラスタ数: {len(clusters)}")

# 可視化：最初の5クラスタを表示
colors = plt.cm.jet(np.linspace(0, 1, len(clusters)))

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

for i, cluster in enumerate(clusters[:5]):
    for s in cluster:
        s = np.array(s)
        ax.plot(s[:, 0], s[:, 1], s[:, 2], color=colors[i])

plt.title("上位5クラスタのストリームライン可視化")
plt.show()
