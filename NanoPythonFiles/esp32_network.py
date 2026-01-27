"""
ESP32 Network Connection Module
Handles WiFi connection to ESP32 access point
"""
import subprocess
import time

class ESP32Network:
    def __init__(self, ssid="ESP32_TestNet", password="12345678", ip="192.168.4.1"):
        self.ssid = ssid
        self.password = password
        self.ip = ip
        
    def connect(self):
        """Connect to ESP32 WiFi network"""
        print(f"Connecting to {self.ssid}...")
        
        # Create WiFi profile XML
        profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{self.ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{self.ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{self.password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        
        # Save and add profile
        profile_file = f"{self.ssid}.xml"
        with open(profile_file, "w") as f:
            f.write(profile)
        
        subprocess.run(f'netsh wlan add profile filename="{profile_file}"', 
                      shell=True, capture_output=True)
        time.sleep(1)
        
        # Connect to network
        result = subprocess.run(f'netsh wlan connect name="{self.ssid}"', 
                              shell=True, capture_output=True, text=True)
        
        time.sleep(5)  # Wait for connection to establish
        print(f"Connected to {self.ssid} at {self.ip}")
        return True
    
    def disconnect(self):
        """Disconnect from ESP32 network"""
        subprocess.run(f'netsh wlan disconnect', shell=True)
        print("Disconnected from ESP32")
