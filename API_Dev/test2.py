from collections import deque

# 定义滑动窗口大小
window_size = 5

# 创建一个固定大小的 deque，最大长度为 window_size
data_window = deque(maxlen=window_size)


# 定义一个函数，用于插入新数据并计算当前窗口的平均值
def sliding_average(new_value):
    # 将新值添加到窗口中，旧值会自动被踢掉
    data_window.append(new_value)

    # 计算并返回当前窗口中的平均值
    return sum(data_window) / len(data_window)


# 示例数据流
data_stream = [476, 16, 9882, 11776, 11913, 23, 9562, 11913, 5894, 8394]

# 模拟滑动平均的过程
for data in data_stream:
    avg = sliding_average(data)
    print(f"新数据: {data}, 当前滑动平均: {avg}")
