# Virtual Memory Simulator (@TheRealSRZ)

PAGE_SIZE = 4  # more PAGE_SIZE means less pages required to cover the same address.
NUM_FRAMES = 4  # number of physical frames, you may increase this to increase physical memory size :)

class Page:
    def __init__(self, page_number, data):
        self.page_number = page_number
        self.data = data  # list of data's in the page
        self.frame_number = None
        self.last_access_time = 0

class VirtualMemorySimulator:
    def __init__(self):
        self.page_table = {}
        self.memory = [None] * NUM_FRAMES  
        self.time = 0  # for LRU replacement
        self.page_faults = 0
        self.total_accesses = 0

    def load_page(self, page_number):
        self.time += 1

        if page_number in self.page_table and self.page_table[page_number].frame_number is not None:
            page = self.page_table[page_number]
            page.last_access_time = self.time
            print(f"[INFO] Page {page_number} is already in memory (Frame {page.frame_number})")
            return page

        self.page_faults += 1
        print(f"[PAGE FAULT] Page {page_number} is not in memory")

        if page_number not in self.page_table:
            data = [page_number * PAGE_SIZE + i for i in range(PAGE_SIZE)]
            self.page_table[page_number] = Page(page_number, data)

        for i in range(NUM_FRAMES):
            if self.memory[i] is None:
                self._load_into_frame(i, page_number)
                return self.page_table[page_number]

        lru_page = min((p for p in self.page_table.values() if p.frame_number is not None),
                       key=lambda p: p.last_access_time)
        print(f"[REPLACEMENT] Replacing page {lru_page.page_number} (LRU) from frame {lru_page.frame_number}")
        self._evict_page(lru_page)
        self._load_into_frame(lru_page.frame_number, page_number)
        return self.page_table[page_number]

    def _load_into_frame(self, frame_number, page_number):
        page = self.page_table[page_number]
        page.frame_number = frame_number
        page.last_access_time = self.time
        self.memory[frame_number] = page
        print(f"[LOAD] Loaded page {page_number} into frame {frame_number}")

    def _evict_page(self, page):
        self.memory[page.frame_number] = None
        page.frame_number = None

    def access(self, virtual_address):
        self.total_accesses += 1
        page_number = virtual_address // PAGE_SIZE
        offset = virtual_address % PAGE_SIZE
        page = self.load_page(page_number)
        value = page.data[offset]
        print(f"[ACCESS] Virtual address {virtual_address} -> Page {page_number}, Offset {offset} = {value}")
        return value

    def write(self, virtual_address, value):
        self.total_accesses += 1
        page_number = virtual_address // PAGE_SIZE
        offset = virtual_address % PAGE_SIZE
        page = self.load_page(page_number)
        old_value = page.data[offset]
        page.data[offset] = value
        print(f"[WRITE] Virtual address {virtual_address} -> Page {page_number}, Offset {offset}: {old_value} -> {value}")

    def display_memory_map(self):
        print("\n=== Memory Map ===")
        for i, page in enumerate(self.memory):
            if page is not None:
                print(f"Frame {i}: Page {page.page_number} | Data: {page.data} | Last Used: {page.last_access_time}")
            else:
                print(f"Frame {i}: Empty")
        print(f"Page Faults: {self.page_faults} / Accesses: {self.total_accesses}")
        print("===================\n")

    def display_page_table(self):
        print("\n=== Page Table ===")
        for page_number, page in sorted(self.page_table.items()):
            frame_info = f"Frame {page.frame_number}" if page.frame_number is not None else "Not in memory"
            print(f"Page {page_number}: {frame_info} | Data: {page.data}")
        print("===================\n")

if __name__ == "__main__":
    vm = VirtualMemorySimulator()
    print("")
    print("=== Virtual Memory Simulator ===")
    print("Commands:")
    print("  read <address>         - Read from virtual address (Decimal Number)")
    print("  write <address> <val>  - Write value to virtual address")
    print("  mem                    - Display memory map")
    print("  table                  - Display page table")
    print("  exit                   - Exit program")
    print("===============================")

    while True:
        cmd = input("vm> ").strip().lower()
        if cmd == "exit":
            break
        elif cmd.startswith("read"):
            try:
                _, addr = cmd.split()
                vm.access(int(addr))
            except:
                print("[ERROR] Usage: read <address>")
        elif cmd.startswith("write"):
            try:
                _, addr, val = cmd.split()
                vm.write(int(addr), int(val))
            except:
                print("[ERROR] Usage: write <address> <value>")
        elif cmd == "mem":
            vm.display_memory_map()
        elif cmd == "table":
            vm.display_page_table()
        else:
            print("[ERROR] Unknown command. Try 'read', 'write', 'mem', 'table', or 'exit'.")