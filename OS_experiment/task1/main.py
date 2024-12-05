import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, \
    QTableWidget, QTableWidgetItem, QLabel, QComboBox, QGroupBox, QGridLayout
from PyQt5.QtGui import QFont


class MemoryBlock:
    def __init__(self, size, start=None, block_id=None):
        self.size = size
        self.start = start
        self.process = None
        self.block_id = block_id


class Process:
    def __init__(self, pid, size):
        self.pid = pid
        self.size = size
        self.start = None
        self.status = "未分配"


class MemoryManager:
    def __init__(self, total_memory):
        self.total_memory = total_memory
        self.memory_blocks = [MemoryBlock(total_memory, 0, block_id=1)]
        self.processes = []

    def allocate(self, process, strategy="first_fit"):
        """ Allocate memory for a process using the specified strategy """
        if strategy == "first_fit":
            return self.first_fit(process)
        elif strategy == "best_fit":
            return self.best_fit(process)
        elif strategy == "worst_fit":
            return self.worst_fit(process)

    def first_fit(self, process):
        self.memory_blocks.sort(key=lambda block: block.start)
        for block in self.memory_blocks:
            if block.process is None and block.size >= process.size:
                block.process = process
                block.size -= process.size
                if block.size > 0:
                    new_block = MemoryBlock(block.size, block.start + process.size,
                                            block_id=len(self.memory_blocks) + 1)
                    self.memory_blocks.append(new_block)
                process.start = block.start
                process.status = "已分配"
                self.cleanup_memory()
                return block.start
        print("未找到足够的空闲区来分配进程")
        self.cleanup_memory()
        return None

    def best_fit(self, process):
        self.memory_blocks.sort(key=lambda block: block.start)
        free_blocks = [block for block in self.memory_blocks if block.process is None]
        free_blocks.sort(key=lambda block: block.size)
        best_block = None
        for block in free_blocks:
            if block.size >= process.size:
                best_block = block
                break
        if best_block:
            best_block.process = process
            best_block.size -= process.size
            if best_block.size > 0:
                new_block = MemoryBlock(best_block.size, best_block.start + process.size,
                                        block_id=len(self.memory_blocks) + 1)
                self.memory_blocks.append(new_block)
            process.start = best_block.start
            process.status = "已分配"
            self.cleanup_memory()
            return best_block.start
        print("未找到足够的空闲区来分配进程")
        self.cleanup_memory()
        return None

    def cleanup_memory(self):
        self.memory_blocks = [block for block in self.memory_blocks if block.size > 0 or block.process is not None]

    def worst_fit(self, process):
        self.memory_blocks.sort(key=lambda block: block.start)
        worst_block = None
        for block in self.memory_blocks:
            if block.process is None and block.size >= process.size:
                if worst_block is None or block.size > worst_block.size:
                    worst_block = block
        if worst_block:
            worst_block.process = process
            worst_block.size -= process.size
            if worst_block.size > 0:
                new_block = MemoryBlock(worst_block.size, worst_block.start + process.size,
                                        block_id=len(self.memory_blocks) + 1)
                self.memory_blocks.append(new_block)
            process.start = worst_block.start
            process.status = "已分配"
            self.cleanup_memory()
            return worst_block.start
        print("未找到足够的空闲区来分配进程")
        self.cleanup_memory()
        return None

    def merge_free_blocks(self):
        """ 合并相邻的空闲内存块并重新分配 block_id """
        self.memory_blocks.sort(key=lambda block: block.start)  # 按照内存块的起始地址排序
        i = 0
        while i < len(self.memory_blocks) - 1:
            current = self.memory_blocks[i]
            next_block = self.memory_blocks[i + 1]

            # 如果相邻两个内存块都是空闲区，则进行合并
            if current.process is None and next_block.process is None:
                current.size += next_block.size  # 合并两个空闲块
                del self.memory_blocks[i + 1]  # 删除合并后的第二个空闲块
            else:
                i += 1  # 如果当前块不是空闲或者下一个块不是空闲，则不合并，继续检查下一个块

        # 更新合并后每个内存块的 block_id
        for idx, block in enumerate(self.memory_blocks):
            block.block_id = idx + 1

    def get_memory_state(self):
        """ 获取当前内存状态 """
        state = []
        self.memory_blocks.sort(key=lambda block: block.start)
        for block in self.memory_blocks:
            if block.process:
                state.append({
                    "block_id": block.block_id,
                    "start": block.start,
                    "size": block.process.size,
                    "process": block.process.pid,  # 进程编号
                    "status": block.process.status  # 进程状态
                })
            else:
                state.append({
                    "block_id": block.block_id,
                    "start": block.start,
                    "size": block.size,
                    "process": "空闲",  # 空闲区
                    "status": "空闲"  # 空闲区状态
                })
        return state

    def free_memory(self, block_id):
        """ Free memory block based on its block_id and merge adjacent free blocks """
        for block in self.memory_blocks:
            if block.block_id == block_id:
                if block.process is None:
                    print(f"内存块 {block_id} 已经是空闲状态，无法重复回收")
                    return False

                block.size = block.process.size
                block.process = None

                self.merge_free_blocks()
                print(f"成功回收内存块 {block_id}")
                return True

        print(f"没有找到内存块编号为 {block_id} 的块")
        return False


class MemoryManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('内存分配模拟系统')
        self.setGeometry(200, 100, 900, 600)
        self.setMinimumWidth(1000)
        self.setMinimumHeight(1200)

        self.memory_manager = None
        self.processes = []  # 存储进程对象
        self.pid_counter = 1  # 进程编号从1开始自增
        self.released_pid = []  # 存储已回收的进程pid

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        large_font = QFont("Arial", 12)

        input_group = QGroupBox("内存与进程配置")
        input_layout = QVBoxLayout()

        self.label = QLabel('请输入内存总大小和进程需求')
        self.label.setFont(large_font)
        input_layout.addWidget(self.label)

        self.memory_size_input = QLineEdit(self)
        self.memory_size_input.setPlaceholderText("请输入内存总大小")
        self.memory_size_input.setFont(large_font)
        input_layout.addWidget(self.memory_size_input)

        self.process_count_input = QLineEdit(self)
        self.process_count_input.setPlaceholderText("请输入进程个数")
        self.process_count_input.setFont(large_font)
        input_layout.addWidget(self.process_count_input)

        self.process_sizes_input = QLineEdit(self)
        self.process_sizes_input.setPlaceholderText("输入每个进程的内存需求（逗号分隔）")
        self.process_sizes_input.setFont(large_font)
        input_layout.addWidget(self.process_sizes_input)

        self.allocate_button = QPushButton('分配内存', self)
        self.allocate_button.setFont(large_font)
        self.allocate_button.clicked.connect(self.allocate_memory)
        input_layout.addWidget(self.allocate_button)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        operation_group = QGroupBox("操作")
        operation_layout = QGridLayout()

        self.free_pid_label = QLabel("回收内存块编号:")
        self.free_pid_label.setFont(large_font)
        self.free_pid_input = QLineEdit(self)
        self.free_pid_input.setPlaceholderText("输入内存块编号")
        self.free_pid_input.setFont(large_font)

        self.new_process_label = QLabel("新增进程内存需求:")
        self.new_process_label.setFont(large_font)
        self.new_process_sizes_input = QLineEdit(self)
        self.new_process_sizes_input.setPlaceholderText("输入新进程的内存需求（逗号分隔）")
        self.new_process_sizes_input.setFont(large_font)

        self.strategy_label = QLabel("选择分配策略:")
        self.strategy_label.setFont(large_font)
        self.strategy_combo = QComboBox(self)
        self.strategy_combo.setFont(large_font)
        self.strategy_combo.addItems(["first_fit", "best_fit", "worst_fit"])

        self.free_button = QPushButton('回收内存', self)
        self.free_button.setFont(large_font)
        self.free_button.clicked.connect(self.free_memory)

        self.add_process_button = QPushButton('新增进程', self)
        self.add_process_button.setFont(large_font)
        self.add_process_button.clicked.connect(self.add_processes)

        operation_layout.addWidget(self.free_pid_label, 0, 0)
        operation_layout.addWidget(self.free_pid_input, 0, 1)
        operation_layout.addWidget(self.free_button, 0, 2)

        operation_layout.addWidget(self.new_process_label, 1, 0)
        operation_layout.addWidget(self.new_process_sizes_input, 1, 1)
        operation_layout.addWidget(self.add_process_button, 1, 2)

        operation_layout.addWidget(self.strategy_label, 2, 0)
        operation_layout.addWidget(self.strategy_combo, 2, 1)

        operation_group.setLayout(operation_layout)
        main_layout.addWidget(operation_group)

        self.memory_table = QTableWidget(self)
        self.memory_table.setColumnCount(4)
        self.memory_table.setHorizontalHeaderLabels(["编号", "内存起始地址", "内存大小", "分配状态"])
        self.memory_table.setFont(large_font)
        main_layout.addWidget(self.memory_table)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        screen_geometry = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        self.move((screen_geometry.width() - window_geometry.width()) // 2,
                  (screen_geometry.height() - window_geometry.height()) // 2)

    def allocate_memory(self):
        try:
            total_memory = int(self.memory_size_input.text())
            process_count = int(self.process_count_input.text())
            process_sizes = list(map(int, self.process_sizes_input.text().split(',')))

            if len(process_sizes) != process_count:
                raise ValueError("进程个数与内存需求不匹配")
        except ValueError as e:
            print(f"输入错误: {e}")
            return

        total_required_memory = sum(process_sizes)
        if total_required_memory > total_memory:
            print(f"内存不足，无法分配所有进程。总需求: {total_required_memory}, 总内存: {total_memory}")
            return

        self.memory_manager = MemoryManager(total_memory)
        self.processes = [Process(pid=self.get_new_pid(), size=size) for size in process_sizes]

        for process in self.processes:
            strategy = self.strategy_combo.currentText()
            allocation_result = self.memory_manager.allocate(process, strategy)

            if allocation_result is None:
                print(f"进程 {process.size} 无法分配内存，回滚所有进程的分配")
                self.rollback_memory(self.processes)  # 回滚当前新增的进程
                return

        self.update_memory_state()

    def get_new_pid(self):
        # 获取一个新的pid，如果有已回收的pid，则使用它们，否则继续自增
        if self.released_pid:
            return self.released_pid.pop(0)  # 如果有已回收的pid，使用第一个
        else:
            pid = self.pid_counter  # 如果没有回收的pid，则使用当前的pid_counter
            self.pid_counter += 1
            return pid

    def rollback_memory(self, processes_to_rollback):
        """ 仅回滚指定进程的分配 """
        for process in processes_to_rollback:
            if process.start is not None:
                block_id = self.get_block_id_by_process(process)
                if block_id:
                    self.memory_manager.free_memory(block_id)
                    # 回收进程编号
                    self.released_pid.append(process.pid)

        # 清理当前回滚的进程
        self.processes = [p for p in self.processes if p not in processes_to_rollback]  # 确保回滚的进程被移除

    def add_processes(self):
        try:
            # 解析用户输入的新进程内存需求
            new_process_sizes = list(map(int, self.new_process_sizes_input.text().split(',')))

            # 查找当前所有进程中的最大PID，然后加1
            max_pid = max([process.pid for process in self.processes], default=0)  # 如果没有进程，返回0
            new_pid = max_pid + 1  # 新增进程的PID

            total_required_memory = sum(new_process_sizes)
            total_available_memory = sum(
                [block.size for block in self.memory_manager.memory_blocks if block.process is None])

            if total_required_memory > total_available_memory:
                print(
                    f"内存不足，无法为所有进程分配内存。总需求: {total_required_memory}, 总空闲内存: {total_available_memory}")
                return

            new_processes = []
            for size in new_process_sizes:
                new_process = Process(pid=new_pid, size=size)
                strategy = self.strategy_combo.currentText()
                allocation_result = self.memory_manager.allocate(new_process, strategy)

                if allocation_result is None:
                    print(f"进程 {new_pid} 无法分配内存，回滚所有进程的分配")
                    self.rollback_memory(new_processes)  # 仅回滚当前新增的进程
                    return

                self.processes.append(new_process)
                new_processes.append(new_process)  # 记录本次新增的进程
                new_pid += 1  # 递增pid_counter

            self.new_process_sizes_input.clear()

        except ValueError:
            print("请输入有效的内存需求")

        self.update_memory_state()

    def update_memory_state(self):
        # 获取当前内存状态
        memory_state = self.memory_manager.get_memory_state()

        # 更新表格行数
        self.memory_table.setRowCount(len(memory_state))

        for i, block in enumerate(memory_state):
            if block["process"] == "空闲":
                # 如果是空闲区，则进程号列留空
                self.memory_table.setItem(i, 0, QTableWidgetItem("空闲"))  # 进程列显示"空闲"
                self.memory_table.setItem(i, 1, QTableWidgetItem(str(block["start"])))  # 显示内存起始地址
                self.memory_table.setItem(i, 2, QTableWidgetItem(str(block["size"])))  # 显示内存块大小
                self.memory_table.setItem(i, 3, QTableWidgetItem("空闲"))  # 状态列显示"空闲"

            else:
                # 如果是已分配的内存块，显示进程号
                self.memory_table.setItem(i, 0, QTableWidgetItem(str(block["process"])))  # 显示进程编号
                self.memory_table.setItem(i, 1, QTableWidgetItem(str(block["start"])))  # 显示内存起始地址
                self.memory_table.setItem(i, 2, QTableWidgetItem(str(block["size"])))  # 显示内存块大小
                self.memory_table.setItem(i, 3, QTableWidgetItem(str(block["status"])))  # 状态列显示"已分配"


    def get_block_id_by_process(self, process):
        """ Find the block ID for a process based on its start address """
        # 遍历内存块，查找已分配给当前进程的内存块
        for block in self.memory_manager.memory_blocks:
            # 如果内存块已分配给进程，则返回该内存块的ID
            if block.process == process:
                return block.block_id
        return None  # 如果没有找到匹配的内存块，返回None

    def free_memory(self):
        try:
            # 获取用户输入的进程编号
            pid = int(self.free_pid_input.text())

            # 查找对应进程
            process_to_free = None
            for process in self.processes:
                if process.pid == pid:
                    process_to_free = process
                    break

            if not process_to_free:
                print(f"没有找到编号为 {pid} 的进程")
                return

            # 根据进程编号找到对应的内存块，释放内存
            block_id = self.get_block_id_by_process(process_to_free)
            if block_id:
                self.memory_manager.free_memory(block_id)  # 释放内存块

                # 从进程列表中删除该进程
                self.processes = [p for p in self.processes if p.pid != pid]
                print(f"成功回收进程 {pid} 使用的内存块")

            self.update_memory_state()

        except ValueError:
            print("请输入有效的进程编号")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MemoryManagerApp()
    window.show()
    sys.exit(app.exec_())

