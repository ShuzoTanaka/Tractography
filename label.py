import nibabel as nib
import numpy as np
import sys

def extract_label(input_path, output_path, target_label):
    # NIfTI画像を読み込む
    img = nib.load(input_path)
    data = img.get_fdata()

    # 指定ラベルのみを残し、それ以外は0にする
    extracted_data = np.where(data == target_label, target_label, 0)

    # 保存用NIfTI作成
    new_img = nib.Nifti1Image(extracted_data.astype(np.uint8), img.affine, img.header)
    nib.save(new_img, output_path)
    print(f"[INFO] ラベル {target_label} のみを含むNIfTIを保存しました: {output_path}")

def main():
    if len(sys.argv) != 4:
        print("使用方法: python label.py <DWI.nii.gz> <target_label(int)> <output_file.nii.gz>")
        sys.exit(1)

    label_image_path = sys.argv[1]
    try:
        target_label = int(sys.argv[2])
    except ValueError:
        print("[ERROR] <target_label> は整数で指定してください。")
        sys.exit(1)
    output_path = sys.argv[3]

    extract_label(label_image_path, output_path, target_label)

if __name__ == "__main__":
    main()
