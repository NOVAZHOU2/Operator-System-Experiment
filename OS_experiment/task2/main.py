import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, \
    QTextEdit, QDesktopWidget


class DiskSchedulerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('磁盘调度模拟器')
        self.resize(900, 600)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        layout = QVBoxLayout()
        self.head_position_input = QLineEdit(self)
        self.requests_input = QLineEdit(self)
        self.algorithm_selector = QComboBox(self)
        self.algorithm_selector.addItems(['先来先服务法', '最短寻道时间优先', '电梯算法'])
        self.direction_selector = QComboBox(self)
        self.direction_selector.addItems(['从小到大', '从大到小'])
        self.calculate_button = QPushButton('计算', self)
        self.result_display = QTextEdit(self)
        self.result_display.setReadOnly(True)

        # 组织布局
        layout.addWidget(QLabel('初始磁头的位置:'))
        layout.addWidget(self.head_position_input)
        layout.addWidget(QLabel('访问序列（以逗号分隔）:'))
        layout.addWidget(self.requests_input)
        layout.addWidget(QLabel('选择算法:'))
        layout.addWidget(self.algorithm_selector)
        layout.addWidget(QLabel('选择方向（当使用电梯算法时需要指定）:'))
        layout.addWidget(self.direction_selector)
        layout.addWidget(self.calculate_button)
        layout.addWidget(QLabel('运行结果:'))
        layout.addWidget(self.result_display)

        self.setLayout(layout)

        self.calculate_button.clicked.connect(self.calculate_disk_schedule)

        self.setStyleSheet("""
            QLabel { font-size: 30px; }
            QLineEdit { font-size: 30px; }
            QComboBox { font-size: 30px; }
            QPushButton { font-size: 30px; }
            QTextEdit { font-size: 30px; }
        """)

    def calculate_disk_schedule(self):
        head_position = int(self.head_position_input.text())
        requests = list(map(int, self.requests_input.text().split(',')))
        algorithm = self.algorithm_selector.currentText()
        direction = self.direction_selector.currentText()

        if algorithm == '先来先服务法':
            total_movement, access_order = fcfs(requests, head_position)
        elif algorithm == '最短寻道时间优先':
            total_movement, access_order = sstf(requests, head_position)
        elif algorithm == '电梯算法':
            total_movement, access_order = scan(requests, head_position, direction)

        self.result_display.setText(f'总移动长度: {total_movement}\n调度顺序: {access_order}')


def fcfs(requests, head_position):
    total_movement = 0
    access_order = []
    for request in requests:
        total_movement += abs(head_position - request)
        head_position = request
        access_order.append(request)
    return total_movement, access_order


def sstf(requests, head_position):
    requests.sort()
    closest_index = min(range(len(requests)), key=lambda i: abs(requests[i] - head_position))
    total_movement = 0
    current_position = head_position
    access_order = [head_position]

    while requests:
        next_request = requests.pop(closest_index)
        total_movement += abs(next_request - current_position)
        current_position = next_request
        access_order.append(next_request)
        if requests:
            closest_index = min(range(len(requests)), key=lambda i: abs(requests[i] - current_position))

    return total_movement, access_order


def scan(requests, head_position, direction):
    requests.sort()
    access_order = [head_position]
    if direction == "从小到大":
        total_movement = 0
        pos = 0
        for i in range(0,len(requests)):
            if requests[i]<=head_position:
                pos = i
        pos1 = pos
        while pos1 >= 0:
            access_order.append(requests[pos1])
            total_movement += abs(head_position - requests[pos1])
            head_position = requests[pos1]
            pos1 -= 1
        pos+=1
        head_position = requests[0]
        while pos<len(requests):
            access_order.append(requests[pos])
            total_movement += abs(head_position - requests[pos])
            head_position = requests[pos]
            pos+=1
    else:
        total_movement = 0
        pos = 0
        for i in range(0, len(requests)):
            if requests[i] >= head_position:
                pos = i
        pos1 = pos
        while pos1 < len(requests):
            access_order.append(requests[pos1])
            total_movement += abs(head_position - requests[pos1])
            head_position = requests[pos1]
            pos1 += 1
        pos -= 1
        head_position = requests[len(requests)-1]
        while pos >= 0:
            access_order.append(requests[pos])
            total_movement += abs(head_position - requests[pos])
            head_position = requests[pos]
            pos -= 1
    print(total_movement)
    print(access_order)
    return total_movement, access_order


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DiskSchedulerApp()
    ex.show()
    sys.exit(app.exec_())
