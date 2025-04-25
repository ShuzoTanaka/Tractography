import os
import sys
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
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
streamline_colors = []
fa_means = []

for streamline in streamlines_transformed:
    values = []
    for point in streamline:
        voxel = np.round(np.dot(np.linalg.inv(fa_affine), np.append(point, 1))[:3]).astype(int)
        if all((0 <= voxel) & (voxel < fa_data.shape)):
            values.append(fa_corrected[tuple(voxel)])  # ← 補正後のFAを使う！
        else:
            values.append(0.0)
            
    # 各ストリームライン内で正規化
    if len(values) > 0:
        fa_min_local = np.min(values)
        fa_max_local = np.max(values)
        if fa_max_local - fa_min_local == 0:
            normed = [0.0 for _ in values]
        else:
            normed = [(v - fa_min_local) / (fa_max_local - fa_min_local) for v in values]

        # 色を設定（赤〜黄）
        streamline_colors.append([
            [1.0, v, 0.0] for v in normed  # R=1.0, G=正規化, B=0.0
        ])

        # ★ ここでストリームラインごとの平均を記録
        fa_means.append(np.mean(values))

    else:
        streamline_colors.append([[1.0, 0.0, 0.0] for _ in streamline])  # デフォルト赤
        fa_means.append(0.0)




# 正規化のための最大・最小値を取得
fa_min = np.min(fa_means)
fa_max = np.max(fa_means)

# 選べるカラーマップ：'jet', 'viridis', 'plasma', 'magma', 'inferno', 'cividis', 'coolwarm', 'bwr' など
colormap = cm.get_cmap('jet_r')  # ここでカラーマップ選択

def get_color_from_fa(fa_value, fa_min, fa_max):
    if fa_max - fa_min == 0:
        normalized_fa = 0
    else:
        normalized_fa = (fa_value - fa_min) / (fa_max - fa_min)
    
    color = colormap(normalized_fa)  # RGBAで取得される (0-1)
    return list(color[:3])  # RGBのみ取り出す


# ストリームラインの色を計算
streamline_colors = np.array([get_color_from_fa(fa, fa_min, fa_max) for fa in fa_means])

# 3D可視化
stream_actor = actor.line(streamlines_transformed, colors=streamline_colors)
scene = window.Scene()
scene.add(stream_actor)
window.show(scene)





