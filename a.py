import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

# 横100ピクセル × 高さ10ピクセル
width = 100
height = 10

# 0〜1の値を横方向に生成
gradient = np.linspace(0, 1, width).reshape(1, width)
gradient = np.repeat(gradient, height, axis=0)  # 高さ方向に繰り返し

# jet_r カラーマップで保存
plt.imsave("jet_r_horizontal_colormap.png", gradient, cmap='jet_r')

print("横向きの jet_r カラーバーを 'jet_r_horizontal_colormap.png' に保存しました。")