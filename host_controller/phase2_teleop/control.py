import pygame
import socket
import sys

# --- Network Constants ---
ESP32_IP = "172.20.10.14" 
ESP32_PORT = 12345

# --- Initialize Hardware ---
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("[-] Error: No Xbox controller detected!")
    print("    Make sure the controller is turned on and paired before running this script.")
    sys.exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"[+] Connected to controller: {joystick.get_name()}")

# Setup UDP Socket for low-latency transmission
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clock = pygame.time.Clock()

print("[+] System online. Connect your laptop to the 'RoboBase_ESP32' Wi-Fi network.")
print("[+] Use the Left Joystick to drive. Press Ctrl+C in this terminal to terminate.")

try:
    while True:
        # Process Pygame internal events to keep the joystick connection alive
        pygame.event.pump()
        
        # Read standard Xbox Controller mapping:
        # Axis 1 = Left Stick Y (Forward/Backward). Inverted so pushing up is positive.
        # Axis 0 = Left Stick X (Left/Right Steering).
        forward = -joystick.get_axis(1)  
        steering = joystick.get_axis(0)  
        
        # Deadzone filter to stop motors from creeping when sticks are resting
        if abs(forward) < 0.12: forward = 0.0
        if abs(steering) < 0.12: steering = 0.0
        
        # Differential drive kinematic mixing
        left_mix = forward + steering
        right_mix = forward - steering
        
        # Convert raw mixing values (-2.0 to 2.0 range) to standard 8-bit PWM bounds (-255 to 255)
        left_speed = int(left_mix * 255)
        right_speed = int(right_mix * 255)
        
        # Hard limits constraint validation (safety clamp)
        left_speed = max(-255, min(255, left_speed))
        right_speed = max(-255, min(255, right_speed))
        
        # Build payload execution frame
        packet = f"<L:{left_speed},R:{right_speed}>\n"
        
        # Send raw string packet over UDP wireless frame
        sock.sendto(packet.encode(), (ESP32_IP, ESP32_PORT))
        
        # Execute loop at a highly stable 50Hz (every 20ms)
        clock.tick(50)

except KeyboardInterrupt:
    print("\n[-] Shutting down transmission. Sending safe stop frames...")
    # Safe fallback: Ensure robot immediately stops execution on script close
    for _ in range(5):
        sock.sendto(b"<L:0,R:0>\n", (ESP32_IP, ESP32_PORT))
    pygame.quit()
    print("[+] Stopped safely.")
