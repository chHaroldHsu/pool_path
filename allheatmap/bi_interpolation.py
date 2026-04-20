import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Matrix : 要計算的二維矩陣
# A, b : 兩端點
# Target : 要插值的位置
def interpolation(Matrix, A, B, Target):
    # 第一個點的值
    P1_value = Matrix[A[0]][A[1]]
    # 第二個點的值
    P2_value = Matrix[B[0]][B[1]]
    if np.isnan(P1_value) and np.isnan(P2_value):
        print("\nall nan")
        return 0
    elif np.isnan(P1_value):
        return P2_value
    elif np.isnan(P2_value):
        return P1_value
    
    if A[0] == B[0]:
        return ((A[1] - Target[1])/(A[1] - B[1])) * P2_value + ((Target[1] - B[1])/(A[1] - B[1])) * P1_value
    elif A[1] == B[1]:
        return ((A[0] - Target[0])/(A[0] - B[0])) * P2_value + ((Target[0] - B[0])/(A[0] - B[0])) * P1_value
    else:
        print("ERROR INPUT!!!!")
        return 0

# Matrix : 要計算的二維矩陣
# Target : 要插值的位置
# step : 插值的間隔
def BilinearInterpolation(Matrix, Target, step):
    x, y = Target
    x0, y0 = (x // step) * step + 1 , (y // step) * step + 1
    x1, y1 = min(x0 + step, Matrix.shape[0] - 1), min(y0 + step, Matrix.shape[1] - 1)
    # if x  == 97 or y ==202:
    #     print(f'x, y, x0, y0, x1, y1 = ', x, y, x0, y0, x1, y1)
    P1 = [x0, y0]
    P2 = [x0, y1]
    P3 = [x1, y0]
    P4 = [x1, y1]
    PR1 = [x0, y]
    PR2 = [x1, y]
    # 第一次線性插值
    Matrix [x0][Target[1]] = interpolation(Matrix, P1, P2, PR1)
    Matrix [x1][Target[1]] = interpolation(Matrix, P3, P4, PR2)
    # 第二次線性插值
    Matrix[x][y] = interpolation(Matrix, PR1, PR2, Target)
    return Matrix

def main(x, step, Cx, Cy):
    updated_matrix = np.nan_to_num(x, nan=0)
    needed_x = 5
    while needed_x < 99:
        needed_y = 5
        while needed_y <= 203:
            ''''''
            updated_matrix = BilinearInterpolation(updated_matrix, [needed_x, needed_y], step)
            print(f'[{needed_x}, {needed_y}] DONE ', "\r" , end=' ')
            needed_y += 1
        needed_x = needed_x + 1
    # print("\nFINAL RESULT =", updated_matrix)
    # np.save('E:\Python\pooltool\pooltool-main/Bilinear_interpolation/resultof20cm_test.npy', updated_matrix)
    needed_x = 5
    while needed_x <= 99:
        needed_y = 5
        while needed_y <= 203:
            if updated_matrix [needed_x][needed_y] < 0:
                updated_matrix[needed_x][needed_y] = 0
            needed_y += 1
        needed_x = needed_x + 1
    np.save(f'E:\Python\project/allheatmap\eval_interpolated/interpolated_{Cx}_{Cy}.npy', updated_matrix)
    print('\nnpy File Saved')
    ax = plt.axes()
    sns.heatmap(updated_matrix,linewidths=0, cmap='coolwarm', square= True, cbar=True, ax=ax, annot=False)
    plt.savefig(f"E:\Python\project/allheatmap\eval_interpolated/{Cx}_{Cy}.png", dpi = 600)
    plt.close()
    print('Figure Saved\n')
    # plt.show()


x= 20
while x <= 100:
    y = 20
    while y <=200:
        datapath = np.load(f"E:\Python\project/allheatmap/eval_interpolated/original_eval/interpolated_{x}_{y}.npy")
        print(f'Original shape = {np.shape(datapath)}')
        new_datapath = datapath[3:102, 5:203]
        print(f'New shape = {np.shape(new_datapath)}')
        np.save(f'E:\Python\project/allheatmap\eval_interpolated/reshape_{x}_{y}.npy', new_datapath)
        ax = plt.axes()
        sns.heatmap(new_datapath,linewidths=0, cmap='coolwarm', square= True, cbar=True, ax=ax, annot=False)
        plt.savefig(f"E:\Python\project/allheatmap/eval_interpolated/reshape_{x}_{y}.png", dpi = 1200)
        print(x,y,'Saved\n')
        plt.close()
        y += 20
    x += 20


# datapath = np.load(f"E:\Python\project/allheatmap/eval_interpolated/interpolated_20_20.npy")
# print(f'Original shape = {np.shape(datapath)}')

# # 使用切片操作轉換形狀
# new_datapath = datapath[3:102, 5:203]
# print(f'New shape = {np.shape(new_datapath)}')
# ax = plt.axes()
# sns.heatmap(new_datapath,linewidths=0, cmap='coolwarm', square= True, cbar=True, ax=ax, annot=False)
# plt.savefig("E:\Python\project/allheatmap/eval_interpolated/reshape_20_20.png", dpi = 1200)
# plt.show()



