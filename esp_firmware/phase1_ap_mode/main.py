import network
import socket
import machine
import time

# --- Network Configuration ---
SSID = "RoboBase_ESP32"
PASSWORD = "robotics123"
UDP_PORT = 12345

# --- Hardware Safety & Pin Definitions (Axle-Split) ---
# 1kHz frequency is optimal for Cytron drivers
freq = 1000 

# Board 1: Front Axle (Safety initialization: duty=0, value=0)
pwm_fl = machine.PWM(machine.Pin(32), freq=freq, duty=0)
dir_fl = machine.Pin(33, machine.Pin.OUT, value=0)
pwm_fr = machine.PWM(machine.Pin(25), freq=freq, duty=0)
dir_fr = machine.Pin(21, machine.Pin.OUT, value=0)

# Board 2: Rear Axle (Safety initialization: duty=0, value=0)
pwm_rl = machine.PWM(machine.Pin(26), freq=freq, duty=0)
dir_rl = machine.Pin(27, machine.Pin.OUT, value=0)
pwm_rr = machine.PWM(machine.Pin(14), freq=freq, duty=0)
dir_rr = machine.Pin(12, machine.Pin.OUT, value=0)

# --- Initialize Wi-Fi Access Point ---
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=SSID, password=PASSWORD)

print("Starting Wi-Fi Access Point...")
while not ap.active():
    time.sleep(0.1)
print(f"AP Active. IP Address: {ap.ifconfig()[0]}")

# --- Initialize UDP Server ---
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(("0.0.0.0", UDP_PORT))
udp.setblocking(False) 
print("UDP Server listening...")

# --- Main Control Loop ---
while True:
    try:
        # Check for incoming wireless data
        data, addr = udp.recvfrom(255)
        msg = data.decode().strip()
        
        # Expected format from your laptop: <L:255,R:-255>
        if msg.startswith("<L:") and ">" in msg:
            core_string = msg[3:].split(">")[0]
            parts = core_string.split(",R:")
            
            if len(parts) == 2:
                left_speed = int(parts[0])
                right_speed = int(parts[1])
                
                # Scale laptop's 8-bit (255) resolution to ESP32's 10-bit (1023) resolution
                left_duty = min(1023, abs(left_speed) * 4)
                left_dir = 1 if left_speed >= 0 else 0
                
                right_duty = min(1023, abs(right_speed) * 4)
                right_dir = 1 if right_speed >= 0 else 0
                
                # --- EXECUTE LEFT WHEELS (Front Left & Rear Left) ---
                dir_fl.value(left_dir)
                dir_rl.value(left_dir)
                pwm_fl.duty(left_duty)
                pwm_rl.duty(left_duty)

                # --- EXECUTE RIGHT WHEELS (Front Right & Rear Right) ---
                dir_fr.value(right_dir)
                dir_rr.value(right_dir)
                pwm_fr.duty(right_duty)
                pwm_rr.duty(right_duty)

    except OSError:
        # No packet received this cycle, keep looping seamlessly
        pass
    except ValueError:
        # Corrupted packet parsing error, ignore and wait for the next frame
        pass