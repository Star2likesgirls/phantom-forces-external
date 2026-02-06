import requests, json, time

max_retries = 3
retry_delay = 1.5

def getOffsets():
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get("https://imtheo.lol/Offsets/Offsets.json", 
                                  headers={'Content-Type': 'application/json'}, 
                                  timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"Loaded Offsets {data.get('Roblox Version', 'unknown')}")
            return data.get('Offsets', {})
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(retry_delay)
    return {}
_off = getOffsets()

class Offsets:
    position_max = 10000
    position_min = 0.01
    matrix_min = 0.001
    matrix_max = 1e10
    
    fakedmptr = _off.get('FakeDataModel', {}).get('Pointer', 130504488)
    fakedmtodm = _off.get('FakeDataModel', {}).get('RealDataModel', 448)
    name = _off.get('Instance', {}).get('Name', 176)
    children = _off.get('Instance', {}).get('ChildrenStart', 112)
    childrenend = _off.get('Instance', {}).get('ChildrenEnd', 8)
    player_mouse = _off.get('Player', {}).get('Mouse', 3368)
    mouse_position = _off.get('MouseService', {}).get('MousePosition', 236)
    fov = _off.get('Camera', {}).get('FieldOfView', 352)
    camera = _off.get('Workspace', {}).get('CurrentCamera', 1120)
    localplayer = _off.get('Player', {}).get('LocalPlayer', 304)
    team_color = _off.get('Player', {}).get('Team', 656)
    team_color_brickcolor = _off.get('Team', {}).get('BrickColor', 208)
    workspace = _off.get('DataModel', {}).get('Workspace', 376)
    place_id = _off.get('DataModel', {}).get('PlaceId', 408)
    place_version = _off.get('DataModel', {}).get('PlaceVersion', 436)
    user_id = _off.get('Player', {}).get('UserId', 696)
    display_name = _off.get('Player', {}).get('DisplayName', 304)
    primitive = _off.get('BasePart', {}).get('Primitive', 328)
    primitive_cframe = _off.get('BasePart', {}).get('Rotation', 192)
    primitive_position = _off.get('BasePart', {}).get('Position', 228)
    primitive_size = _off.get('BasePart', {}).get('Size', 432)
    visual_engine_base = _off.get('VisualEngine', {}).get('Pointer', 125167824)
    view_matrix_offsets = [_off.get('VisualEngine', {}).get('ViewMatrix', 288)]
    humanoid_health = _off.get('Humanoid', {}).get('Health', 404)
    humanoid_max_health = _off.get('Humanoid', {}).get('MaxHealth', 436)
    humanoid_walkspeed = _off.get('Humanoid', {}).get('Walkspeed', 468)
    humanoid_jumppower = _off.get('Humanoid', {}).get('JumpPower', 432)
    humanoid_jumheight = _off.get('Humanoid', {}).get('JumpHeight', 428)
    humanoid_hipheight = _off.get('Humanoid', {}).get('HipHeight', 416)
    part_primitive_flags = _off.get('BasePart', {}).get('PrimitiveFlags', 430)
    part_anchored_bit = _off.get('PrimitiveFlags', {}).get('Anchored', 2)
    part_cancollide_bit = _off.get('PrimitiveFlags', {}).get('CanCollide', 8)
    part_cantouch_bit = _off.get('PrimitiveFlags', {}).get('CanTouch', 16)
    part_transparency = _off.get('BasePart', {}).get('Transparency', 240)
    part_size = _off.get('BasePart', {}).get('Size', 432)
    model_instance = _off.get('Player', {}).get('ModelInstance', 896)
