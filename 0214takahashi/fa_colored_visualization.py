import os
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from dipy.io.streamline import load_tractogram
from dipy.tracking.streamline import set_number_of_points
from dipy.viz import window, actor
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap

# ======= 入力ファイルのパスを指定 =======
fa_path = 'Takahashi_FA.nii.gz'
tck_path = 'track.tck'

# ======= FAマップの読み込み =======
fa_img = nib.load(fa_path)
fa_data = fa_img.get_fdata()
affine = fa_img.affine

# ======= Streamlineの読み込み =======
tractogram = load_tractogram(tck_path, fa_img, bbox_valid_check=False)
streamlines = list(tractogram.streamlines)

# ======= Streamlineを同じ長さに揃える（中点を取るため） =======
n_points = 20  # 20点に揃える
resampled_streamlines = list(set_number_of_points(streamlines, n_points))

# ======= 各streamlineのFA値をサンプリング =======
fa_means = []
for sl in resampled_streamlines:
    fa_vals = []
    for point in sl:
        ijk = np.round(np.linalg.inv(affine).dot(np.append(point, 1)))[:3].astype(int)
        if np.all((ijk >= 0) & (ijk < fa_data.shape)):
            fa_vals.append(fa_data[tuple(ijk)])
    if len(fa_vals) > 0:
        fa_means.append(np.mean(fa_vals))
    else:
        fa_means.append(0.0)

fa_means = np.array(fa_means)

# ======= FA値を0〜1に正規化 =======
norm = Normalize(vmin=np.min(fa_means), vmax=np.max(fa_means))
fa_normalized = norm(fa_means)

# ======= 可視化 =======
cmap = get_cmap('jet')
colors = cmap(fa_normalized)[:, :3]  # RGB

scene = window.Scene()
lines_actor = actor.line(resampled_streamlines, colors)
scene.add(lines_actor)

window.show(scene)
