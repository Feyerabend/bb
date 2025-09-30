"""
Shared protocol for Dogfight multiplayer game
Used by both server and clients

Packet Types:
- CLIENT_INPUT: Button states from client to server
- FULL_STATE: Complete game state (initial sync)
- DELTA_STATE: Incremental updates
- PING/PONG: Connection monitoring
"""

import struct

# Packet type constants
PKT_CLIENT_INPUT = 0x01
PKT_FULL_STATE = 0x02
PKT_DELTA_STATE = 0x03
PKT_PING = 0x04
PKT_PONG = 0x05
PKT_CLIENT_CONNECT = 0x06
PKT_CLIENT_ACK = 0x07

# Game constants (shared between server and clients)
GAME_WIDTH = 100
GAME_HEIGHT = 80

# Direction constants
DIR_N, DIR_NE, DIR_E, DIR_SE = 0, 1, 2, 3
DIR_S, DIR_SW, DIR_W, DIR_NW = 4, 5, 6, 7

DIR_DX = [0, 1, 1, 1, 0, -1, -1, -1]
DIR_DY = [-1, -1, 0, 1, 1, 1, 0, -1]

class ClientInputPacket:
    """
    Client -> Server
    Button states for this frame
    """
    FORMAT = "!BBBBBBxx"  # type, player_id, btn_a, btn_b, btn_x, btn_y, padding
    SIZE = struct.calcsize(FORMAT)
    
    @staticmethod
    def pack(player_id, btn_a, btn_b, btn_x, btn_y):
        return struct.pack(
            ClientInputPacket.FORMAT,
            PKT_CLIENT_INPUT,
            player_id,
            1 if btn_a else 0,
            1 if btn_b else 0,
            1 if btn_x else 0,
            1 if btn_y else 0
        )
    
    @staticmethod
    def unpack(data):
        pkt_type, player_id, btn_a, btn_b, btn_x, btn_y = struct.unpack(
            ClientInputPacket.FORMAT, data[:ClientInputPacket.SIZE]
        )
        return {
            'player_id': player_id,
            'btn_a': bool(btn_a),
            'btn_b': bool(btn_b),
            'btn_x': bool(btn_x),
            'btn_y': bool(btn_y)
        }

class ConnectPacket:
    """
    Client -> Server: Request to join game
    Server -> Client: Acknowledgment with player ID
    """
    FORMAT = "!BB6x"  # type, player_id (0 for request), padding
    SIZE = struct.calcsize(FORMAT)
    
    @staticmethod
    def pack_request():
        return struct.pack(ConnectPacket.FORMAT, PKT_CLIENT_CONNECT, 0)
    
    @staticmethod
    def pack_ack(player_id):
        return struct.pack(ConnectPacket.FORMAT, PKT_CLIENT_ACK, player_id)
    
    @staticmethod
    def unpack(data):
        pkt_type, player_id = struct.unpack(ConnectPacket.FORMAT, data[:ConnectPacket.SIZE])
        return {'type': pkt_type, 'player_id': player_id}

class FullStatePacket:
    """
    Server -> Client
    Complete game state for sync
    """

    # Header: type, seq, p1_alive, p2_alive, game_over, winner
    HEADER_FORMAT = "!BHBBBB"

    # Per player: x, y, dir
    PLAYER_FORMAT = "BBB"

    # Per shot: x, y, dir, range, owner
    SHOT_FORMAT = "BBBBB"
    

    @staticmethod
    def pack(seq, p1_state, p2_state, p1_shots, p2_shots, game_over=False, winner=0):
        """
        Pack full game state
        p1_state/p2_state: dict with x, y, dir, alive
        p1_shots/p2_shots: list of dicts with x, y, dir, range
        """
        # Pack header
        data = struct.pack(
            FullStatePacket.HEADER_FORMAT,
            PKT_FULL_STATE,
            seq,
            1 if p1_state['alive'] else 0,
            1 if p2_state['alive'] else 0,
            1 if game_over else 0,
            winner
        )
        
        # Pack player 1
        data += struct.pack(
            FullStatePacket.PLAYER_FORMAT,
            p1_state['x'],
            p1_state['y'],
            p1_state['dir']
        )
        
        # Pack player 2
        data += struct.pack(
            FullStatePacket.PLAYER_FORMAT,
            p2_state['x'],
            p2_state['y'],
            p2_state['dir']
        )
        
        # Pack shot counts
        data += struct.pack("BB", len(p1_shots), len(p2_shots))
        
        # Pack player 1 shots
        for shot in p1_shots:
            data += struct.pack(
                FullStatePacket.SHOT_FORMAT,
                shot['x'],
                shot['y'],
                shot['dir'],
                shot['range'],
                1  # owner = player 1
            )
        
        # Pack player 2 shots
        for shot in p2_shots:
            data += struct.pack(
                FullStatePacket.SHOT_FORMAT,
                shot['x'],
                shot['y'],
                shot['dir'],
                shot['range'],
                2  # owner = player 2
            )
        
        return data
    
    @staticmethod
    def unpack(data):
        offset = 0
        header_size = struct.calcsize(FullStatePacket.HEADER_FORMAT)
        
        # Unpack header
        pkt_type, seq, p1_alive, p2_alive, game_over, winner = struct.unpack(
            FullStatePacket.HEADER_FORMAT,
            data[offset:offset+header_size]
        )
        offset += header_size
        
        # Unpack player 1
        player_size = struct.calcsize(FullStatePacket.PLAYER_FORMAT)
        p1_x, p1_y, p1_dir = struct.unpack(
            FullStatePacket.PLAYER_FORMAT,
            data[offset:offset+player_size]
        )
        offset += player_size
        
        # Unpack player 2
        p2_x, p2_y, p2_dir = struct.unpack(
            FullStatePacket.PLAYER_FORMAT,
            data[offset:offset+player_size]
        )
        offset += player_size
        
        # Unpack shot counts
        p1_shot_count, p2_shot_count = struct.unpack("BB", data[offset:offset+2])
        offset += 2
        
        # Unpack shots
        shots = []
        shot_size = struct.calcsize(FullStatePacket.SHOT_FORMAT)
        total_shots = p1_shot_count + p2_shot_count
        
        for _ in range(total_shots):
            x, y, dir, range, owner = struct.unpack(
                FullStatePacket.SHOT_FORMAT,
                data[offset:offset+shot_size]
            )
            shots.append({'x': x, 'y': y, 'dir': dir, 'range': range, 'owner': owner})
            offset += shot_size
        
        return {
            'seq': seq,
            'p1': {'x': p1_x, 'y': p1_y, 'dir': p1_dir, 'alive': bool(p1_alive)},
            'p2': {'x': p2_x, 'y': p2_y, 'dir': p2_dir, 'alive': bool(p2_alive)},
            'shots': shots,
            'game_over': bool(game_over),
            'winner': winner
        }

class DeltaStatePacket:
    """
    Server -> Client
    Incremental updates (positions changed, shots added/removed)
    """
    HEADER_FORMAT = "!BHB"  # type, seq, flags
    POSITION_FORMAT = "BBB"  # player_id, x, y (dir sent only if changed)
    SHOT_ADD_FORMAT = "BBBBB"  # x, y, dir, range, owner
    SHOT_REMOVE_FORMAT = "BB"  # x, y (approximate position for identification)
    
    # Flags
    FLAG_P1_POS = 0x01
    FLAG_P2_POS = 0x02
    FLAG_P1_DIR = 0x04
    FLAG_P2_DIR = 0x08
    FLAG_GAME_OVER = 0x10
    
    @staticmethod
    def pack(seq, p1_pos=None, p2_pos=None, shots_added=None, shots_removed=None, game_over=False, winner=0):
        """
        Pack *delta* update
        p1_pos/p2_pos: dict with x, y, dir (optional) or None if no change
        shots_added: list of shot dicts
        shots_removed: list of (x, y) tuples
        """
        flags = 0
        if p1_pos: flags |= DeltaStatePacket.FLAG_P1_POS
        if p2_pos: flags |= DeltaStatePacket.FLAG_P2_POS
        if p1_pos and 'dir' in p1_pos: flags |= DeltaStatePacket.FLAG_P1_DIR
        if p2_pos and 'dir' in p2_pos: flags |= DeltaStatePacket.FLAG_P2_DIR
        if game_over: flags |= DeltaStatePacket.FLAG_GAME_OVER
        
        data = struct.pack(DeltaStatePacket.HEADER_FORMAT, PKT_DELTA_STATE, seq, flags)
        
        # Pack player positions if changed
        if p1_pos:
            data += struct.pack("BB", p1_pos['x'], p1_pos['y'])
            if 'dir' in p1_pos:
                data += struct.pack("B", p1_pos['dir'])
        
        if p2_pos:
            data += struct.pack("BB", p2_pos['x'], p2_pos['y'])
            if 'dir' in p2_pos:
                data += struct.pack("B", p2_pos['dir'])
        
        # Pack game over info if applicable
        if game_over:
            data += struct.pack("B", winner)
        
        # Pack shots added
        shots_added = shots_added or []
        data += struct.pack("B", len(shots_added))
        for shot in shots_added:
            data += struct.pack(
                DeltaStatePacket.SHOT_ADD_FORMAT,
                shot['x'], shot['y'], shot['dir'], shot['range'], shot['owner']
            )
        
        # Pack shots removed (just positions for matching)
        shots_removed = shots_removed or []
        data += struct.pack("B", len(shots_removed))
        for x, y in shots_removed:
            data += struct.pack(DeltaStatePacket.SHOT_REMOVE_FORMAT, x, y)
        
        return data
    
    @staticmethod
    def unpack(data):
        offset = 0
        header_size = struct.calcsize(DeltaStatePacket.HEADER_FORMAT)
        
        pkt_type, seq, flags = struct.unpack(
            DeltaStatePacket.HEADER_FORMAT,
            data[offset:offset+header_size]
        )
        offset += header_size
        
        result = {'seq': seq, 'p1': {}, 'p2': {}, 'shots_added': [], 'shots_removed': []}
        
        # Unpack player 1 position
        if flags & DeltaStatePacket.FLAG_P1_POS:
            x, y = struct.unpack("BB", data[offset:offset+2])
            result['p1']['x'] = x
            result['p1']['y'] = y
            offset += 2
            
            if flags & DeltaStatePacket.FLAG_P1_DIR:
                result['p1']['dir'] = struct.unpack("B", data[offset:offset+1])[0]
                offset += 1
        
        # Unpack player 2 position
        if flags & DeltaStatePacket.FLAG_P2_POS:
            x, y = struct.unpack("BB", data[offset:offset+2])
            result['p2']['x'] = x
            result['p2']['y'] = y
            offset += 2
            
            if flags & DeltaStatePacket.FLAG_P2_DIR:
                result['p2']['dir'] = struct.unpack("B", data[offset:offset+1])[0]
                offset += 1
        
        # Unpack game over
        result['game_over'] = bool(flags & DeltaStatePacket.FLAG_GAME_OVER)
        if result['game_over']:
            result['winner'] = struct.unpack("B", data[offset:offset+1])[0]
            offset += 1
        
        # Unpack shots added
        shot_add_count = struct.unpack("B", data[offset:offset+1])[0]
        offset += 1
        
        shot_size = struct.calcsize(DeltaStatePacket.SHOT_ADD_FORMAT)
        for _ in range(shot_add_count):
            x, y, dir, range, owner = struct.unpack(
                DeltaStatePacket.SHOT_ADD_FORMAT,
                data[offset:offset+shot_size]
            )
            result['shots_added'].append({
                'x': x, 'y': y, 'dir': dir, 'range': range, 'owner': owner
            })
            offset += shot_size
        
        # Unpack shots removed
        shot_remove_count = struct.unpack("B", data[offset:offset+1])[0]
        offset += 1
        
        remove_size = struct.calcsize(DeltaStatePacket.SHOT_REMOVE_FORMAT)
        for _ in range(shot_remove_count):
            x, y = struct.unpack(
                DeltaStatePacket.SHOT_REMOVE_FORMAT,
                data[offset:offset+remove_size]
            )
            result['shots_removed'].append((x, y))
            offset += remove_size
        
        return result

# Simple ping/pong for connection monitoring
class PingPacket:

    FORMAT = "!BxHI"  # type, padding, seq, timestamp
    SIZE = struct.calcsize(FORMAT)
    
    @staticmethod
    def pack(seq, timestamp):
        return struct.pack(PingPacket.FORMAT, PKT_PING, seq, timestamp)
    
    @staticmethod
    def pack_pong(seq, timestamp):
        return struct.pack(PingPacket.FORMAT, PKT_PONG, seq, timestamp)
    
    @staticmethod
    def unpack(data):
        pkt_type, seq, timestamp = struct.unpack(PingPacket.FORMAT, data[:PingPacket.SIZE])
        return {'type': pkt_type, 'seq': seq, 'timestamp': timestamp}

