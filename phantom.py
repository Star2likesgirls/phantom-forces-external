import math, time, colorsys, pygame, ctypes, win32api, win32con, win32gui, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
from framework.framework import *
from framework.offsets import Offsets
from framework.info import get_place_info
from framework.guilib import GUIManager, Tab, Toggle, Slider, Dropdown, Keybind, Colors, ColorPicker

class Config:
    def __init__(self):
        self.ghost_color = (255, 165, 0)  
        self.phantom_color = (0, 0, 233)  
        self.highlight_color = (0, 0, 255)
        self.show_boxes = False
        self.show_skeleton = True
        self.show_teams = True
        self.show_ghosts = True
        self.show_phantoms = True
        self.show_tracers = True
        self.tracer_from_crosshair = True
        self.rainbow_skeleton = True
        self.rainbow_boxes = True
        self.rainbow_tracers = True
        self.rainbow_speed = 0.1
        self.skeleton_thickness = 2
        self.tracer_thickness = 2
        self.box_thickness = 2
        self.aimbot_enabled = True
        self.aimbot_key = 0x02
        self.aimbot_head_offset = 0.0
        self.smooth_factor = 1
        self.fov_circle = True
        self.fov_size = 130 

class PhantomForces:
    def __init__(self, game):
        self.game = game
        user32 = ctypes.windll.user32
        self.width = user32.GetSystemMetrics(0)
        self.height = user32.GetSystemMetrics(1)
        self.renderer = Renderer(self.width, self.height)
        self.config = Config()
        
        self.gui_visible = False
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
        self.hwnd = pygame.display.get_wm_info()["window"]
        self.update_window_style()
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 18)
        
        self.gui = GUIManager()
        self.build_gui()
    
    def update_window_style(self):
        style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        style = style & ~win32con.WS_EX_TRANSPARENT if self.gui_visible else style | win32con.WS_EX_TRANSPARENT
        style = style | win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, style)
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 255, win32con.LWA_COLORKEY)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def build_gui(self):
        x_start = 300
        y = 300
        x_spacing = 230  
        
        x = x_start
        combat_elements = [
            Toggle(x, y, "Aimbot", self.config.aimbot_enabled,
                          lambda v: setattr(self.config, 'aimbot_enabled', v)),
        ]
        
        aimbot_settings = [
            Keybind(x, y, "Aimbot Key", self.config.aimbot_key,
                           lambda k: setattr(self.config, 'aimbot_key', k)),
            Slider(x, y, "Head Offset", -1.0, 3.0, self.config.aimbot_head_offset,
                          lambda v: setattr(self.config, 'aimbot_head_offset', v)),
            Slider(x, y, "Smoothing", 1.0, 10.0, self.config.smooth_factor,
                          lambda v: setattr(self.config, 'smooth_factor', v)),
            Slider(x, y, "FOV Size", 25, 500, self.config.fov_size,
                          lambda v: setattr(self.config, 'fov_size', v)),
            Toggle(x, y, "FOV Circle", self.config.fov_circle,
                          lambda v: setattr(self.config, 'fov_circle', v)),
            ColorPicker(x, y, "Highlight Color", self.config.highlight_color,
                       lambda c: setattr(self.config, 'highlight_color', c)),
        ]
        
        combat_elements.append(Dropdown(x, y, "Aimbot Settings", aimbot_settings))
        combat_tab = Tab(x, y, "Combat", combat_elements)
        self.gui.add_tab(combat_tab)
        
        x = x_start + x_spacing
        visual_elements = [
            Toggle(x, y, "BoxESP", self.config.show_boxes,
                          lambda v: setattr(self.config, 'show_boxes', v)),
            Toggle(x, y, "Skeleton", self.config.show_skeleton,
                          lambda v: setattr(self.config, 'show_skeleton', v)),
            Toggle(x, y, "Tracers", self.config.show_tracers,
                          lambda v: setattr(self.config, 'show_tracers', v)),
            Toggle(x, y, "NameTags", self.config.show_teams,
                          lambda v: setattr(self.config, 'show_teams', v)),
        ]
        
        rainbow_settings = [
            Toggle(x, y, "Rainbow Skeleton", self.config.rainbow_skeleton,
                          lambda v: setattr(self.config, 'rainbow_skeleton', v)),
            Toggle(x, y, "Rainbow Boxes", self.config.rainbow_boxes,
                          lambda v: setattr(self.config, 'rainbow_boxes', v)),
            Toggle(x, y, "Rainbow Tracers", self.config.rainbow_tracers,
                          lambda v: setattr(self.config, 'rainbow_tracers', v)),
            Slider(x, y, "Speed", 0.1, 2.0, self.config.rainbow_speed,
                          lambda v: setattr(self.config, 'rainbow_speed', v)),
        ]
        
        visual_settings = [
            Slider(x, y, "Skeleton Width", 1, 5, self.config.skeleton_thickness,
                          lambda v: setattr(self.config, 'skeleton_thickness', int(v))),
            Slider(x, y, "Tracer Width", 1, 5, self.config.tracer_thickness,
                          lambda v: setattr(self.config, 'tracer_thickness', int(v))),
            Slider(x, y, "Box Width", 1, 5, self.config.box_thickness,
                          lambda v: setattr(self.config, 'box_thickness', int(v))),
        ]
        
        visual_elements.append(Dropdown(x, y, "Rainbow", rainbow_settings))
        visual_elements.append(Dropdown(x, y, "Thickness", visual_settings))

        tracer_settings = [
            Toggle(x, y, "From Crosshair", self.config.tracer_from_crosshair,
                   lambda v: setattr(self.config, 'tracer_from_crosshair', v))
        ]
        visual_elements.append(Dropdown(x, y, "Tracer Settings", tracer_settings))

        visual_tab = Tab(x, y, "Visual", visual_elements)
        self.gui.add_tab(visual_tab)
        
        x = x_start + x_spacing * 2
        player_elements = [
            Toggle(x, y, "Show Ghosts", self.config.show_ghosts,
                          lambda v: setattr(self.config, 'show_ghosts', v)),
            Toggle(x, y, "Show Phantoms", self.config.show_phantoms,
                          lambda v: setattr(self.config, 'show_phantoms', v)),
        ]
        player_tab = Tab(x, y, "Player", player_elements)
        self.gui.add_tab(player_tab)
    
    def get_workspace_players_folder(self):
        try:
            workspace = self.game.dm.get_workspace()
            if not workspace.is_valid(): return None
            players_folder = workspace.find_first_child("Players")
            if not players_folder.is_valid(): return None
            return players_folder
        except:
            return None
    
    def get_all_part_positions(self, character):
        parts = []
        
        try:
            children_ptr = self.game.mem.read_ptr(character.address + Offsets.children)
            if children_ptr == 0:
                return parts
            
            start = self.game.mem.read_ptr(children_ptr)
            end = self.game.mem.read_ptr(children_ptr + Offsets.childrenend)
            
            for ptr in range(start, end, 0x10):
                part_ptr = self.game.mem.read_ptr(ptr)
                if part_ptr == 0:
                    continue
                
                part = Instance(part_ptr, self.game.mem)
                
                try:
                    primitive_ptr = self.game.mem.read_ptr(part.address + Offsets.primitive)
                    if primitive_ptr != 0:
                        position = self.game.mem.read_vector3(primitive_ptr + Offsets.primitive_position)
                        x, y, z = position
                        
                        if abs(x) < Offsets.position_max and abs(y) < Offsets.position_max and abs(z) < Offsets.position_max:
                            if abs(x) > Offsets.position_min or abs(y) > Offsets.position_min or abs(z) > Offsets.position_min:
                                parts.append({
                                    'position': position,
                                    'y': y,
                                    'x': x,
                                    'z': z
                                })
                except:
                    continue
        except:
            pass
        
        return parts
    
    def get_character_data(self, character, is_ghost=False):
        data = type('obj', (object,), {
            'position': None,
            'head_position': None,
            'distance': None,
            'screen_position': None,
            'head_screen_position': None,
            'is_ghost': is_ghost,
            'name': character.get_name() or "Player",
            'skeleton_parts': [],
            'skeleton_connections': []
        })()
        
        all_parts = self.get_all_part_positions(character)
        if not all_parts:
            return data
        
        all_parts.sort(key=lambda p: p['y'], reverse=True)
        
        if len(all_parts) > 0:
            data.head_position = all_parts[0]['position']
        
        if len(all_parts) > 2:
            middle_idx = len(all_parts) // 2
            data.position = all_parts[middle_idx]['position']
        elif len(all_parts) > 0:
            data.position = all_parts[0]['position']
        
        data.skeleton_parts = all_parts
        
        if len(all_parts) > 1:
            connections = []
            for i, part1 in enumerate(all_parts):
                for j, part2 in enumerate(all_parts):
                    if i >= j:
                        continue
                    
                    dx = part1['x'] - part2['x']
                    dy = part1['y'] - part2['y']
                    dz = part1['z'] - part2['z']
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                    
                    if dist < 2.0:
                        connections.append((part1['position'], part2['position']))
            
            data.skeleton_connections = connections
        
        if data.position and self.game.view_matrix:
            data.screen_position = self.renderer.world_to_screen(data.position, self.game.view_matrix)
        
        if data.head_position and self.game.view_matrix:
            data.head_screen_position = self.renderer.world_to_screen(data.head_position, self.game.view_matrix)
        
        if self.game.local_player and data.position:
            try:
                local_char = self.game.local_player.get_character()
                if local_char.is_valid():
                    local_parts = self.get_all_part_positions(local_char)
                    if local_parts:
                        local_pos = local_parts[len(local_parts) // 2]['position']
                        dx = data.position[0] - local_pos[0]
                        dy = data.position[1] - local_pos[1]
                        dz = data.position[2] - local_pos[2]
                        data.distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            except:
                pass
        
        return data
    
    def get_players(self):
        all_players = []
        
        players_folder = self.get_workspace_players_folder()
        if not players_folder or not players_folder.is_valid():
            return all_players
        
        children_ptr = self.game.mem.read_ptr(players_folder.address + Offsets.children)
        if children_ptr == 0:
            return all_players
        
        start = self.game.mem.read_ptr(children_ptr)
        end = self.game.mem.read_ptr(children_ptr + Offsets.childrenend)
        
        team_folders = []
        for ptr in range(start, end, 0x10):
            team_ptr = self.game.mem.read_ptr(ptr)
            if team_ptr != 0:
                team_folders.append(Instance(team_ptr, self.game.mem))
        
        for folder_idx, team_folder in enumerate(team_folders):
            is_ghost = (folder_idx == 0)
            
            if is_ghost and not self.config.show_ghosts:
                continue
            if not is_ghost and not self.config.show_phantoms:
                continue
            
            team_children_ptr = self.game.mem.read_ptr(team_folder.address + Offsets.children)
            if team_children_ptr == 0:
                continue
            
            team_start = self.game.mem.read_ptr(team_children_ptr)
            team_end = self.game.mem.read_ptr(team_children_ptr + Offsets.childrenend)
            
            for char_ptr_addr in range(team_start, team_end, 0x10):
                char_ptr = self.game.mem.read_ptr(char_ptr_addr)
                if char_ptr == 0:
                    continue
                
                character = Instance(char_ptr, self.game.mem)
                player_data = self.get_character_data(character, is_ghost=is_ghost)
                if player_data.screen_position: 
                    all_players.append(player_data)
        
        return all_players
    
    def draw_skeleton(self, player, highlight=False):
        if not self.config.show_skeleton or not player.skeleton_connections:
            return
    
        if highlight:
            color = self.config.highlight_color
        elif self.config.rainbow_skeleton:
            hue = (time.time() * self.config.rainbow_speed * 0.3) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = tuple(int(c * 255) for c in rgb)
        else:
            color = self.config.ghost_color if player.is_ghost else self.config.phantom_color
    
        for pos1, pos2 in player.skeleton_connections:
            screen1 = self.renderer.world_to_screen(pos1, self.game.view_matrix)
            screen2 = self.renderer.world_to_screen(pos2, self.game.view_matrix)
        
            if screen1 and screen2:
                pygame.draw.line(self.screen, (0, 0, 0), screen1, screen2, self.config.skeleton_thickness + 2)
                pygame.draw.line(self.screen, color, screen1, screen2, self.config.skeleton_thickness)
    
    def draw_tracer(self, player, highlight=False):
        if not self.config.show_tracers or not player.screen_position:
            return
    
        if highlight:
            color = self.config.highlight_color
        elif self.config.rainbow_tracers:
            hue = (time.time() * self.config.rainbow_speed * 0.3) % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = tuple(int(c * 255) for c in rgb)
        else:
            color = self.config.ghost_color if player.is_ghost else self.config.phantom_color
    
        if self.config.tracer_from_crosshair:
            start_pos = (self.width // 2, self.height // 2)
        else:
            start_pos = (self.width // 2, self.height)
        end_pos = player.screen_position
    
        pygame.draw.line(self.screen, (0, 0, 0), start_pos, end_pos, self.config.tracer_thickness + 2)
        pygame.draw.line(self.screen, color, start_pos, end_pos, self.config.tracer_thickness)
    
    def draw_player(self, player, highlight=False):
        if not player.screen_position:
            return
    
        x, y = player.screen_position
    
        if highlight:
            base_color = self.config.highlight_color
        else:
            base_color = self.config.ghost_color if player.is_ghost else self.config.phantom_color
    
        self.draw_skeleton(player, highlight)
        self.draw_tracer(player, highlight)
    
        if self.config.show_boxes:
            if self.config.rainbow_boxes and not highlight:
                hue = (time.time() * self.config.rainbow_speed * 0.3) % 1.0
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                c = tuple(int(c * 255) for c in rgb)
                pygame.draw.rect(self.screen, c, (x - 19, y - 30, 38, 60), self.config.box_thickness)
            else:
               pygame.draw.rect(self.screen, base_color, (x - 19, y - 30, 38, 60), self.config.box_thickness)
    
        if self.config.show_teams:
            team_name = "Ghost" if player.is_ghost else "Phantom"
            text = self.font.render(team_name, True, Colors.WHITE)
            self.screen.blit(text, (x - text.get_width() // 2, y - 58))
    
    def get_aimbot_target(self, players):
        cx, cy = self.width // 2, self.height // 2
        closest, min_dist = None, float('inf')
        
        for player in players:
            aim_pos = player.head_screen_position if player.head_screen_position else player.screen_position
            
            if not aim_pos:
                continue
            
            dist = math.sqrt((aim_pos[0] - cx)**2 + (aim_pos[1] - cy)**2)
            if dist < self.config.fov_size and dist < min_dist:
                min_dist, closest = dist, player
        
        return closest
    
    def smooth_aim(self, target):
        cx, cy = win32api.GetCursorPos()

        if target.head_screen_position:
            tx, ty = target.head_screen_position
            if target.head_position and self.game.view_matrix:
                offset_position = (
                target.head_position[0],
                target.head_position[1] + self.config.aimbot_head_offset,
                target.head_position[2]
                )
                offset_screen = self.renderer.world_to_screen(offset_position, self.game.view_matrix)
                if offset_screen:
                    tx, ty = offset_screen
        else:
            tx, ty = target.screen_position

        dx = tx - cx
        dy = ty - cy
    
        dx_smooth = dx / self.config.smooth_factor
        dy_smooth = dy / self.config.smooth_factor
    
        if abs(dx_smooth) > 0.5 or abs(dy_smooth) > 0.5:
            move_x = int(dx_smooth) or (1 if dx_smooth > 0 else -1)
            move_y = int(dy_smooth) or (1 if dy_smooth > 0 else -1)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)
    
    def handle_gui_input(self, event, mouse_down):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            self.gui.handle_click(mx, my)
            return True
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.gui.handle_release()
            return False
        
        if event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            self.gui.handle_drag(mx, my)
        
        return mouse_down
    
    def run(self):
        running, mouse_down = True, False
        print("Press Shift+F To Open GUI.")
        while running:
            name = self.game.dm.get_name()
            #print(name)
            if not name:
                print("Game Closed, Or You Left.")
                sys.exit()
            elif name == "LuaApp":
                print("Please Run When You Have Joined A Game.")
                sys.exit()
            elif name != "Ugc":
                print("Game Closed, Or You Left.")
                sys.exit()
            for event in pygame.event.get():
               # if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                #    running = False
                if self.gui_visible:
                    mouse_down = self.handle_gui_input(event, mouse_down)
            
            if (win32api.GetAsyncKeyState(0x10) & 0x8000) and (win32api.GetAsyncKeyState(0x46) & 0x8000):
                pygame.time.wait(300)
                self.gui_visible = not self.gui_visible
                self.update_window_style()
            
            self.game.update()
            players = self.get_players()
            
            self.screen.fill((0, 0, 0))
            
            for player in players:
                self.draw_player(player)
            
            if self.config.aimbot_enabled and (win32api.GetAsyncKeyState(self.config.aimbot_key) & 0x8000):
                target = self.get_aimbot_target(players)
                if target:
                    self.draw_player(target, highlight=True)
                    self.smooth_aim(target)
            
            if self.config.fov_circle:
                pygame.draw.circle(self.screen, Colors.WHITE, (self.width // 2, self.height // 2), 
                                 int(self.config.fov_size), 1)
            
            if self.gui_visible:
                mx, my = pygame.mouse.get_pos()
                self.gui.update_hover(mx, my)
                self.gui.check_keybinds()
                self.gui.draw_all(self.screen)
            
            pygame.display.flip()
            self.clock.tick(240)
        
        pygame.quit()

if __name__ == "__main__":
    pid = Process.get_pid('Roblox')
    
    if not pid:
        print('Cannot find Roblox.')
        exit()
    
    mem = Memory(pid)
    base = Process.get_module_base(mem.handle)
    game = RobloxGame(base, mem)

    if game.dm.get_name() == "LuaApp":
        print("Please Load Into A Game First.")
        sys.exit()
    
    place_id = game.dm.get_place_id()
    if place_id != 292439477:
        print(f"You Must Be In Phantom Forces.")
        sys.exit()
        
    info = get_place_info(place_id)
    if info:
       print(f"Game Name: {info['name']}")
       print(f"Place ID: {info['place_id']}")
       print(f"Universe ID: {info['universe_id']}")
    else:
      print(f"Couldn't Get Game Info (Place ID: {place_id})")
    

    PhantomForces(game).run()