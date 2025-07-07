import streamlit as st
import random
import json
import os
import math

#GOOGLE DRIVE STUFF
###################################################################
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

FOLDER_ID = '1IWzgBwqL85nGjxvQUr0vDRx_IzojNUF1'
# --- Load from Streamlit secrets ---
creds_dict = st.secrets["gdrive_service_account"]

# --- Authenticate ---
creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/drive.file"])
drive_service = build("drive", "v3", credentials=creds)



def upload_json_to_drive(filename, data):
    # Search for existing file
    query = f"name='{filename}' and '{FOLDER_ID}' in parents and trashed=false"
    response = drive_service.files().list(q=query, fields="files(id)").execute()
    files = response.get('files', [])
    
    # Convert data to a stream
    stream = io.BytesIO(json.dumps(data, indent=2).encode('utf-8'))
    media = MediaIoBaseUpload(stream, mimetype='application/json', resumable=True)

    if files:
        # Update existing file
        file_id = files[0]['id']
        updated_file = drive_service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
    else:
        # Create new file
        file_metadata = {
            'name': filename,
            'parents': [FOLDER_ID],
            'mimeType': 'application/json'
        }
        created_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

def download_json_from_drive(filename):
    # Find the file in the folder
    query = f"name='{filename}' and '{FOLDER_ID}' in parents and trashed=false"
    response = drive_service.files().list(q=query, fields="files(id)").execute()
    files = response.get('files', [])

    if not files:
        return None

    file_id = files[0]['id']
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    return json.load(fh)





###################################################################


ship_money = 100000
available_tons = 100

stations_data_file = "stations.json"
# --- Load stations from file ---
def load_stations():
    if os.path.exists(stations_data_file):
        with open(stations_data_file, "r") as f:
            return json.load(f)
    return []

# --- Save stations to file ---
def save_stations(data):
    with open(stations_data_file, "w") as f:
        json.dump(data, f, indent=2)

# Load once on app startup
if "stations" not in st.session_state:
    st.session_state.stations = load_stations()

current_station_file = "current_station.json"

ship_data_file = "ship.json"

def load_ship():
    if os.path.exists(ship_data_file):
        with open(ship_data_file, "r") as f:
            return json.load(f)
    return {"inventory": {}, "credits": 100000, "cargo_limit": 50}

def save_ship(data):
    with open(ship_data_file, "w") as f:
        json.dump(data, f, indent=2)

# Load into session state
if "ship" not in st.session_state:
    st.session_state.ship = load_ship()



def save_current_station(name):
    with open(current_station_file, "w") as f:
        json.dump({"name": name}, f)
def load_current_station():
    if os.path.exists(current_station_file):
        with open(current_station_file, "r") as f:
            return json.load(f).get("name")
    return None
# Initialize current station in session state
if "current_station" not in st.session_state:
    st.session_state.current_station = load_current_station()



all_tags = [
    "Astronautic",
    "Component",
    "Consumer",
    "Cultural", #ADD THEM TO LIST BELOW
    "Entertainment",
    "Exotic",
    "Food",
    "High Tech",
    "Illegal",
    "Information",
    "Life Support",
    "Livestock",
    "Low Tech",
    "Luxury",
    "Maltech",
    "Medical",
    "Military",
    "Pretech", #Needs more
    "Raw Material",
    "Tool",
    "Vehicle"
]

trade_goods = [
    {"name": "Pretech Components", "tags": ["Pretech"], "base_price": 40000 },
    {"name": "Spare Ship Parts", "tags": ["Astronautic", "Raw Material"], "base_price": 10000 },
    {"name": "Propulsion Components", "tags": ["Astronautic", "High Tech"], "base_price": 16000 },
    {"name": "Hull Alloys", "tags": ["Astronautic", "Raw Material"], "base_price": 10000 },
    {"name": "Sensor Systems", "tags": ["Astronautic", "High Tech"], "base_price": 15000 },
    {"name": "Ship Maintenance Equipment", "tags": ["Astronautic", "Tool"], "base_price": 10000 },
    {"name": "Circuit Boards", "tags": ["Component", "High Tech"], "base_price": 6000 },
    {"name": "Power Cells", "tags": ["Component", "High Tech"], "base_price": 12000 },
    {"name": "Microactuators", "tags": ["Component", "High Tech"], "base_price": 16000 },
    {"name": "Quantum Chips", "tags": ["Component", "High Tech"], "base_price": 20000 },
    {"name": "Bearings & Bushings", "tags": ["Component", "Low Tech"], "base_price": 4000 },
    {"name": "Structural Beams", "tags": ["Component", "Low Tech"], "base_price": 4000 },
    {"name": "Fasteners", "tags": ["Component", "Low Tech"], "base_price": 3000 },
    {"name": "Personal Electronics", "tags": ["Consumer", "Low Tech"], "base_price": 6000 },
    {"name": "Fashion and Apparel", "tags": ["Consumer", "Low Tech"], "base_price": 3000 },
    {"name": "Household Robotics", "tags": ["Consumer", "High Tech"], "base_price": 8000 },
    {"name": "Holo-vids and Simulations", "tags": ["Entertainment", "High Tech"], "base_price": 6000 },
    {"name": "Musical Instruments and Gear", "tags": ["Entertainment", "Consumer"], "base_price": 6000 },
    {"name": "Alien Biomass", "tags": ["Exotic", "Raw Material"], "base_price": 12000 },
    {"name": "Rare Isotopes", "tags": ["Exotic", "Raw Material"], "base_price": 22000 },
    {"name": "Preserved Rations", "tags": ["Food", "Low Tech"], "base_price": 4000 },
    {"name": "Fresh Produce", "tags": ["Food", "Consumer"], "base_price": 4000 },
    {"name": "Bioengineered Fruits", "tags": ["Food", "Exotic"], "base_price": 4000 },
    {"name": "Food (Cultural Specialties)", "tags": ["Food", "Exotic"], "base_price": 10000 },
    {"name": "Food (Luxury Delicacies)", "tags": ["Food", "Luxury"], "base_price": 15000 },
    {"name": "Synthetic Proteins", "tags": ["Food", "Life Support"], "base_price": 4000 },
    {"name": "AI Cores", "tags": ["High Tech", "Component"], "base_price": 20000 },
    {"name": "Nanite Bots", "tags": ["High Tech", "Component"], "base_price": 20000 },
    {"name": "Cloaking Devices", "tags": ["High Tech", "Military"], "base_price": 10000 },
    {"name": "Cybernetic Implants", "tags": ["High Tech", "Consumer"], "base_price": 10000 },
    {"name": "Star Charts and Survey Data", "tags": ["Information", "Astronautic"], "base_price": 4000 },
    {"name": "CourierNet SSD's", "tags": ["Information", "Consumer"], "base_price": 8000 },
    {"name": "Research Data and Blueprints", "tags": ["Information", "High Tech"], "base_price": 10000 },
    {"name": "Oxygen Canisters", "tags": ["Life Support", "Low Tech"], "base_price": 4000 },
    {"name": "Water Recycling Units", "tags": ["Life Support", "Low Tech"], "base_price": 6000 },
    {"name": "Temperature Control Systems", "tags": ["Life Support", "Low Tech"], "base_price": 5000 },
    {"name": "Emergency Survival Gear", "tags": ["Life Support", "Consumer"], "base_price": 4000 },
    {"name": "Protein Livestock", "tags": ["Livestock", "Food"], "base_price": 4000 },
    {"name": "Pack Beasts", "tags": ["Livestock", "Vehicle"], "base_price": 4000 },
    {"name": "Companion Animals", "tags": ["Livestock", "Luxury"], "base_price": 12000},
    {"name": "Hand Tools", "tags": ["Low Tech", "Tool"], "base_price": 4000},
    {"name": "Servo Motors", "tags": ["Low Tech", "Component"], "base_price": 6000},
    {"name": "Manual Power Generators", "tags": ["Low Tech", "Life Support"], "base_price": 4000},
    {"name": "Designer Clothing", "tags": ["Luxury", "Consumer"], "base_price": 12000},
    {"name": "Jewelry", "tags": ["Luxury", "Consumer"], "base_price": 20000},
    {"name": "Rare Spices", "tags": ["Luxury", "Food"], "base_price": 8000},
    {"name": "Rare Beverages", "tags": ["Luxury", "Food"], "base_price": 6000},
    {"name": "Rare Gems", "tags": ["Luxury", "Raw Material"], "base_price": 12000},
    {"name": "Unbraked AI Cores", "tags": ["Maltech", "High Tech"], "base_price": 40000},
    {"name": "Common Medicine", "tags": ["Medical", "Life Support"], "base_price": 8000},
    {"name": "Specialized Treatments", "tags": ["Medical", "High Tech"], "base_price": 10000},
    {"name": "Combat Stimulants", "tags": ["Medical", "Military"], "base_price": 8000},
    {"name": "Recreational Drugs", "tags": ["Medical", "Consumer"], "base_price": 8000},
    {"name": "Organ Replacements", "tags": ["Medical", "High Tech"], "base_price": 12000},
    {"name": "Small Arms & Ammunition", "tags": ["Military", "Low Tech"], "base_price": 3000},
    {"name": "Heavy Arms & Ammunition", "tags": ["Military", "Low Tech"], "base_price": 8000},
    {"name": "Powered Armor", "tags": ["Military", "High Tech"], "base_price": 10000},
    {"name": "ECM Generator", "tags": ["Military", "High Tech"], "base_price": 10000},
    {"name": "Tactical Drones", "tags": ["Military", "High Tech"], "base_price": 8000},
    {"name": "Ore (Unrefined)", "tags": ["Raw Material", "Low Tech"], "base_price": 1000},
    {"name": "Ore (Rare)", "tags": ["Raw Material", "Exotic"], "base_price": 4000},
    {"name": "Polyceramics", "tags": ["Raw Material", "High Tech"], "base_price": 6000},
    {"name": "Timber and Plant Fiber", "tags": ["Raw Material", "Luxury"], "base_price": 10000},
    {"name": "Construction Equipment", "tags": ["Tool", "Vehicle"], "base_price": 8000},
    {"name": "Precision Instruments", "tags": ["Tool", "High Tech"], "base_price": 8000},
    {"name": "Gravcar", "tags": ["Vehicle", "Consumer"], "base_price": 4000},
    {"name": "Gravtank", "tags": ["Vehicle", "Military"], "base_price": 20000},
    {"name": "Hoverbikes", "tags": ["Vehicle", "Consumer"], "base_price": 2000},
    ]

price_variation_file = "price_variation.json"

def load_price_variations():
    if os.path.exists(price_variation_file):
        with open(price_variation_file, "r") as f:
            return json.load(f)
    else:
        initialize_variations()
        with open(price_variation_file, "r") as f:
            return json.load(f)
        
    return {}

def save_price_variations(variations):
    with open(price_variation_file, "w") as f:
        json.dump(variations, f, indent=1)

def initialize_variations():
    variations = {}
    for item in trade_goods:
        variation = random.uniform(0.9, 1.1)
        variations[item["name"]] = variation
    save_price_variations(variations)

if "price_variations" not in st.session_state:
    st.session_state.price_variations = load_price_variations()


# Initialize shop_items if not already present
if "shop_items" not in st.session_state:
    st.session_state.shop_items = []

# If current station is loaded and shop_items is empty, generate once
current = st.session_state.get("current_station")
stations = st.session_state.get("stations", [])

if current and not st.session_state.shop_items:
    station_data = next((s for s in stations if s["name"] == current), None)
    if station_data:
        available_items = []
        for item in trade_goods:
            if any(station_data["goods"].get(tag, {}).get("sells") for tag in item["tags"]):
                if random.random() <= 0.9:
                    available_items.append(item)
        st.session_state.shop_items = available_items





st.title("Stars Without Number Trading App")


# Track selected tab persistently
tab_names = ["Ship Cargo", "Buy Goods", "Sell Goods", "Travel", "Trade Station Config"]
selected_tab = st.radio("Select Tab", tab_names, key="selected_tab", horizontal=True, label_visibility="hidden")

# Ping alert at top of screen
def ping_alert():
    if "alert" in st.session_state:
        st.success(st.session_state.alert)
        del st.session_state.alert

ping_alert()

if selected_tab == "Ship Cargo":
    st.title("Ship Cargo")
    ship = st.session_state.ship
    inventory = ship.get("inventory", {})
    total_cargo = sum(inventory.values())
    st.markdown(f"**Cargo Used:** {total_cargo} / {ship['cargo_limit']} units")
    st.markdown(f"**Credits:** {round(ship['credits'])} cr")
    
    if not inventory:
        st.info("No cargo in ship.")
    else:
        # Table headers: Add Tags column
        header_cols = st.columns([2.5, 2.5, 1.5, 1.5, 1.5])
        for col, label in zip(header_cols, ["Item", "Tags", "Amount", "Qty", "Eject"]):
            col.markdown(f"**{label}**")

        for idx, (item_name, amount_owned) in enumerate(inventory.items()):
            cols = st.columns([2.5, 2.5, 1.5, 1.5, 1.5])

            # Find matching trade good for tags
            item_info = next((g for g in trade_goods if g["name"] == item_name), None)
            tag_text = ", ".join(item_info["tags"]) if item_info else "Unknown"

            cols[0].write(item_name)
            cols[1].write(tag_text)
            cols[2].write(f"{amount_owned}")

            # Quantity selector
            qty_key = f"eject_qty_{idx}"
            eject_qty = cols[3].selectbox(
                "", options=list(range(0, amount_owned + 1)),
                key=qty_key, label_visibility="collapsed"
            )

            # Eject button
            eject_key = f"eject_btn_{idx}"
            if cols[4].button("Eject", key=eject_key) and eject_qty > 0:
                new_amount = amount_owned - eject_qty
                if new_amount > 0:
                    inventory[item_name] = new_amount
                else:
                    del inventory[item_name]  # remove if 0

                save_ship(ship)
                st.session_state.alert = f"Ejected {eject_qty} units of {item_name}"
                st.rerun()

    st.subheader("Add or Subtract Funds")
    # Input: amount to add or subtract
    credit_delta = st.number_input("Enter amount", min_value=0, step=100, key="credit_input",format="%d")

    # Two side-by-side buttons
    credit_cols = st.columns([1, 1])
    if credit_cols[0].button("Add Funds"):
        ship["credits"] += credit_delta
        save_ship(ship)
        st.session_state.alert = f"Added {credit_delta:.0f} credits" 
        st.rerun()

    if credit_cols[1].button("Spend Funds"):
        if ship["credits"] >= credit_delta:
            ship["credits"] -= credit_delta
            save_ship(ship)
            st.session_state.alert = f"Spent {credit_delta:.0f} credits"
            st.rerun()
        else:
            st.error("Not enough credits!")

    st.subheader("Add Looted Cargo")
    # Dropdown to select item
    item_names = [item["name"] for item in trade_goods]
    selected_item = st.selectbox("Select Item", item_names, key="manual_add_item")

    # Quantity selector
    manual_qty = st.number_input("Quantity", min_value=1, max_value=50, step=1, value=1, key="manual_add_qty")

    # Add Button
    if st.button("Add Cargo"):
        inventory = st.session_state.ship["inventory"]
        inventory[selected_item] = inventory.get(selected_item, 0) + manual_qty
        save_ship(st.session_state.ship)
        st.session_state.alert = f"Looted {manual_qty}x {selected_item}"
        st.rerun()
    
    st.subheader("Adjust Cargo Capacity")
    new_limit = st.number_input("Set new cargo limit", min_value=1, step=1, value=ship["cargo_limit"], key="cargo_limit_input")
    if st.button("Update Cargo Limit"):
        ship["cargo_limit"] = new_limit
        save_ship(ship)
        st.session_state.alert = f"Updated cargo limit to {new_limit} units"
        st.rerun()

elif selected_tab == "Buy Goods":
    st.title("Buy Screen")
    # --- Load current station ---
    current = st.session_state.current_station
    station_data = next((s for s in st.session_state.stations if s["name"] == current), None)

    if not station_data:
        st.warning("No station selected. Go to Travel tab.")
    else:
        goods_tags = station_data["goods"]
        ship = st.session_state.ship
        inventory = ship["inventory"]
        credits = round(ship["credits"])
        cargo_limit = ship["cargo_limit"]
        used_cargo = sum(inventory.values())
        remaining_space = cargo_limit - used_cargo

        st.markdown(f"**Current Credits:** {credits} cr  |  **Remaining Cargo Space:** {remaining_space} units")
        # --- Table Headers ---
        header_cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5, 1.5])
        headers = ["Item", "Tags", "Base", "Mod", "Price", "Qty", "Buy"]
        for col, label in zip(header_cols, headers):
            col.markdown(f"**{label}**")

        for idx, item in enumerate(st.session_state.shop_items):
            # Determine price modifier: average across all matching tags
            modifiers = []
            for tag in item["tags"]:
                tag_data = goods_tags.get(tag)
                if tag_data:
                    mod_str = tag_data["modifier"]
                    mod_val = int(mod_str.strip("%")) / 100.0
                    modifiers.append(mod_val)
                raw_bonus = sum(modifiers)
                combined_bonus = math.tanh(raw_bonus)  # Smooths to [-1, 1]
                mod = 1 + combined_bonus  # Final base multiplier in [0, 2]
                # Random variation ±10%
                random_factor = st.session_state.price_variations.get(item["name"], 1.0)
                mod *= random_factor
                # Clamp to final bounds
                mod = max(0.5, min(2.0, mod))
                # Final price
                current_price = round(item["base_price"] * mod)

            # UI Layout
            cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5, 1.5])
            cols[0].write(item["name"])
            cols[1].write(", ".join(item["tags"]))
            cols[2].write(f"{item['base_price']} cr")
            if mod < 1:
                cols[3].markdown(f"<span style='color: green;'>{round(mod*100)}%</span>", unsafe_allow_html=True)
                cols[4].markdown(f"<span style='color: green;'>{current_price} cr</span>", unsafe_allow_html=True)
            else:
                cols[3].write(f"{round(mod*100)}%")
                cols[4].write(f"{current_price} cr")

            # Quantity selector
            qty_key = f"qty_{idx}"
            max_qty = min(remaining_space, 20)
            amount = cols[5].selectbox(
                "qty", options=list(range(1, max_qty + 2)), key=qty_key, label_visibility="collapsed"
            )

            # Disable Buy if over cargo or over credits
            total_cost = current_price * amount
            can_afford = total_cost <= credits
            can_store = amount <= remaining_space

            buy_key = f"buy_{idx}"
            if cols[6].button("Buy", key=buy_key, disabled=not (can_afford and can_store)):
                # Update inventory
                inventory[item["name"]] = inventory.get(item["name"], 0) + amount
                ship["credits"] -= total_cost
                save_ship(ship)
                st.session_state.alert = f"Bought {amount}x {item['name']} for {total_cost:.0f} cr"
                st.rerun()
elif selected_tab == "Sell Goods":
    st.title("Sell Goods")

    current = st.session_state.current_station
    station_data = next((s for s in st.session_state.stations if s["name"] == current), None)

    if not station_data:
        st.warning("No station selected. Go to Travel tab.")
    else:
        goods_tags = station_data["goods"]
        ship = st.session_state.ship
        inventory = ship["inventory"]
        credits = round(ship["credits"])

        if not inventory:
            st.info("You have no items to sell.")
        else:
            st.markdown(f"**Current Credits:** {credits} cr")

            # Table headers
            header_cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5, 1.5])
            headers = ["Item", "Tags", "Base", "Mod", "Price", "Qty", "Sell"]
            for col, label in zip(header_cols, headers):
                col.markdown(f"**{label}**")

            for idx, (item_name, quantity_owned) in enumerate(inventory.items()):
                item_info = next((g for g in trade_goods if g["name"] == item_name), None)
                if not item_info:
                    continue

                base_price = item_info["base_price"]
                tag_text = ", ".join(item_info["tags"])

                # Determine price modifier from matching station tags
                modifiers = []
                for tag in item_info["tags"]:
                    tag_data = goods_tags.get(tag)
                    if tag_data:
                        mod_str = tag_data["modifier"]
                        mod_val = int(mod_str.strip("%")) / 100.0
                        modifiers.append(mod_val)
                raw_bonus = sum(modifiers)
                combined_bonus = math.tanh(raw_bonus)  # Smooths to [-1, 1]
                mod = 1 + combined_bonus  # Final base multiplier in [0, 2]
                # Random variation ±10%
                random_factor = st.session_state.price_variations.get(item_info["name"], 1.0)
                mod *= random_factor
                # Clamp to final bounds
                mod = max(0.5, min(2.0, mod))
                # Final price
                current_price = round(item_info["base_price"] * mod)
                cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5, 1.5])
                cols[0].write(item_name)
                cols[1].write(tag_text)
                cols[2].write(f"{base_price} cr")
                if mod > 1:
                    cols[3].markdown(f"<span style='color: green;'>{round(mod*100)}%</span>", unsafe_allow_html=True)
                    cols[4].markdown(f"<span style='color: green;'>{current_price} cr</span>", unsafe_allow_html=True)
                else:
                    cols[3].write(f"{round(mod*100)}%")
                    cols[4].write(f"{current_price} cr")

                qty_key = f"sell_qty_{idx}"
                amount = cols[5].selectbox(
                    "qty", options=list(range(1, quantity_owned + 1)),
                    key=qty_key, label_visibility="collapsed"
                )

                sell_key = f"sell_btn_{idx}"
                if cols[6].button("Sell", key=sell_key):
                    total_value = current_price * amount
                    ship["credits"] += total_value

                    if quantity_owned > amount:
                        inventory[item_name] -= amount
                    else:
                        del inventory[item_name]

                    save_ship(ship)
                    st.session_state.alert = f"Sold {amount}x {item_name} for {total_value:.0f} cr"
                    st.rerun()
elif selected_tab == "Travel":
    st.title("Travel to Space Station")
    current = st.session_state.current_station
    st.markdown(f"**Current Station:** {current or '*None*'}")
    st.markdown("### Available Stations")
    for idx, station in enumerate(st.session_state.stations):
        name = station["name"]
        cols = st.columns([4, 1])
        cols[0].markdown(f"**{name}**")
        if name == current:
            cols[1].button("Here", key=f"here_{idx}", disabled=True)
        else:
            if cols[1].button("Travel", key=f"travel_{idx}"):
                st.session_state.current_station = name
                save_current_station(name)
                
                # Re-generate shop items with 90% chance
                shop_items = []
                for item in trade_goods:
                    if any(station["goods"].get(tag, {}).get("sells") for tag in item["tags"]):
                        if random.random() <= 0.4:
                            shop_items.append(item)
                st.session_state.shop_items = shop_items

                # Re-generate price variation
                initialize_variations()
                st.session_state.price_variations = load_price_variations()

                st.session_state.alert = f"Traveled to {name}"
                st.rerun()
elif selected_tab == "Trade Station Config":
    # --- Define a new station ---
    st.subheader("Define a New Space Station")
    station_name = st.text_input("Station Name")
    st.markdown("### Goods Availability and Price Modifiers")

    selected_tags = {}
    modifiers = {}

    cols = st.columns(3)
    for i, tag in enumerate(all_tags):
        col = cols[i % 3]
        with col:
            selected_tags[tag] = st.checkbox(f"{tag}", key=f"chk_{tag}")
            modifiers[tag] = st.selectbox(
                f"Modifier ({tag})",
                options=[f"{i}%" for i in range(-30, 31, 5)],
                index=6,  # "0%"
                key=f"mod_{tag}"
            )

    # --- Save Button ---
    if st.button("Save Station"):
        if station_name.strip() == "":
            st.error("Station name cannot be empty.")
        else:
            station_data = {
                "name": station_name.strip(),
                "goods": {
                    tag: {
                        "sells": selected_tags[tag],
                        "modifier": modifiers[tag]
                    } for tag in all_tags
                }
            }
            st.session_state.stations.append(station_data)
            save_stations(st.session_state.stations)
            st.session_state.alert = f"Saved station: {station_name}"
            st.rerun()


    # --- Display saved stations ---
    st.markdown("### Saved Stations")

    for idx, station in enumerate(st.session_state.stations):
        st.markdown(f"**{station['name']}**")

        lines = []
        for tag, info in station["goods"].items():
            status = "Sells" if info["sells"] else "Not Sold"
            lines.append(f"{tag}: {status}, Modifier: {info['modifier']}")

        st.markdown("<br>".join(lines), unsafe_allow_html=True) 
    
        if st.button("Delete Station", key=f"delete_{idx}"):
            del st.session_state.stations[idx]
            save_stations(st.session_state.stations)
            st.session_state.alert = f"Deleted station: {station['name']}"
            st.rerun()