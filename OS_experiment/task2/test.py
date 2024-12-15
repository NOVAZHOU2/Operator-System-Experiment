import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os

# 设置默认字体为 SimHei
rcParams['font.sans-serif'] = ['SimHei']
# 解决负号问题
rcParams['axes.unicode_minus'] = False


def load_sample_data(file_name):
    """
    从文件加载样例数据。
    每一行的格式为：磁头位置,请求1,请求2,...
    """
    sample_data = []
    try:
        with open(file_name, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) > 1:
                    try:
                        head_position = int(parts[0])
                        requests = list(map(int, parts[1:]))
                        sample_data.append((head_position, requests))
                    except ValueError:
                        print(f"格式错误，跳过行: {line.strip()}")
                else:
                    print(f"行格式无效: {line.strip()}")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
    return sample_data


def fcfs(requests, head_position):
    """先来先服务法 (FCFS)"""
    total_movement = 0
    for request in requests:
        total_movement += abs(head_position - request)
        head_position = request
    return total_movement


def sstf(requests, head_position):
    """最短寻道时间优先 (SSTF)"""
    requests = sorted(requests)
    total_movement = 0
    while requests:
        closest_request = min(requests, key=lambda x: abs(x - head_position))
        total_movement += abs(head_position - closest_request)
        head_position = closest_request
        requests.remove(closest_request)
    return total_movement


def scan(requests, head_position, direction="从小到大"):
    """电梯算法 (SCAN)"""
    requests = sorted(requests)
    total_movement = 0
    if direction == "从小到大":
        # 从小到大的电梯算法
        for request in requests:
            if request >= head_position:
                total_movement += abs(head_position - request)
                head_position = request
        total_movement += abs(head_position - requests[0])
        head_position = requests[0]
        for request in requests:
            if request < head_position:
                total_movement += abs(head_position - request)
                head_position = request
    elif direction == "从大到小":
        # 从大到小的电梯算法
        for request in reversed(requests):
            if request <= head_position:
                total_movement += abs(head_position - request)
                head_position = request
        total_movement += abs(head_position - requests[-1])
        head_position = requests[-1]
        for request in reversed(requests):
            if request > head_position:
                total_movement += abs(head_position - request)
                head_position = request
    return total_movement


def calculate_average_movements(sample_data):
    """
    计算三种算法的平均寻道时间。
    """
    fcfs_movements = []
    sstf_movements = []
    scan_movements_asc = []
    scan_movements_desc = []

    for head_position, requests in sample_data:
        fcfs_movements.append(fcfs(requests, head_position))
        sstf_movements.append(sstf(requests, head_position))
        scan_movements_asc.append(scan(requests, head_position, "从小到大"))
        scan_movements_desc.append(scan(requests, head_position, "从大到小"))

    return {
        "先来先服务法": np.mean(fcfs_movements),
        "最短寻道时间优先": np.mean(sstf_movements),
        "电梯算法 (从小到大)": np.mean(scan_movements_asc),
        "电梯算法 (从大到小)": np.mean(scan_movements_desc),
    }


def plot_results(results):
    """
    绘制三种算法的平均寻道时间对比图。
    """
    algorithms = list(results.keys())
    average_movements = list(results.values())

    plt.bar(algorithms, average_movements)
    plt.title("不同算法平均寻道时间对比")
    plt.xlabel("调度算法")
    plt.ylabel("平均寻道时间")
    plt.xticks(rotation=45, ha='right')  # 旋转X轴标签以适应长文字
    plt.tight_layout()  # 自动调整布局
    plt.show()


if __name__ == "__main__":
    # 选择文件路径
    file_path = "C:\\Users\\13620\\PycharmProjects\\OS_experiment\\task2\\large_samples.txt"

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print("文件不存在，请检查路径。")
    else:
        # 加载样本数据
        sample_data = load_sample_data(file_path)

        if not sample_data:
            print("未能加载有效的数据，请检查文件格式。")
        else:
            # 计算平均寻道时间
            results = calculate_average_movements(sample_data)

            # 打印结果
            print("三种算法的平均寻道时间:")
            for algo, avg_movement in results.items():
                print(f"{algo}: {avg_movement:.2f}")

            # 绘制结果图
            plot_results(results)
