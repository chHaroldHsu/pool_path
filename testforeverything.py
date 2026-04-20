import math

def calculate_vector(point1, point2):
    # 计算两个点之间的向量
    return [point2[0] - point1[0], point2[1] - point1[1]]

def dot_product(vector1, vector2):
    # 计算两个向量的点积
    return vector1[0] * vector2[0] + vector1[1] * vector2[1]

def magnitude(vector):
    # 计算向量的大小
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)

def angle_between_vectors(point1, point2, point3, point4, in_degrees=True):
    # 根据四个位置的坐标计算两个向量的夹角，返回角度值（默认）
    vector1 = calculate_vector(point1, point2)
    vector2 = calculate_vector(point3, point4)
    dot = dot_product(vector1, vector2)
    magnitude_product = magnitude(vector1) * magnitude(vector2)
    angle_rad = math.acos(dot / magnitude_product)
    if in_degrees:
        # 将弧度转换为角度
        print(math.degrees(angle_rad))
        return math.degrees(angle_rad)
    else:
        print(angle_rad)
        return angle_rad