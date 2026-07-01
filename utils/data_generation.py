import json
import random
import string

random.seed(42)

CATEGORIES = [
    "Electronics/Computers/Laptops",
    "Electronics/Computers/Peripherals",
    "Electronics/Phones/Smartphones",
    "Electronics/Phones/Accessories",
    "Electronics/Audio/Headphones",
    "Electronics/Audio/Speakers",
    "Office/Furniture/Chairs",
    "Office/Furniture/Desks",
    "Office/Supplies/Paper",
    "Office/Supplies/Pens",
    "Software/Productivity",
    "Software/Security",
    "Networking/Routers",
    "Networking/Switches",
    "Networking/Cables",
]

WORDS = [
    "wireless", "ergonomic", "compact", "portable", "mechanical",
    "bluetooth", "usb", "hdmi", "rechargeable", "adjustable",
    "gaming", "professional", "silent", "backlit", "foldable",
    "keyboard", "mouse", "monitor", "headset", "webcam",
    "chair", "desk", "lamp", "cable", "adapter",
    "router", "switch", "hub", "drive", "printer",
    "laser", "inkjet", "optical", "digital", "smart",
    "pro", "lite", "plus", "max", "ultra",
]

def make_product(i: int) -> dict:
    n_words = random.randint(2, 4)
    name_words = random.sample(WORDS, n_words)
    name = " ".join(w.capitalize() for w in name_words)
    tags = random.sample(WORDS, random.randint(2, 6))
    return {
        "id": f"P{i:05d}",
        "name": name,
        "category": random.choice(CATEGORIES),
        "tags": tags,
        "price": round(random.uniform(5.0, 999.0), 2),
        "stock": random.randint(0, 500),
        "sales_rank": random.randint(1, 5000),
    }

catalog = [make_product(i) for i in range(5000)]
with open("catalog.json", "w") as f:
    json.dump(catalog, f, indent=2)

print(f"Generated {len(catalog)} products -> catalog.json")