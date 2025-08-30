# Important note: This will overwrite any existing FAT filesystem on your SD card when it formats!

import struct
import utime

class HierarchicalVFS:
    BLOCK_SIZE = 512
    MAGIC_NUMBER = 0x48565653  # "HVFS"
    
    # Entry types
    FILE_TYPE = 1
    DIR_TYPE = 2
    
    def __init__(self, sdcard_obj):
        self.sd = sdcard_obj
        self.current_dir = None
        self.superblock = self._read_superblock()
        if not self.superblock:
            self._format_disk()
        self.current_dir = self.superblock['root_dir_block']
    
    def _read_superblock(self):
        try:
            data = self.sd.read_block(0)
            magic, total_blocks, free_blocks, root_dir = struct.unpack('<IIII', data[:16])
            if magic == self.MAGIC_NUMBER:
                return {
                    'total_blocks': total_blocks,
                    'free_blocks': free_blocks,
                    'root_dir_block': root_dir,
                    'block_bitmap_start': 1
                }
        except:
            pass
        return None
    
    def _format_disk(self):
        print("Formatting Hierarchical VFS...")
        total_blocks = 1000
        
        # Superblock
        superblock = struct.pack('<IIII', self.MAGIC_NUMBER, total_blocks, total_blocks-3, 2)
        self.sd.write_block(0, superblock + b'\x00' * (self.BLOCK_SIZE - 16))
        
        # Block bitmap
        bitmap = bytearray(self.BLOCK_SIZE)
        bitmap[0] = 0x07  # Blocks 0,1,2 used
        self.sd.write_block(1, bitmap)
        
        # Root directory
        self.sd.write_block(2, b'\x00' * self.BLOCK_SIZE)
        
        self.superblock = {
            'total_blocks': total_blocks,
            'free_blocks': total_blocks-3,
            'root_dir_block': 2,
            'block_bitmap_start': 1
        }
    
    def _allocate_block(self):
        bitmap_data = bytearray(self.sd.read_block(1))
        
        for byte_idx, byte_val in enumerate(bitmap_data):
            if byte_val != 0xFF:
                for bit_idx in range(8):
                    if not (byte_val & (1 << bit_idx)):
                        block_num = byte_idx * 8 + bit_idx
                        bitmap_data[byte_idx] |= (1 << bit_idx)
                        self.sd.write_block(1, bitmap_data)
                        return block_num
        return None
    
    def _find_entry(self, name, dir_block=None):
        if dir_block is None:
            dir_block = self.current_dir
            
        dir_data = self.sd.read_block(dir_block)
        
        # Each entry: type(1) + name(27) + block_ptr(4) = 32 bytes
        for i in range(0, self.BLOCK_SIZE, 32):
            if dir_data[i] != 0:
                entry_type = dir_data[i]
                entry_name = dir_data[i+1:i+28].rstrip(b'\x00').decode('utf-8')
                entry_block = struct.unpack('<I', dir_data[i+28:i+32])[0]
                
                if entry_name == name:
                    return {
                        'type': entry_type,
                        'name': entry_name,
                        'block': entry_block,
                        'offset': i
                    }
        return None
    
    def _add_dir_entry(self, name, entry_type, data_block, dir_block=None):
        if dir_block is None:
            dir_block = self.current_dir
            
        dir_data = bytearray(self.sd.read_block(dir_block))
        
        # Find empty slot
        for i in range(0, self.BLOCK_SIZE, 32):
            if dir_data[i] == 0:
                entry = struct.pack('<B', entry_type) + name.encode('utf-8').ljust(27, b'\x00') + struct.pack('<I', data_block)
                dir_data[i:i+32] = entry
                self.sd.write_block(dir_block, dir_data)
                return True
        return False  # Directory full
    
    def create_file(self, filename, data):
        if self._find_entry(filename):
            raise FileExistsError(f"File '{filename}' already exists")
        
        data_block = self._allocate_block()
        if data_block is None:
            raise RuntimeError("Disk full")
        
        # Write file data
        file_data = data[:self.BLOCK_SIZE] + b'\x00' * max(0, self.BLOCK_SIZE - len(data))
        self.sd.write_block(data_block, file_data)
        
        # Add to directory
        if not self._add_dir_entry(filename, self.FILE_TYPE, data_block):
            raise RuntimeError("Directory full")
    
    def create_dir(self, dirname):
        if self._find_entry(dirname):
            raise FileExistsError(f"Directory '{dirname}' already exists")
        
        dir_block = self._allocate_block()
        if dir_block is None:
            raise RuntimeError("Disk full")
        
        # Init empty directory
        self.sd.write_block(dir_block, b'\x00' * self.BLOCK_SIZE)
        
        # Add to current directory
        if not self._add_dir_entry(dirname, self.DIR_TYPE, dir_block):
            raise RuntimeError("Directory full")
    
    def read_file(self, filename):
        entry = self._find_entry(filename)
        if not entry:
            raise FileNotFoundError(f"File '{filename}' not found")
        if entry['type'] != self.FILE_TYPE:
            raise IsADirectoryError(f"'{filename}' is a directory")
        
        data = self.sd.read_block(entry['block'])
        return data.split(b'\x00')[0]
    
    def list_dir(self, path=None):
        dir_block = self.current_dir
        if path:
            entry = self._find_entry(path)
            if not entry or entry['type'] != self.DIR_TYPE:
                raise NotADirectoryError(f"'{path}' is not a directory")
            dir_block = entry['block']
        
        items = []
        dir_data = self.sd.read_block(dir_block)
        
        for i in range(0, self.BLOCK_SIZE, 32):
            if dir_data[i] != 0:
                entry_type = "DIR" if dir_data[i] == self.DIR_TYPE else "FILE"
                entry_name = dir_data[i+1:i+28].rstrip(b'\x00').decode('utf-8')
                items.append({'name': entry_name, 'type': entry_type})
        
        return items
    
    def change_dir(self, dirname):
        if dirname == "..":
            # Simple implementation - you'd need parent pointers for full support
            self.current_dir = self.superblock['root_dir_block']
            return
        
        entry = self._find_entry(dirname)
        if not entry:
            raise FileNotFoundError(f"Directory '{dirname}' not found")
        if entry['type'] != self.DIR_TYPE:
            raise NotADirectoryError(f"'{dirname}' is not a directory")
        
        self.current_dir = entry['block']
    
    def get_current_path(self):
        if self.current_dir == self.superblock['root_dir_block']:
            return "/"
        return "/unknown"  # Would need parent tracking for full paths

# Use with existing setup:
"""
# existing init - NO CHANGES!
import machine, sdcard
import utime, uos

cs = machine.Pin(1, machine.Pin.OUT)
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4))

sd = sdcard.SDCard(spi, cs)

# DON'T mount with uos - we're creating our own filesystem!
# Just pass the sd object directly to our VFS:

vfs = HierarchicalVFS(sd)

# Now use it:
vfs.create_file("readme.txt", b"This is a test file")
vfs.create_dir("documents") 
vfs.create_dir("images")

print("Root contents:", vfs.list_dir())

# Navigate and create files
vfs.change_dir("documents")
vfs.create_file("note.txt", b"A note in documents folder")
vfs.create_file("todo.txt", b"1. Learn VFS\n2. Build filesystem\n3. Expand!")

print("Documents contents:", vfs.list_dir())
print("Note content:", vfs.read_file("note.txt").decode())

# Go back to root  
vfs.change_dir("..")
print("Back to root:", vfs.list_dir())
"""

