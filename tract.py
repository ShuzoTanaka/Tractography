"""
tckファイルとniiファイル(参照画像)からtractographyを作成するスクリプト
参照画像を .nii に変換（もし .mif の場合）:
@bash
mrconvert DWI_preproc.mif DWI_preproc.nii.gz
"""

import os
import sys
from dipy.io.streamline import load_tck
from dipy.viz import window, actor
import nibabel as nib

# コマンドライン引数でディレクトリを取得
if len(sys.argv) < 2:
    print("使用方法: python visualize_tracts.py <ディレクトリパス>")
    sys.exit(1)

input_dir = sys.argv[1]

# 入力ディレクトリの確認
if not os.path.isdir(input_dir):
    print(f"指定されたディレクトリが存在しません: {input_dir}")
    sys.exit(1)

# ファイルパスの設定
tck_file = os.path.join(input_dir, "track.tck")
reference_file = os.path.join(input_dir, "DWI.nii.gz")

# ファイルの存在確認
if not os.path.isfile(tck_file):
    print(f"track.tck が見つかりません: {tck_file}")
    sys.exit(1)

if not os.path.isfile(reference_file):
    print(f"DWI.nii.gz が見つかりません: {reference_file}")
    sys.exit(1)

# nibabelで参照画像をロード
reference_img = nib.load(reference_file)

# .tckファイルを読み込む
sft = load_tck(tck_file, reference=reference_img)

# トラクトのストリームラインを取得
streamlines = sft.streamlines

# 3D可視化
scene = window.Scene()
stream_actor = actor.line(streamlines)
scene.add(stream_actor)
window.show(scene)
