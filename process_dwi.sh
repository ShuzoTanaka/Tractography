#!/bin/bash

# 手動roiデータ用スクリプト
# ./process_dwi.sh /Users/rira/Documents/研究室/卒業研究/MRtrix3/Babasaki_Katsuhiro/babasaki/Tract_3mm_ASSET_3 babasaki2 roifile
# スクリプトをエラー時に停止
set -e  # エラーが発生したらスクリプトを終了
trap 'echo "エラーが発生しました。処理を中断します。" >&2; exit 1' ERR

source /Users/tanakashuuzou/Documents/tractography/mrtrixenv/bin/activate
# 引数の確認
if [[ $# -lt 2 ]]; then
  echo "使用方法: $0 <DICOMフォルダ> <出力フォルダ> <roiファイル>"
  exit 1
fi

DICOM_DIR=$(realpath "$1")
OUTPUT_DIR=$2
ROI_FILE=$3 

# DICOMフォルダの存在確認
if [[ ! -d "$DICOM_DIR" ]]; then
  echo "指定されたDICOMフォルダが存在しません: $DICOM_DIR"
  exit 1
fi

# 出力フォルダの確認・作成
if [[ -d "$OUTPUT_DIR" ]]; then
  OUTPUT_DIR=$(realpath "$OUTPUT_DIR")
  echo "指定された出力フォルダは既に存在します: $OUTPUT_DIR"
  echo -n "上書きしてもよろしいですか？ (y/n): "
  read CONFIRMATION
  if [[ "$CONFIRMATION" != "y" ]]; then
    echo "処理を中止しました。"
    exit 0
  fi
else
  echo "出力フォルダを作成します: $OUTPUT_DIR"
  mkdir -p "$OUTPUT_DIR"
  OUTPUT_DIR=$(realpath "$OUTPUT_DIR")
fi

# DICOMの変換を実行
echo "DICOMファイルをNIFTIに変換中..."
dcm2niix -o "$OUTPUT_DIR" -f "DWI" -b y -z y "$DICOM_DIR"

# 出力フォルダ内でファイルの確認
echo "変換結果のファイルを確認中..."
NIFTI_FILE=$(realpath "$OUTPUT_DIR/DWI.nii.gz")
BVEC_FILE=$(realpath "$OUTPUT_DIR/DWI.bvec")
BVAL_FILE=$(realpath "$OUTPUT_DIR/DWI.bval")
JSON_FILE=$(realpath "$OUTPUT_DIR/DWI.json")

echo "ファイルの存在を確認中..."
if [[ -f "$NIFTI_FILE" ]]; then
  echo "  [OK] NIFTI ファイル: $NIFTI_FILE"
else
  echo "  [MISSING] NIFTI ファイルが見つかりません: $NIFTI_FILE"
fi

if [[ -f "$BVEC_FILE" ]]; then
  echo "  [OK] BVEC ファイル: $BVEC_FILE"
else
  echo "  [MISSING] BVEC ファイルが見つかりません: $BVEC_FILE"
fi

if [[ -f "$BVAL_FILE" ]]; then
  echo "  [OK] BVAL ファイル: $BVAL_FILE"
else
  echo "  [MISSING] BVAL ファイルが見つかりません: $BVAL_FILE"
fi

if [[ -f "$JSON_FILE" ]]; then
  echo "  [OK] JSON ファイル: $JSON_FILE"
else
  echo "  [MISSING] JSON ファイルが見つかりません: $JSON_FILE"
fi

# 全てのファイルが存在するか確認
if [[ ! -f "$NIFTI_FILE" || ! -f "$BVEC_FILE" || ! -f "$BVAL_FILE" || ! -f "$JSON_FILE" ]]; then
  echo "必要なファイルが揃っていません。処理を中止します。"
  exit 1
fi

echo "全ての必要なファイルが揃っています。処理を開始します。"

# 処理の開始
cd "$OUTPUT_DIR"

# 1. DWI データを MIF フォーマットに変換
echo "Step 1: Converting DWI data to MIF format..."
if ! mrconvert -fslgrad "$BVEC_FILE" "$BVAL_FILE" -json_import "$JSON_FILE" "$NIFTI_FILE" DWI.mif; then
  echo "Error: mrconvert failed."
  exit 1
fi

#前処理は省略

# 3. NiftiからROI マスク(.mif)を作成
echo "Step 3: Creating a sample ROI mask..."
if ! mrconvert "$ROI_FILE" ROI_mask.mif; then
  echo "Error: mrmath for ROI_mask failed."
  exit 1
fi

# 4. 白質応答関数の計算
echo "Step 4: Calculating WM response function..."
if ! dwi2response tournier DWI.mif WM_response_function.tx; then
  echo "Error: dwi2response failed."
  exit 1
fi

# 5. FOD (Fiber Orientation Distribution) の生成
echo "Step 5: Generating FOD (Fiber Orientation Distribution)..."
if ! dwi2fod csd DWI.mif WM_response_function.tx WM_FOD.mif -mask ROI_mask.mif; then
  echo "Error: dwi2fod failed."
  exit 1
fi

# 6. トラクトグラフィーの生成
echo "Step 6: Generating tractography..."
if ! tckgen WM_FOD.mif track.tck -seed_image ROI_mask.mif -mask ROI_mask.mif -select 10000; then
  echo "Error: tckgen failed."
  exit 1
fi

cd ..

echo "trcファイルの作成が完了しました。仮想環境を移動します"

# 仮想環境1を終了
deactivate || echo "仮想環境1の終了に問題がありましたが、処理を続行します。"

echo "次の仮想環境を有効化します..."
source /Users/tanakashuuzou/Documents/tractography/tractenv3/bin/activate

# 仮想環境の有効化確認
if [[ "$VIRTUAL_ENV" != "/Users/tanakashuuzou/Documents/tractography/tractenv3" ]]; then
  echo "仮想環境の有効化に失敗しました。"
  exit 1
fi

echo "仮想環境2内で処理を実行します..."
if ! python tract.py $OUTPUT_DIR; then
  echo "Error: tract.py の実行に失敗しました。"
  exit 1
fi

echo "仮想環境2での処理が正常に完了しました。"

# 仮想環境2を終了
deactivate || echo "仮想環境2の終了に問題がありましたが、処理を続行します。"

echo "すべての処理が正常に完了しました。"