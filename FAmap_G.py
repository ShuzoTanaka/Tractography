"""
@.tractenv3
02/20修正、正しそうなFAmapを作成可能にしました!
ただし、色の変化がわかりづらいです。
highlited_FA.nii.gzを新規ファイルとして、参照した箇所を見ることができる
"""

import os
import sys
import numpy as np
import nibabel as nib
from dipy.io.streamline import load_tck
from dipy.viz import window, actor
from dipy.io.image import load_nifti
from dipy.tracking.streamline import transform_streamlines
from scipy.ndimage import gaussian_filter


# コマンドライン引数でディレクトリを取得
if len(sys.argv) < 5:
    print("使用方法: python FAmap.py <tckファイル> <DWI.nii.gzファイル> <faファイル> <(出力ファイル名)highlighted_FA.nii.gz>")
    sys.exit(1)

# .tck ファイルと参照画像のパス
tck_file = sys.argv[1]
reference_file = sys.argv[2]  # DWI 参照画像
fa_file = sys.argv[3]  # FAマップのパス
highlighted_fa_path = sys.argv[4]

# FAマップと DWI のロード
fa_data, fa_affine = load_nifti(fa_file)
dwi_data, dwi_affine = load_nifti(reference_file)

# .tck ファイルをロード
sft = load_tck(tck_file, reference=reference_file)
streamlines = sft.streamlines 

# ガウシアンフィルタによる補正
fa_corrected = gaussian_filter(fa_data, sigma=1)

# DWI の座標系から FA マップの座標系への変換行列
affine_transform = np.linalg.inv(dwi_affine) @ fa_affine

# ストリームラインをFAマップの空間に変換
streamlines_transformed = list(transform_streamlines(streamlines, affine_transform))

# 参照されたボクセルを記録するマスクを作成
accessed_voxels = np.zeros_like(fa_data, dtype=bool)

# ストリームラインごとのFA平均値を計算
fa_means = []
for streamline in streamlines_transformed:
    values = []
    for point in streamline:
        voxel = np.round(np.dot(np.linalg.inv(fa_affine), np.append(point, 1))[:3]).astype(int)
        if all((0 <= voxel) & (voxel < fa_data.shape)):
            values.append(fa_corrected[tuple(voxel)])
    mean_fa = np.mean(values) if values else 0
    fa_means.append(mean_fa)


# 正規化のための最大・最小値を取得
fa_min = np.min(fa_means)
fa_max = np.max(fa_means)

def get_color_from_fa(fa_value, fa_min, fa_max):
    if fa_max - fa_min == 0:
        normalized_fa = 0  # すべての値が同じ場合、0にする
    else:
        normalized_fa = (fa_value - fa_min) / (fa_max - fa_min)  # 0-1の範囲に正規化
    
    # print(normalized_fa)

    # 赤チャネルは常に強く (一定の高い値)
    red_channel = 1.0

    # 緑チャネルはFA値が高いほど強くなる（赤からオレンジへの変化）
    green_channel = normalized_fa

    # 青チャネルは固定で0（赤とオレンジのみを表現）
    blue_channel = 0.0

    return [red_channel, green_channel, blue_channel]

# ストリームラインの色を計算
streamline_colors = np.array([get_color_from_fa(fa, fa_min, fa_max) for fa in fa_means])

# 3D可視化
stream_actor = actor.line(streamlines_transformed, colors=streamline_colors)
scene = window.Scene()
scene.add(stream_actor)
window.show(scene)

