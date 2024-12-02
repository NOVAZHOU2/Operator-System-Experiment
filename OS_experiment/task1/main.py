import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, \
    QTableWidget, QTableWidgetItem, QLabel, QComboBox, QGroupBox, QGridLayout
from PyQt5.QtGui import QFont  # Import QFont to change fonts


class MemoryBlock:
    def __init__(self, size, start=None, block_id=None):
        self.size = size  # Memory block size
        self.start = start  # Start address of the memory block
        self.process = None  # Process occupying this block
        self.block_id = block_id  # Unique identifier for the memory block


class Process:
    def __init__(self, pid, size):
        self.pid = pid  # Process ID
        self.size = size  # Memory required by the process
        self.start = None  # Memory start address (None means not allocated)
        self.status = "未分配"  # Allocation status ("未分配" or "已分配")


class MemoryManager:
    def __init__(self, total_memory):
        self.total_memory = total_memory  # Total memory size
        self.memory_blocks = [MemoryBlock(total_memory, 0, block_id=1)]  # One initial large block, starting at 0
        self.processes = []  # List to store processes

    def allocate(self, process, strategy="first_fit"):
        """ Allocate memory for a process using the specified strategy """
        if strategy == "first_fit":
            return self.first_fit(process)
        elif strategy == "best_fit":
            return self.best_fit(process)
        elif strategy == "worst_fit":
            return self.worst_fit(process)

    def first_fit(self, process):
        """ First Fit strategy for memory allocation """
        for block in self.memory_blocks:
            if block.process is None and block.size >= process.size:
                block.process = process
                block.size -= process.size
                new_block = MemoryBlock(block.size, block.start + process.size, block_id=len(self.memory_blocks) + 1)
                self.memory_blocks.append(new_block)
                process.start = block.start
                process.status = "已分配"
                self.cleanup_memory()
                return block.start
        self.cleanup_memory()
        return None

    def best_fit(self, process):
        """ Best Fit strategy for memory allocation """
        best_block = None
        for block in self.memory_blocks:
            if block.process is None and block.size >= process.size:
                if best_block is None or block.size < best_block.size:
                    best_block = block
        if best_block:
            best_block.process = process
            best_block.size -= process.size
            if best_block.size == 0:
                self.memory_blocks.remove(best_block)
            new_block = MemoryBlock(best_block.size, best_block.start + process.size,
                                    block_id=len(self.memory_blocks) + 1)
            self.memory_blocks.append(new_block)
            process.start = best_block.start
            process.status = "已分配"
            self.cleanup_memory()
            return best_block.start
        self.cleanup_memory()
        return None

    def worst_fit(self, process):
        """ Worst Fit strategy for memory allocation """
        worst_block = None
        for block in self.memory_blocks:
            if block.process is None and block.size >= process.size:
                if worst_block is None or block.size > worst_block.size:
                    worst_block = block
        if worst_block:
            worst_block.process = process
            worst_block.size -= process.size
            new_block = MemoryBlock(worst_block.size, worst_block.start + process.size,
                                    block_id=len(self.memory_blocks) + 1)
            self.memory_blocks.append(new_block)
            process.start = worst_block.start
            process.status = "已分配"
            self.cleanup_memory()
            return worst_block.start
        self.cleanup_memory()
        return None

    def cleanup_memory(self):
        """ Remove zero-sized memory blocks """
        # Delete blocks that have size 0 (not allocated or merged blocks)
        self.memory_blocks = [block for block in self.memory_blocks if (block.size > 0 or block.process != None)]

    def free_memory(self, block_id):
        """ Free memory block based on its block_id and merge adjacent free blocks """
        for block in self.memory_blocks:
            if block.block_id == block_id:  # Find the block with the given block_id
                block.size = block.process.size
                block.process = None  # Set the block as free

                # Merge adjacent free blocks
                self.merge_free_blocks()
                return True
        return False

    def merge_free_blocks(self):
        """ Merge adjacent free memory blocks and reassign block_ids """
        self.memory_blocks.sort(key=lambda block: block.start)  # Sort by address
        i = 0
        while i < len(self.memory_blocks) - 1:
            current = self.memory_blocks[i]
            next_block = self.memory_blocks[i + 1]

            # If both blocks are free, merge them
            if current.process is None and next_block.process is None:
                current.size += next_block.size
                del self.memory_blocks[i + 1]  # Remove the merged block
            else:
                i += 1  # Otherwise, continue checking the next block

        # Reassign block_ids after merging
        for idx, block in enumerate(self.memory_blocks):
            block.block_id = idx + 1
    def get_memory_state(self):
        """ Get the current memory state for visualization """
        state = []
        for block in self.memory_blocks:
            if block.process:
                state.append({
                    "block_id": block.block_id,
                    "start": block.start,
                    "size": block.process.size,
                    "process": block.process.pid,
                    "status": block.process.status
                })
            else:
                state.append({
                    "block_id": block.block_id,
                    "start": block.start,
                    "size": block.size,
                    "process": "空闲",
                    "status": "空闲"
                })
        return state


class MemoryManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('内存分配模拟系统')
        self.setGeometry(200, 100, 900, 600)  # Larger initial window size
        self.setMinimumWidth(1000)
        self.setMinimumHeight(800)

        self.memory_manager = None  # Memory Manager instance
        self.processes = []  # List to store process objects

        # Create UI elements
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Create a large font for controls
        large_font = QFont("Arial", 12)  # Increase font size here

        # GroupBox for inputs
        input_group = QGroupBox("内存与进程配置")
        input_layout = QVBoxLayout()

        self.label = QLabel('请输入内存总大小和进程需求')
        self.label.setFont(large_font)  # Set font for label
        input_layout.addWidget(self.label)

        self.memory_size_input = QLineEdit(self)
        self.memory_size_input.setPlaceholderText("请输入内存总大小")
        self.memory_size_input.setFont(large_font)  # Set font for input field
        input_layout.addWidget(self.memory_size_input)

        self.process_count_input = QLineEdit(self)
        self.process_count_input.setPlaceholderText("请输入进程个数")
        self.process_count_input.setFont(large_font)  # Set font for input field
        input_layout.addWidget(self.process_count_input)

        self.process_sizes_input = QLineEdit(self)
        self.process_sizes_input.setPlaceholderText("输入每个进程的内存需求（逗号分隔）")
        self.process_sizes_input.setFont(large_font)  # Set font for input field
        input_layout.addWidget(self.process_sizes_input)

        self.allocate_button = QPushButton('分配内存', self)
        self.allocate_button.setFont(large_font)  # Set font for button
        self.allocate_button.clicked.connect(self.allocate_memory)
        input_layout.addWidget(self.allocate_button)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # GroupBox for operations
        operation_group = QGroupBox("操作")
        operation_layout = QGridLayout()  # Use QGridLayout instead of QHBoxLayout

        # Labels and inputs for operations
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

        # Buttons for operations
        self.free_button = QPushButton('回收内存', self)
        self.free_button.setFont(large_font)  # Set font for button
        self.free_button.clicked.connect(self.free_memory)

        self.add_process_button = QPushButton('新增进程', self)
        self.add_process_button.setFont(large_font)  # Set font for button
        self.add_process_button.clicked.connect(self.add_processes)

        # Add widgets to grid layout
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

        # Table for memory visualization
        self.memory_table = QTableWidget(self)
        self.memory_table.setColumnCount(4)
        self.memory_table.setHorizontalHeaderLabels(["内存块编号", "内存大小", "分配状态", "内存起始地址"])
        self.memory_table.setFont(large_font)  # Set font for table
        main_layout.addWidget(self.memory_table)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Center window on the screen
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
            return  # Invalid input

        self.memory_manager = MemoryManager(total_memory)
        self.processes = [Process(pid=i + 1, size=size) for i, size in enumerate(process_sizes)]

        for process in self.processes:
            strategy = self.strategy_combo.currentText()
            self.memory_manager.allocate(process, strategy)

        self.update_memory_state()

    def free_memory(self):
        try:
            block_id = int(self.free_pid_input.text())  # Get block_id to free
            if self.memory_manager.free_memory(block_id):
                print(f"成功回收内存块 {block_id}")
            else:
                print(f"没有找到内存块编号为 {block_id} 的块")
        except ValueError:
            print("请输入有效的内存块编号")

        self.update_memory_state()

    def add_processes(self):
        try:
            new_process_sizes = list(map(int, self.new_process_sizes_input.text().split(',')))
            new_pid = len(self.processes) + 1  # Assign new process IDs

            for size in new_process_sizes:
                new_process = Process(pid=new_pid, size=size)
                strategy = self.strategy_combo.currentText()
                self.memory_manager.allocate(new_process, strategy)
                self.processes.append(new_process)
                new_pid += 1

            self.new_process_sizes_input.clear()  # Clear input after adding

        except ValueError:
            print("请输入有效的内存需求")

        self.update_memory_state()

    def update_memory_state(self):
        memory_state = self.memory_manager.get_memory_state()
        self.memory_table.setRowCount(len(memory_state))

        for i, block in enumerate(memory_state):
            self.memory_table.setItem(i, 0, QTableWidgetItem(str(block["block_id"])))
            self.memory_table.setItem(i, 1, QTableWidgetItem(str(block["size"])))
            self.memory_table.setItem(i, 2, QTableWidgetItem(str(block["status"])))
            self.memory_table.setItem(i, 3, QTableWidgetItem(str(block["start"])))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MemoryManagerApp()
    window.show()
    sys.exit(app.exec_())