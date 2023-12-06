import requests
import json

class PrinterIO:
    def __init__(self, ip_address="192.168.1.177", port_number=7125):
        self.ip_address = ip_address
        self.port_number = port_number

    def print_gcode(self, gcode_filename):
        url = f"http://{self.ip_address}:{self.port_number}/printer/print/start"
        payload = {"filename": f"{gcode_filename}"}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code == 200
    
    def get_xyz_position(self):
        url = f"http://{self.ip_address}:{self.port_number}/printer/objects/query"
        payload = {"objects": {"print_stats": None, "toolhead": None}}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()
        x = data['result']['status']['toolhead']['position'][0]
        y = data['result']['status']['toolhead']['position'][1]
        z = data['result']['status']['toolhead']['position'][2]
        return x, y, z
    
    def set_xyz_position(self, x, y, z):
        url = f"http://{self.ip_address}:{self.port_number}/printer/gcode/script"
        gcode = f"G1 X{x} Y{y} Z{z}"
        payload = {"script": gcode}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code == 200
    
    def set_xy_position(self, x, y):
        url = f"http://{self.ip_address}:{self.port_number}/printer/gcode/script"
        gcode = f"G1 X{x} Y{y}"
        payload = {"script": gcode}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code == 200