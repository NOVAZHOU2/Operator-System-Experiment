import random


class MemoryBlock:
    def __init__(self, size, start=None):
        self.size = size  # Memory block size
        self.start = start  # Start address of the memory block
        self.process = None  # Process occupying this block


class MemoryManager:
    def __init__(self, total_memory):
        self.total_memory = total_memory  # Total memory size
        self.memory_blocks = [MemoryBlock(total_memory)]  # One initial large block
        self.processes = []  # List to store allocated processes

    def allocate(self, process_size, strategy="first_fit"):
        """ Allocate memory for a process using the specified strategy """
        if strategy == "first_fit":
            return self.first_fit(process_size)
        elif strategy == "best_fit":
            return self.best_fit(process_size)
        elif strategy == "worst_fit":
            return self.worst_fit(process_size)

    def first_fit(self, process_size):
        """ First Fit strategy for memory allocation """
        for block in self.memory_blocks:
            if block.process is None and block.size >= process_size:
                block.process = process_size
                block.size -= process_size
                new_block = MemoryBlock(block.size, block.start + process_size)
                self.memory_blocks.append(new_block)
                return block.start
        return None

    def best_fit(self, process_size):
        """ Best Fit strategy for memory allocation """
        best_block = None
        for block in self.memory_blocks:
            if block.process is None and block.size >= process_size:
                if best_block is None or block.size < best_block.size:
                    best_block = block
        if best_block:
            best_block.process = process_size
            best_block.size -= process_size
            new_block = MemoryBlock(best_block.size, best_block.start + process_size)
            self.memory_blocks.append(new_block)
            return best_block.start
        return None

    def worst_fit(self, process_size):
        """ Worst Fit strategy for memory allocation """
        worst_block = None
        for block in self.memory_blocks:
            if block.process is None and block.size >= process_size:
                if worst_block is None or block.size > worst_block.size:
                    worst_block = block
        if worst_block:
            worst_block.process = process_size
            worst_block.size -= process_size
            new_block = MemoryBlock(worst_block.size, worst_block.start + process_size)
            self.memory_blocks.append(new_block)
            return worst_block.start
        return None

    def free_memory(self, start_address):
        """ Free memory block of the process starting from the given address """
        for block in self.memory_blocks:
            if block.start == start_address:
                block.process = None
                self.merge_free_blocks()
                return True
        return False

    def merge_free_blocks(self):
        """ Merge adjacent free memory blocks """
        self.memory_blocks.sort(key=lambda block: block.start)
        i = 0
        while i < len(self.memory_blocks) - 1:
            current = self.memory_blocks[i]
            next_block = self.memory_blocks[i + 1]
            if current.process is None and next_block.process is None:
                current.size += next_block.size
                self.memory_blocks.remove(next_block)
            else:
                i += 1

    def get_memory_state(self):
        """ Get the current memory state for visualization """
        state = []
        for block in self.memory_blocks:
            state.append({
                "start": block.start,
                "size": block.size,
                "process": block.process
            })
        return state
