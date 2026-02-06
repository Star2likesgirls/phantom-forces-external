import ctypes
import struct
from ctypes import wintypes
from .offsets import Offsets

# Windows API constants
PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_QUERY_INFORMATION = 0x0400

# Load Windows DLLs
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi
user32 = ctypes.windll.user32


class Process:
    @staticmethod
    def get_pid(process_name):
        """Get process ID by name."""
        import subprocess
        try:
            # Use tasklist to find the process
            output = subprocess.check_output(
                f'tasklist /FI "IMAGENAME eq {process_name}*" /FO CSV /NH',
                shell=True, stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='ignore')
            
            for line in output.strip().split('\n'):
                if line and process_name.lower() in line.lower():
                    parts = line.replace('"', '').split(',')
                    if len(parts) >= 2:
                        return int(parts[1])
        except:
            pass
        
        # Fallback: enumerate all processes
        try:
            process_ids = (wintypes.DWORD * 1024)()
            bytes_returned = wintypes.DWORD()
            
            if psapi.EnumProcesses(ctypes.byref(process_ids), ctypes.sizeof(process_ids), ctypes.byref(bytes_returned)):
                num_processes = bytes_returned.value // ctypes.sizeof(wintypes.DWORD)
                
                for i in range(num_processes):
                    pid = process_ids[i]
                    if pid == 0:
                        continue
                    
                    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
                    if handle:
                        try:
                            name_buffer = (ctypes.c_char * 260)()
                            if psapi.GetModuleBaseNameA(handle, None, name_buffer, 260):
                                name = name_buffer.value.decode('utf-8', errors='ignore')
                                if process_name.lower() in name.lower():
                                    kernel32.CloseHandle(handle)
                                    return pid
                        finally:
                            kernel32.CloseHandle(handle)
        except:
            pass
        
        return None
    
    @staticmethod
    def get_module_base(handle):
        """Get the base address of the main module."""
        try:
            modules = (ctypes.c_void_p * 1024)()
            bytes_needed = wintypes.DWORD()
            
            if psapi.EnumProcessModulesEx(handle, ctypes.byref(modules), ctypes.sizeof(modules), ctypes.byref(bytes_needed), 0x03):
                return modules[0]
        except:
            pass
        return 0


class Memory:
    def __init__(self, pid):
        self.pid = pid
        self.handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not self.handle:
            raise Exception(f"Failed to open process {pid}")
    
    def read_bytes(self, address, size):
        """Read raw bytes from memory."""
        buffer = (ctypes.c_char * size)()
        bytes_read = ctypes.c_size_t()
        
        if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(address), buffer, size, ctypes.byref(bytes_read)):
            return bytes(buffer)
        return None
    
    def read_ptr(self, address):
        """Read a 64-bit pointer."""
        data = self.read_bytes(address, 8)
        if data:
            return struct.unpack('<Q', data)[0]
        return 0
    
    def read_int(self, address):
        """Read a 32-bit integer."""
        data = self.read_bytes(address, 4)
        if data:
            return struct.unpack('<i', data)[0]
        return 0
    
    def read_uint(self, address):
        """Read an unsigned 32-bit integer."""
        data = self.read_bytes(address, 4)
        if data:
            return struct.unpack('<I', data)[0]
        return 0
    
    def read_float(self, address):
        """Read a 32-bit float."""
        data = self.read_bytes(address, 4)
        if data:
            return struct.unpack('<f', data)[0]
        return 0.0
    
    def read_double(self, address):
        """Read a 64-bit double."""
        data = self.read_bytes(address, 8)
        if data:
            return struct.unpack('<d', data)[0]
        return 0.0
    
    def read_vector3(self, address):
        """Read a Vector3 (3 floats)."""
        data = self.read_bytes(address, 12)
        if data:
            return struct.unpack('<fff', data)
        return (0.0, 0.0, 0.0)
    
    def read_string(self, address, max_length=256):
        """Read a null-terminated string."""
        data = self.read_bytes(address, max_length)
        if data:
            try:
                null_idx = data.index(b'\x00')
                return data[:null_idx].decode('utf-8', errors='ignore')
            except ValueError:
                return data.decode('utf-8', errors='ignore')
        return ""
    
    def read_roblox_string(self, address):
        """Read a Roblox string (pointer to string data)."""
        ptr = self.read_ptr(address)
        if ptr:
            return self.read_string(ptr)
        return ""
    
    def read_matrix4x4(self, address):
        """Read a 4x4 matrix (16 floats)."""
        data = self.read_bytes(address, 64)
        if data:
            return list(struct.unpack('<16f', data))
        return [0.0] * 16
    
    def close(self):
        """Close the process handle."""
        if self.handle:
            kernel32.CloseHandle(self.handle)
            self.handle = None


class Instance:
    def __init__(self, address, mem):
        self.address = address
        self.mem = mem
    
    def is_valid(self):
        """Check if this instance is valid."""
        return self.address != 0
    
    def get_name(self):
        """Get the name of this instance."""
        if not self.is_valid():
            return None
        return self.mem.read_roblox_string(self.address + Offsets.name)
    
    def get_children(self):
        """Get all children of this instance."""
        children = []
        if not self.is_valid():
            return children
        
        children_ptr = self.mem.read_ptr(self.address + Offsets.children)
        if children_ptr == 0:
            return children
        
        start = self.mem.read_ptr(children_ptr)
        end = self.mem.read_ptr(children_ptr + Offsets.childrenend)
        
        for ptr in range(start, end, 0x10):
            child_ptr = self.mem.read_ptr(ptr)
            if child_ptr != 0:
                children.append(Instance(child_ptr, self.mem))
        
        return children
    
    def find_first_child(self, name):
        """Find the first child with the given name."""
        for child in self.get_children():
            if child.get_name() == name:
                return child
        return Instance(0, self.mem)
    
    def get_character(self):
        """Get the character model (for Player instances)."""
        if not self.is_valid():
            return Instance(0, self.mem)
        
        # Try to find Character child
        for child in self.get_children():
            child_name = child.get_name()
            if child_name and child_name not in ['Backpack', 'PlayerGui', 'PlayerScripts', 'StarterGear']:
                # Check if it has a Humanoid (indicating it's a character)
                humanoid = child.find_first_child('Humanoid')
                if humanoid.is_valid():
                    return child
        
        return Instance(0, self.mem)


class DataModel:
    def __init__(self, base, mem):
        self.base = base
        self.mem = mem
        self._dm_address = None
    
    def get_dm_address(self):
        """Get the DataModel address."""
        if self._dm_address:
            return self._dm_address
        
        fake_dm_ptr = self.mem.read_ptr(self.base + Offsets.fakedmptr)
        if fake_dm_ptr:
            self._dm_address = self.mem.read_ptr(fake_dm_ptr + Offsets.fakedmtodm)
        return self._dm_address or 0
    
    def get_name(self):
        """Get the name of the DataModel (indicates game state)."""
        dm = self.get_dm_address()
        if dm:
            return self.mem.read_roblox_string(dm + Offsets.name)
        return None
    
    def get_workspace(self):
        """Get the Workspace instance."""
        dm = self.get_dm_address()
        if dm:
            workspace_ptr = self.mem.read_ptr(dm + Offsets.workspace)
            return Instance(workspace_ptr, self.mem)
        return Instance(0, self.mem)
    
    def get_place_id(self):
        """Get the current place ID."""
        dm = self.get_dm_address()
        if dm:
            return self.mem.read_int(dm + Offsets.place_id)
        return 0
    
    def get_players_service(self):
        """Get the Players service."""
        workspace = self.get_workspace()
        if workspace.is_valid():
            # Players is a sibling of Workspace in DataModel
            dm = self.get_dm_address()
            if dm:
                dm_instance = Instance(dm, self.mem)
                return dm_instance.find_first_child("Players")
        return Instance(0, self.mem)
    
    def get_local_player(self):
        """Get the local player."""
        players = self.get_players_service()
        if players.is_valid():
            local_ptr = self.mem.read_ptr(players.address + Offsets.localplayer)
            return Instance(local_ptr, self.mem)
        return Instance(0, self.mem)


class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def world_to_screen(self, world_pos, view_matrix):
        """Convert world coordinates to screen coordinates."""
        if not view_matrix or len(view_matrix) < 16:
            return None
        
        x, y, z = world_pos
        
        # Apply view-projection matrix (Row-Major)
        clip_x = view_matrix[0] * x + view_matrix[1] * y + view_matrix[2] * z + view_matrix[3]
        clip_y = view_matrix[4] * x + view_matrix[5] * y + view_matrix[6] * z + view_matrix[7]
        clip_w = view_matrix[12] * x + view_matrix[13] * y + view_matrix[14] * z + view_matrix[15]
        
        # Check if behind camera
        if clip_w < 0.1:
            return None
        
        # Perspective divide
        ndc_x = clip_x / clip_w
        ndc_y = clip_y / clip_w
        
        # Convert to screen coordinates
        screen_x = (1.0 + ndc_x) * 0.5 * self.width
        screen_y = (1.0 - ndc_y) * 0.5 * self.height
        
        # Check bounds
        # if 0 <= screen_x <= self.width and 0 <= screen_y <= self.height:
        return (int(screen_x), int(screen_y))
        
        # return None


class RobloxGame:
    def __init__(self, base, mem):
        self.base = base
        self.mem = mem
        self.dm = DataModel(base, mem)
        self.view_matrix = None
        self.local_player = None
    
    def update(self):
        """Update game state (call each frame)."""
        self._update_view_matrix()
        self._update_local_player()
    
    def _update_view_matrix(self):
        """Update the view matrix from the visual engine."""
        try:
            visual_engine = self.mem.read_ptr(self.base + Offsets.visual_engine_base)
            if visual_engine:
                for offset in Offsets.view_matrix_offsets:
                    matrix = self.mem.read_matrix4x4(visual_engine + offset)
                    # Validate matrix
                    if any(abs(v) > Offsets.matrix_min and abs(v) < Offsets.matrix_max for v in matrix[:4]):
                        self.view_matrix = matrix
                        return
        except:
            pass
        self.view_matrix = None
    
    def _update_local_player(self):
        """Update the local player reference."""
        self.local_player = self.dm.get_local_player()
