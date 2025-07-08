import streamlit as st
import random
import json
import os
import math
from supabase import create_client
import tempfile

# --- Supabase setup ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)
bucket = "swnbucket"  


# --- Upload JSON file to Supabase Storage ---
def upload_json(filename, data):
    content = json.dumps(data, indent=2)

    # Create a temporary file
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    # Upload the file by path
    supabase.storage.from_(bucket).upload(
        filename,
        tmp_path,
        {"content-type": "application/json", "upsert": "true"}
    )

    # Clean up temporary file
    os.remove(tmp_path)


# --- Download JSON file from Supabase Storage ---
def download_json(filename):
    try:
        res = supabase.storage.from_(bucket).download(filename)
        if res:
            return json.loads(res.decode())
        else:
            return None
    except Exception as e:
        st.error(f"Failed to download {filename}: {e}")
        return None

###################################################################


ship_money = 100000
available_tons = 100

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

def update_price_variations():
    variations = {}
    for item in trade_goods:
        variation = random.uniform(0.9, 1.1)
        variations[item["name"]] = variation
    upload_json("price_variations.json", variations)
    st.session_state.price_variations = variations

# Load once on app startup
if "stations" not in st.session_state:
    st.session_state.stations = download_json("stations.json") or []

if "current_station" not in st.session_state:
    st.session_state.current_station = download_json("current_station.json") or []

if "ship" not in st.session_state:
    st.session_state.ship = download_json("ship.json") or {"inventory": {}, "credits": 100000, "cargo_limit": 50}

if "price_variations" not in st.session_state:
    update_price_variations()

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

                upload_json("ship.json", ship)
                st.session_state.alert = f"Ejected {eject_qty} units of {item_name}"
                st.rerun()

    st.subheader("Add or Subtract Funds")
    # Input: amount to add or subtract
    credit_delta = st.number_input("Enter amount", min_value=0, step=100, key="credit_input",format="%d")

    # Two side-by-side buttons
    credit_cols = st.columns([1, 1])
    if credit_cols[0].button("Add Funds"):
        ship["credits"] += credit_delta
        upload_json("ship.json", ship)
        st.session_state.alert = f"Added {credit_delta:.0f} credits" 
        st.rerun()

    if credit_cols[1].button("Spend Funds"):
        if ship["credits"] >= credit_delta:
            ship["credits"] -= credit_delta
            upload_json("ship.json", ship)
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
        upload_json("ship.json", st.session_state.ship)
        st.session_state.alert = f"Looted {manual_qty}x {selected_item}"
        st.rerun()
    
    st.subheader("Adjust Cargo Capacity")
    new_limit = st.number_input("Set new cargo limit", min_value=1, step=1, value=ship["cargo_limit"], key="cargo_limit_input")
    if st.button("Update Cargo Limit"):
        ship["cargo_limit"] = new_limit
        upload_json("ship.json", st.session_state.ship)
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
                upload_json("ship.json", ship)
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

                    upload_json("ship.json", ship)
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
                upload_json("current_station.json", name)
                
                # Re-generate shop items with 90% chance
                shop_items = []
                for item in trade_goods:
                    if any(station["goods"].get(tag, {}).get("sells") for tag in item["tags"]):
                        if random.random() <= 0.4:
                            shop_items.append(item)
                st.session_state.shop_items = shop_items

                # Re-generate price variation
                update_price_variations()
                

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
            upload_json("stations.json", st.session_state.stations)
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
            upload_json("stations.json", st.session_state.stations)
            st.session_state.alert = f"Deleted station: {station['name']}"
            st.rerun()