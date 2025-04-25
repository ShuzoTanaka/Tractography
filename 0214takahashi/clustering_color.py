import numpy as np
from dipy.io.streamline import load_tck
from dipy.segment.clustering import QuickBundles
from fury import window, actor
from matplotlib import cm

# 入力ファイル
tck_file = 'track.tck'
fa_file = 'Takahashi_FA.nii.gz'

# streamlineの読み込み
streams_obj = load_tck(tck_file, reference=fa_file)
streamlines = streams_obj.streamlines
print(f"総streamline数: {len(streamlines)}")

# QuickBundlesでクラスタリング（距離閾値で調整）
threshold = 35.0  # 大きくすると「大まかに」クラスタ分けされます
qb = QuickBundles(threshold=threshold)
clusters = qb.cluster(streamlines)
print(f"クラスタ数: {len(clusters)}")

# 各クラスタごとに色を割り当て
cmap = cm.get_cmap('tab20', len(clusters))
scene = window.Scene()

for i, cluster in enumerate(clusters):
    color = cmap(i)[:3]  # RGB
    bundle_streamlines = [streamlines[idx] for idx in cluster.indices]
    stream_actor = actor.line(bundle_streamlines, color)
    scene.add(stream_actor)

print(f"クラスタ数: {len(clusters)}")
scene.SetBackground(0, 0, 0)
window.show(scene, size=(1000, 1000))

