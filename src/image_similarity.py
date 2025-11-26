import os
import requests
import json
from tqdm import tqdm
import time

# Rotating SerpAPI Keys
SERPAPI_KEYS = [
    "ab6f0a0814c55f6ff9d74ca67f31ce2e5516283edd7c2349fe7d2120611e5d45",
    "3a03c7309259dc503e3ffcf0b274b7b157573a5bad04a06f8a5e16581ba004a6",
    "19ee6937b78ed64f4bd24e24faec255b52c82deb7f04b4e9905499155fa2c7fa",
    "f1a0e78017c417c2de39bb6b00d601cfc931ec66c1b4f7ccc2dcccce742c38da",
    "b9d116b3a340ee26f33fb36e18fe6b39280b13bebf1c1c691bec6054e9da68f1"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

NUM_IMAGES = 20
RETRY_LIMIT = 10
SLEEP_BETWEEN_ATTEMPTS = 1  # seconds
SAVE_DIR = "images"

# List of 200+ industrial products
PRODUCTS = [
    "Industrial Drill Machine", "CNC Milling Machine", "Air Compressor", "Hydraulic Jack", "Electric Motor",
    "Welding Machine", "Vacuum Pump", "Conveyor Belt", "Heat Exchanger", "Ball Bearing",
    "Gearbox", "Inverter Drive", "Power Transformer", "PLC Controller", "Stepper Motor",
    "Servo Motor", "Pneumatic Cylinder", "Hydraulic Pump", "Solenoid Valve", "Rotary Encoder",
    "Proximity Sensor", "Load Cell", "Pressure Transmitter", "Flow Meter", "Temperature Sensor",
    "Level Sensor", "Industrial PC", "HMI Display", "SCADA System", "Industrial Robot",
    "Stepper Driver", "VFD Drive", "Industrial Power Supply", "Limit Switch", "Contactor Relay",
    "Circuit Breaker", "Industrial Plug", "Push Button", "Emergency Stop Switch", "SMPS",
    "DIN Rail", "Cable Gland", "Terminal Block", "Busbar", "Panel Meter",
    "Torque Wrench", "Measuring Caliper", "Industrial Fan", "Cooling Tower", "Industrial Heater",
    "Fume Extractor", "Dust Collector", "Air Filter Regulator", "Oil Skimmer", "Industrial Chiller",
    "Control Panel", "Distribution Board", "Industrial UPS", "Battery Charger", "Solar Inverter",
    "Industrial Light", "LED Flood Light", "Induction Lamp", "High Bay Light", "Panel Light",
    "Wiring Duct", "Cable Tray", "Junction Box", "Flexible Conduit", "Cable Tie",
    "Wire Marker", "Cable Lug", "Ferrule Printing Machine", "Label Printer", "Bar Code Scanner",
    "RFID Reader", "Magnetic Sensor", "Industrial Camera", "Vision Sensor", "Thermal Imager",
    "Ultrasonic Sensor", "Laser Distance Sensor", "Smoke Detector", "Gas Leak Detector", "Fire Alarm System",
    "Access Control System", "Biometric Attendance", "Door Interlock System", "PA System", "Intercom System",
    "Temperature Controller", "Humidity Controller", "Data Logger", "Signal Converter", "Relay Module",
    "IO Module", "Modbus Gateway", "Wireless Transmitter", "Industrial Router", "Ethernet Switch",
    "Fiber Optic Converter", "PoE Switch", "Surge Protector", "Network Cabinet", "Rack Mount Tray",
    "Cooling Fan", "Air Curtain", "Industrial Vacuum Cleaner", "Heavy Duty Trolley", "Scissor Lift Table",
    "Drum Lifter", "Pallet Truck", "Stacker", "Hydraulic Crane", "Goods Lift",
    "Roller Conveyor", "Chain Conveyor", "Slat Conveyor", "Belt Conveyor", "Screw Conveyor",
    "Bucket Elevator", "Z Bucket Elevator", "Inclined Conveyor", "Sorting Conveyor", "Flexible Conveyor",
    "Industrial Burner", "Boiler", "Steam Generator", "Thermic Fluid Heater", "Heat Pump",
    "Cooling Coil", "Evaporator Coil", "Condenser Coil", "AHU Unit", "Air Washer",
    "Dehumidifier", "Humidifier", "Industrial Oven", "Furnace", "Brazing Machine",
    "Spot Welding Machine", "Arc Welding Machine", "TIG Welding Machine", "MIG Welding Machine", "Laser Welding Machine",
    "CNC Lathe Machine", "CNC Router", "CNC Plasma Cutter", "Laser Cutting Machine", "Waterjet Cutting Machine",
    "Surface Grinder", "Tool Grinder", "Bench Grinder", "Drilling Cum Tapping Machine", "Radial Drill Machine",
    "Column Drill Machine", "Multi Spindle Drill Machine", "Slotting Machine", "Shaping Machine", "Horizontal Boring Machine",
    "Vertical Milling Machine", "Horizontal Milling Machine", "Universal Milling Machine", "Gear Hobbing Machine", "Gear Shaping Machine",
    "Broaching Machine", "Press Machine", "Hydraulic Press", "Pneumatic Press", "Mechanical Press",
    "Power Press", "C Type Press", "H Type Press", "Press Brake", "Shearing Machine",
    "Plate Rolling Machine", "Pipe Bending Machine", "Busbar Bending Machine", "Notching Machine", "Punching Machine",
    "Deburring Machine", "Chamfering Machine", "Beveling Machine", "Pipe Cutting Machine", "Tube End Forming Machine",
    "Wire Cutting Machine", "EDM Machine", "Wire EDM", "Sinker EDM", "3D Printer",
    "Injection Molding Machine", "Blow Molding Machine", "Extrusion Machine", "Granulator Machine", "Crushing Machine",
    "Vibratory Feeder", "Screw Feeder", "Belt Feeder", "Weighing Scale", "Checkweigher",
    "Metal Detector", "X-ray Inspection System", "Labeling Machine", "Packing Machine", "Filling Machine",
    "Capping Machine", "Sealing Machine", "Vacuum Packing Machine", "Shrink Wrapping Machine", "Strapping Machine",
    "Batch Coding Machine", "Inkjet Printer", "Thermal Transfer Printer", "Carton Sealer", "Case Erector",
    "Palletizer", "Depalletizer", "Stretch Wrapping Machine", "Industrial Water Pump", "Vibration Sensor",
    "Power Factor Controller", "Inductive Coupler"
]

def get_next_key(index):
    return SERPAPI_KEYS[index % len(SERPAPI_KEYS)]

def fetch_images(product, api_key):
    try:
        response = requests.get(
            "https://serpapi.com/search.json",
            headers=HEADERS,
            params={
                "q": product,
                "tbm": "isch",
                "api_key": api_key,
                "ijn": 0
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        return data.get("images_results", [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch images for {product}: {e}")
        return []

def sanitize_filename(text):
    return "".join(c for c in text if c.isalnum() or c in (' ', '_')).strip().replace(" ", "_")

def extract_brand_from_title(title):
    words = title.split()
    if len(words) >= 2:
        return "_".join(words[:2])
    elif words:
        return words[0]
    return "Unknown"

def save_image(url, path):
    try:
        img_data = requests.get(url, timeout=10).content
        with open(path, 'wb') as handler:
            handler.write(img_data)
        return True
    except Exception as e:
        print(f"[ERROR] Could not save image from {url}: {e}")
        return False

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def scrape_images():
    ensure_dir(SAVE_DIR)
    key_index = 0

    for product in tqdm(PRODUCTS, desc="Scraping Products"):
        product_folder = os.path.join(SAVE_DIR, sanitize_filename(product))
        ensure_dir(product_folder)

        metadata = []
        count = 0
        attempts = 0
        used_filenames = set()

        while count < NUM_IMAGES and attempts < RETRY_LIMIT:
            key = get_next_key(key_index)
            key_index += 1
            results = fetch_images(product, key)

            for result in results:
                if count >= NUM_IMAGES:
                    break

                title = result.get("title", "")
                if product.lower() not in title.lower():
                    continue

                brand = extract_brand_from_title(title)
                filename = sanitize_filename(f"{brand}_{product}")
                if filename.lower() in used_filenames:
                    continue

                url = result.get("original")
                filepath = os.path.join(product_folder, f"{filename}.jpg")

                if save_image(url, filepath):
                    metadata.append({
                        "filename": f"{filename}.jpg",
                        "url": url,
                        "product": product,
                        "brand": brand,
                        "title": title
                    })
                    used_filenames.add(filename.lower())
                    count += 1

            attempts += 1
            time.sleep(SLEEP_BETWEEN_ATTEMPTS)

        # Save metadata
        metadata_path = os.path.join(product_folder, "metadata.json")
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Failed to save metadata for {product}: {e}")

if __name__ == "__main__":
    scrape_images()
