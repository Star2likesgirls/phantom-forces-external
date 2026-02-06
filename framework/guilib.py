import pygame

class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 165, 0)
    ACCENT = (100, 100, 255)
    BG_DARK = (30, 30, 40)
    BG_LIGHT = (50, 50, 60)
    PANEL = (40, 40, 50, 200)


class GUIElement:
    def __init__(self, x, y, label):
        self.x = x
        self.y = y
        self.label = label
        self.height = 25
        self.width = 180
        self.hovered = False
        self.visible = True
    
    def draw(self, screen, font, y_offset):
        pass
    
    def handle_click(self, mx, my, y_offset):
        return False
    
    def handle_release(self):
        pass
    
    def handle_drag(self, mx, my, y_offset):
        pass
    
    def is_hovered(self, mx, my, y_offset):
        return (self.x <= mx <= self.x + self.width and 
                y_offset <= my <= y_offset + self.height)
    
    def check_keybind(self):
        pass


class Toggle(GUIElement):
    def __init__(self, x, y, label, value, callback):
        super().__init__(x, y, label)
        self.value = value
        self.callback = callback
    
    def draw(self, screen, font, y_offset):
        # Background
        bg_color = Colors.BG_LIGHT if self.hovered else Colors.BG_DARK
        pygame.draw.rect(screen, bg_color, (self.x, y_offset, self.width, self.height))
        pygame.draw.rect(screen, Colors.GRAY, (self.x, y_offset, self.width, self.height), 1)
        
        # Label
        text = font.render(self.label, True, Colors.WHITE)
        screen.blit(text, (self.x + 5, y_offset + 5))
        
        # Toggle indicator
        toggle_x = self.x + self.width - 30
        toggle_color = Colors.GREEN if self.value else Colors.RED
        pygame.draw.rect(screen, toggle_color, (toggle_x, y_offset + 5, 20, 15))
    
    def handle_click(self, mx, my, y_offset):
        if self.is_hovered(mx, my, y_offset):
            self.value = not self.value
            self.callback(self.value)
            return True
        return False


class Slider(GUIElement):
    def __init__(self, x, y, label, min_val, max_val, value, callback):
        super().__init__(x, y, label)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.callback = callback
        self.dragging = False
        self.height = 40
    
    def draw(self, screen, font, y_offset):
        # Background
        bg_color = Colors.BG_LIGHT if self.hovered else Colors.BG_DARK
        pygame.draw.rect(screen, bg_color, (self.x, y_offset, self.width, self.height))
        pygame.draw.rect(screen, Colors.GRAY, (self.x, y_offset, self.width, self.height), 1)
        
        # Label and value
        text = font.render(f"{self.label}: {self.value:.1f}", True, Colors.WHITE)
        screen.blit(text, (self.x + 5, y_offset + 3))
        
        # Slider track
        track_y = y_offset + 25
        pygame.draw.rect(screen, Colors.DARK_GRAY, (self.x + 10, track_y, self.width - 20, 6))
        
        # Slider fill
        pct = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_width = int((self.width - 20) * pct)
        pygame.draw.rect(screen, Colors.ACCENT, (self.x + 10, track_y, fill_width, 6))
        
        # Slider handle
        handle_x = self.x + 10 + fill_width - 4
        pygame.draw.rect(screen, Colors.WHITE, (handle_x, track_y - 2, 8, 10))
    
    def handle_click(self, mx, my, y_offset):
        if self.is_hovered(mx, my, y_offset):
            self.dragging = True
            self._update_value(mx)
            return True
        return False
    
    def handle_release(self):
        self.dragging = False
    
    def handle_drag(self, mx, my, y_offset):
        if self.dragging:
            self._update_value(mx)
    
    def _update_value(self, mx):
        pct = (mx - self.x - 10) / (self.width - 20)
        pct = max(0, min(1, pct))
        self.value = self.min_val + pct * (self.max_val - self.min_val)
        self.callback(self.value)


class Dropdown(GUIElement):
    def __init__(self, x, y, label, elements):
        super().__init__(x, y, label)
        self.elements = elements
        self.expanded = False
        self.height = 25
    
    def draw(self, screen, font, y_offset):
        # Header
        bg_color = Colors.BG_LIGHT if self.hovered else Colors.BG_DARK
        pygame.draw.rect(screen, bg_color, (self.x, y_offset, self.width, 25))
        pygame.draw.rect(screen, Colors.GRAY, (self.x, y_offset, self.width, 25), 1)
        
        # Label with arrow
        arrow = "▼" if self.expanded else "►"
        text = font.render(f"{arrow} {self.label}", True, Colors.WHITE)
        screen.blit(text, (self.x + 5, y_offset + 5))
        
        # Draw children if expanded
        if self.expanded:
            child_y = y_offset + 25
            for elem in self.elements:
                elem.draw(screen, font, child_y)
                child_y += elem.height
    
    def get_total_height(self):
        if self.expanded:
            return 25 + sum(e.height for e in self.elements)
        return 25
    
    def handle_click(self, mx, my, y_offset):
        # Check header click
        if self.x <= mx <= self.x + self.width and y_offset <= my <= y_offset + 25:
            self.expanded = not self.expanded
            return True
        
        # Check child clicks
        if self.expanded:
            child_y = y_offset + 25
            for elem in self.elements:
                if elem.handle_click(mx, my, child_y):
                    return True
                child_y += elem.height
        
        return False
    
    def handle_release(self):
        for elem in self.elements:
            elem.handle_release()
    
    def handle_drag(self, mx, my, y_offset):
        if self.expanded:
            child_y = y_offset + 25
            for elem in self.elements:
                elem.handle_drag(mx, my, child_y)
                child_y += elem.height
    
    def update_hover(self, mx, my, y_offset):
        self.hovered = self.x <= mx <= self.x + self.width and y_offset <= my <= y_offset + 25
        
        if self.expanded:
            child_y = y_offset + 25
            for elem in self.elements:
                elem.hovered = elem.is_hovered(mx, my, child_y)
                if hasattr(elem, 'update_hover'):
                    elem.update_hover(mx, my, child_y)
                child_y += elem.height
    
    def check_keybinds(self):
        if self.expanded:
            for elem in self.elements:
                elem.check_keybind()


class Keybind(GUIElement):
    def __init__(self, x, y, label, key, callback):
        super().__init__(x, y, label)
        self.key = key
        self.callback = callback
        self.waiting = False
    
    def draw(self, screen, font, y_offset):
        bg_color = Colors.BG_LIGHT if self.hovered else Colors.BG_DARK
        pygame.draw.rect(screen, bg_color, (self.x, y_offset, self.width, self.height))
        pygame.draw.rect(screen, Colors.GRAY, (self.x, y_offset, self.width, self.height), 1)
        
        if self.waiting:
            text = font.render(f"{self.label}: [...]", True, Colors.YELLOW)
        else:
            key_name = self._get_key_name()
            text = font.render(f"{self.label}: {key_name}", True, Colors.WHITE)
        
        screen.blit(text, (self.x + 5, y_offset + 5))
    
    def _get_key_name(self):
        key_names = {
            0x01: "LMB", 0x02: "RMB", 0x04: "MMB",
            0x05: "X1", 0x06: "X2",
            0x10: "Shift", 0x11: "Ctrl", 0x12: "Alt",
        }
        return key_names.get(self.key, f"0x{self.key:02X}")
    
    def handle_click(self, mx, my, y_offset):
        if self.is_hovered(mx, my, y_offset):
            self.waiting = True
            return True
        return False
    
    def check_keybind(self):
        if self.waiting:
            import win32api
            for key in range(1, 256):
                if key in [0x01]:  # Skip left mouse (used for clicking)
                    continue
                if win32api.GetAsyncKeyState(key) & 0x8000:
                    if key == 0x1B:  # Escape cancels
                        self.waiting = False
                    else:
                        self.key = key
                        self.callback(key)
                        self.waiting = False
                    break


class ColorPicker(GUIElement):
    def __init__(self, x, y, label, color, callback):
        super().__init__(x, y, label)
        self.color = color
        self.callback = callback
        self.expanded = False
        self.height = 25
    
    def draw(self, screen, font, y_offset):
        bg_color = Colors.BG_LIGHT if self.hovered else Colors.BG_DARK
        pygame.draw.rect(screen, bg_color, (self.x, y_offset, self.width, 25))
        pygame.draw.rect(screen, Colors.GRAY, (self.x, y_offset, self.width, 25), 1)
        
        # Label
        text = font.render(self.label, True, Colors.WHITE)
        screen.blit(text, (self.x + 5, y_offset + 5))
        
        # Color preview
        pygame.draw.rect(screen, self.color, (self.x + self.width - 30, y_offset + 5, 20, 15))
        pygame.draw.rect(screen, Colors.WHITE, (self.x + self.width - 30, y_offset + 5, 20, 15), 1)
        
        if self.expanded:
            # Simple color palette
            colors = [
                (255, 0, 0), (0, 255, 0), (0, 0, 255),
                (255, 255, 0), (255, 0, 255), (0, 255, 255),
                (255, 128, 0), (128, 0, 255), (255, 255, 255)
            ]
            
            for i, c in enumerate(colors):
                cx = self.x + 10 + (i % 3) * 30
                cy = y_offset + 30 + (i // 3) * 25
                pygame.draw.rect(screen, c, (cx, cy, 25, 20))
                pygame.draw.rect(screen, Colors.WHITE, (cx, cy, 25, 20), 1)
    
    def get_total_height(self):
        return 25 + (75 if self.expanded else 0)
    
    def handle_click(self, mx, my, y_offset):
        # Header click
        if self.x <= mx <= self.x + self.width and y_offset <= my <= y_offset + 25:
            self.expanded = not self.expanded
            return True
        
        # Color selection
        if self.expanded:
            colors = [
                (255, 0, 0), (0, 255, 0), (0, 0, 255),
                (255, 255, 0), (255, 0, 255), (0, 255, 255),
                (255, 128, 0), (128, 0, 255), (255, 255, 255)
            ]
            
            for i, c in enumerate(colors):
                cx = self.x + 10 + (i % 3) * 30
                cy = y_offset + 30 + (i // 3) * 25
                if cx <= mx <= cx + 25 and cy <= my <= cy + 20:
                    self.color = c
                    self.callback(c)
                    self.expanded = False
                    return True
        
        return False


class Tab:
    def __init__(self, x, y, label, elements):
        self.x = x
        self.y = y
        self.label = label
        self.elements = elements
        self.expanded = True
        self.width = 200
        self.header_height = 30
    
    def draw(self, screen, font):
        # Tab header
        pygame.draw.rect(screen, Colors.BG_DARK, (self.x, self.y, self.width, self.header_height))
        pygame.draw.rect(screen, Colors.ACCENT, (self.x, self.y, self.width, self.header_height), 2)
        
        arrow = "▼" if self.expanded else "►"
        text = font.render(f"{arrow} {self.label}", True, Colors.WHITE)
        screen.blit(text, (self.x + 10, self.y + 8))
        
        if self.expanded:
            current_y = self.y + self.header_height
            for elem in self.elements:
                elem.x = self.x + 10
                elem.draw(screen, font, current_y)
                if hasattr(elem, 'get_total_height'):
                    current_y += elem.get_total_height()
                else:
                    current_y += elem.height
    
    def get_total_height(self):
        if not self.expanded:
            return self.header_height
        
        height = self.header_height
        for elem in self.elements:
            if hasattr(elem, 'get_total_height'):
                height += elem.get_total_height()
            else:
                height += elem.height
        return height
    
    def handle_click(self, mx, my):
        # Header click
        if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.header_height:
            self.expanded = not self.expanded
            return True
        
        if self.expanded:
            current_y = self.y + self.header_height
            for elem in self.elements:
                if hasattr(elem, 'get_total_height'):
                    elem_height = elem.get_total_height()
                else:
                    elem_height = elem.height
                
                if elem.handle_click(mx, my, current_y):
                    return True
                current_y += elem_height
        
        return False
    
    def handle_release(self):
        for elem in self.elements:
            elem.handle_release()
    
    def handle_drag(self, mx, my):
        if self.expanded:
            current_y = self.y + self.header_height
            for elem in self.elements:
                if hasattr(elem, 'get_total_height'):
                    elem_height = elem.get_total_height()
                else:
                    elem_height = elem.height
                
                elem.handle_drag(mx, my, current_y)
                current_y += elem_height
    
    def update_hover(self, mx, my):
        if self.expanded:
            current_y = self.y + self.header_height
            for elem in self.elements:
                if hasattr(elem, 'get_total_height'):
                    elem_height = elem.get_total_height()
                else:
                    elem_height = elem.height
                
                elem.hovered = elem.is_hovered(mx, my, current_y)
                if hasattr(elem, 'update_hover'):
                    elem.update_hover(mx, my, current_y)
                current_y += elem_height
    
    def check_keybinds(self):
        if self.expanded:
            for elem in self.elements:
                elem.check_keybind()
                if hasattr(elem, 'check_keybinds'):
                    elem.check_keybinds()


class GUIManager:
    def __init__(self):
        self.tabs = []
        self.font = None
    
    def add_tab(self, tab):
        self.tabs.append(tab)
    
    def draw_all(self, screen):
        if self.font is None:
            self.font = pygame.font.Font(None, 18)
        
        for tab in self.tabs:
            tab.draw(screen, self.font)
    
    def handle_click(self, mx, my):
        for tab in self.tabs:
            if tab.handle_click(mx, my):
                return True
        return False
    
    def handle_release(self):
        for tab in self.tabs:
            tab.handle_release()
    
    def handle_drag(self, mx, my):
        for tab in self.tabs:
            tab.handle_drag(mx, my)
    
    def update_hover(self, mx, my):
        for tab in self.tabs:
            tab.update_hover(mx, my)
    
    def check_keybinds(self):
        for tab in self.tabs:
            tab.check_keybinds()
