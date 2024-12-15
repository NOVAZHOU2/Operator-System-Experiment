import random


def generate_large_sample(num_requests, min_value, max_value):
    """
    生成一个大样例数据集。

    :param num_requests: 访问请求的数量
    :param min_value: 请求的最小值
    :param max_value: 请求的最大值
    :return: 一个包含请求序列的元组 (head_position, requests)
    """
    # 随机生成初始磁头位置
    head_position = random.randint(min_value, max_value)

    # 随机生成请求序列
    requests = random.sample(range(min_value, max_value + 1), num_requests)

    return head_position, requests


def save_sample_to_file(filename, num_samples, num_requests, min_value, max_value):
    """
    生成多个样例并保存到文件中。

    :param filename: 输出文件名
    :param num_samples: 需要生成的样例数量
    :param num_requests: 每个样例中的请求数量
    :param min_value: 请求的最小值
    :param max_value: 请求的最大值
    """
    with open(filename, 'w') as file:
        for _ in range(num_samples):
            head_position, requests = generate_large_sample(num_requests, min_value, max_value)
            # 写入初始磁头位置和请求序列
            file.write(f"{head_position},{','.join(map(str, requests))}\n")


if __name__ == "__main__":
    # 设置生成样例的参数
    num_samples = 100  # 生成100个样例
    num_requests = 50  # 每个样例包含50个请求
    min_value = 0  # 请求的最小值
    max_value = 500  # 请求的最大值

    # 生成样例并保存到文件
    save_sample_to_file('large_samples.txt', num_samples, num_requests, min_value, max_value)
    print(f"已生成 {num_samples} 个样例并保存到 'large_samples.txt' 文件中。")
