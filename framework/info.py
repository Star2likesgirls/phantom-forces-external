import requests

def get_place_info(place_id):
    """Get information about a Roblox place by its ID."""
    try:
        # Get universe ID from place ID
        response = requests.get(
            f"https://apis.roblox.com/universes/v1/places/{place_id}/universe",
            timeout=10
        )
        if response.status_code != 200:
            return None
        
        universe_id = response.json().get('universeId')
        if not universe_id:
            return None
        
        # Get game details
        response = requests.get(
            f"https://games.roblox.com/v1/games?universeIds={universe_id}",
            timeout=10
        )
        if response.status_code != 200:
            return None
        
        data = response.json().get('data', [])
        if not data:
            return None
        
        game_info = data[0]
        return {
            'name': game_info.get('name', 'Unknown'),
            'place_id': place_id,
            'universe_id': universe_id,
            'description': game_info.get('description', ''),
            'creator': game_info.get('creator', {}).get('name', 'Unknown'),
            'playing': game_info.get('playing', 0),
            'visits': game_info.get('visits', 0)
        }
    except Exception as e:
        print(f"Error getting place info: {e}")
        return None
