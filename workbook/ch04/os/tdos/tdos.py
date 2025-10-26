# main.py - Pico TDOS Node (NO select, NO USB_VCP)
# Just prints JSON lines + reads from stdin

import ujson
import uasyncio as asyncio
import sys
import time
from micropython import const

# --- Message Types ---
class MessageType:
    SENSOR_READ = const("sensor_read")
    HEARTBEAT   = const("heartbeat")
    ERROR       = const("error")

# --- Message Class ---
class Message:
    __slots__ = ('msg_type', 'payload', 'msg_id', 'reply_to', 'ts')

    def __init__(self, msg_type, payload, msg_id=None, reply_to=None):
        self.msg_type  = msg_type
        self.payload   = payload
        self.msg_id    = msg_id or hex(time.ticks_us() & 0xFFFFFF)[2:]
        self.reply_to  = reply_to
        self.ts        = time.ticks_ms()

    def to_json(self):
        data = {"t": self.msg_type, "p": self.payload, "id": self.msg_id, "ts": self.ts}
        if self.reply_to:
            data["r"] = self.reply_to
        return ujson.dumps(data)

    @classmethod
    def from_json(cls, text):
        try:
            d = ujson.loads(text)
            return cls(d["t"], d["p"], d.get("id"), d.get("r"))
        except:
            return None

# --- Pico Node ---
class PicoNode:
    def __init__(self, name="pico-node", sensor_pin=4):
        self.name = name
        self.pin = machine.Pin(sensor_pin, machine.Pin.IN) if sensor_pin else None
        self.running = True
        self.buffer = ""

    def _read_sensor(self):
        return self.pin.value() if self.pin else (time.ticks_ms() // 1000) % 100

    async def _heartbeat(self):
        while self.running:
            msg = Message(
                msg_type=MessageType.HEARTBEAT,
                payload={"name": self.name, "up": time.ticks_ms()}
            )
            print(msg.to_json())
            await asyncio.sleep(5)

    async def _read_serial_input(self):
        self.buffer = ""
        while self.running:
            # Try non-blocking read
            try:
                if hasattr(sys.stdin, 'buffer'):
                    if sys.stdin.buffer in select.select([sys.stdin.buffer], [], [], 0)[0]:
                        byte = sys.stdin.buffer.read(1)
                        if byte:
                            char = byte.decode('utf-8', 'ignore')
                            if char in '\n\r':
                                if self.buffer.strip():
                                    self._handle_input(self.buffer)
                                self.buffer = ""
                            else:
                                self.buffer += char
                else:
                    # Fallback to input()
                    line = input().strip()
                    if line:
                        self._handle_input(line)
            except:
                # Fallback: use input() every 100ms
                try:
                    line = input().strip()
                    if line:
                        self._handle_input(line)
                except:
                    pass
            await asyncio.sleep_ms(10)

    def _handle_input(self, text):
        msg = Message.from_json(text)
        if msg and msg.msg_type == MessageType.SENSOR_READ:
            value = self._read_sensor()
            resp = Message(
                msg_type=MessageType.SENSOR_READ,
                payload={"value": value, "unit": "raw"},
                reply_to=msg.msg_id
            )
            print(resp.to_json())

    async def run(self):
        print("Pico TDOS Node READY – send JSON lines to request")
        await asyncio.gather(
            self._heartbeat(),
            self._read_serial_input()
        )

# --- MAIN ---
def main():
    import machine
    node = PicoNode(sensor_pin=4)
    try:
        asyncio.run(node.run())
    except KeyboardInterrupt:
        print("\nStopped")

if __name__ == "__main__":
    main()