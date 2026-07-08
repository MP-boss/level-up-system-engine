import streamlit as st
import sqlite3
import hashlib
import json
import os
from datetime import datetime

# Switched to v4 to completely bypass the locked, corrupted older database file!
DB_FILE = "system_data_v4.db"
IMAGE_FOLDER = "hunter_vault_images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Build the perfect 13-column structural layout right out of the gate
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, level INTEGER, xp INTEGER, 
                  strength INTEGER, agility INTEGER, intelligence INTEGER, gold INTEGER,
                  streak INTEGER, custom_quests TEXT, inventory TEXT, equipped TEXT, gallery_logs TEXT)''')
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, 1, 0, 10, 10, 10, 100, 0, '[]', '[]', '', '[]')", (username, hashed_pw))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
    user = c.fetchone()
    conn.close()
    return user

def update_all_data(username, level, xp, strength, agility, intelligence, gold, streak, custom_quests, inventory, equipped, gallery_logs):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''UPDATE users SET level=?, xp=?, strength=?, agility=?, intelligence=?, gold=?, 
                 streak=?, custom_quests=?, inventory=?, equipped=?, gallery_logs=? WHERE username=?''', 
              (level, xp, strength, agility, intelligence, gold, streak, custom_quests, inventory, equipped, gallery_logs, username))
    conn.commit()
    conn.close()

init_db()

# --- INTERFACE CONFIG ---
st.set_page_config(page_title="THE SYSTEM", page_icon="⚡", layout="wide")
st.title("⚡ THE SYSTEM ENGINE v3.4 ⚡")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- AUTHENTICATION ---
if not st.session_state.logged_in:
    menu = ["Login", "Register As Hunter"]
    choice = st.sidebar.selectbox("System Menu", menu)

    if choice == "Login":
        st.subheader("Awaken Your Account")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            userdata = login_user(username, password)
            if userdata:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.level = userdata[2]
                st.session_state.xp = userdata[3]
                st.session_state.strength = userdata[4]
                st.session_state.agility = userdata[5]
                st.session_state.intelligence = userdata[6]
                st.session_state.gold = userdata[7]
                st.session_state.streak = userdata[8]
                
                try: st.session_state.custom_quests = json.loads(userdata[9]) if userdata[9] else []
                except: st.session_state.custom_quests = []
                    
                try: st.session_state.inventory = json.loads(userdata[10]) if userdata[10] else []
                except: st.session_state.inventory = []
                    
                st.session_state.equipped = userdata[11] if userdata[11] is not None else ""
                
                try: st.session_state.gallery_logs = json.loads(userdata[12]) if userdata[12] else []
                except: st.session_state.gallery_logs = []
                st.rerun()
            else:
                st.error("Invalid Credentials.")
                
    elif choice == "Register As Hunter":
        st.subheader("Create New Hunter Profile")
        new_user = st.text_input("Choose Username")
        new_password = st.text_input("Choose Password", type='password')
        if st.button("Register"):
            if create_user(new_user, new_password):
                st.success("Profile created! Switch to Login menu.")
            else:
                st.error("Username taken.")

# --- THE GAME INTERFACE ---
else:
    def save_game():
        update_all_data(
            st.session_state.username, st.session_state.level, st.session_state.xp,
            st.session_state.strength, st.session_state.agility, st.session_state.intelligence,
            st.session_state.gold, st.session_state.streak, 
            json.dumps(st.session_state.custom_quests), json.dumps(st.session_state.inventory), 
            st.session_state.equipped, json.dumps(st.session_state.gallery_logs)
        )

    xp_mult, gold_mult = 1.0, 1.0
    if st.session_state.equipped == "Heavy Weights": xp_mult += 0.20
    if st.session_state.equipped == "Running Shoes": xp_mult += 0.10
    if st.session_state.equipped == "Amulet of Greed": gold_mult += 0.50

    if st.session_state.streak >= 7: gold_mult += 0.50; xp_mult += 0.50
    elif st.session_state.streak >= 3: gold_mult += 0.25; xp_mult += 0.25

    st.sidebar.header(f"👤 HUNTER STATUS")
    st.sidebar.subheader(f"Name: {st.session_state.username}")
    
    total_stats = st.session_state.strength + st.session_state.agility + st.session_state.intelligence
    if total_stats > 120: hunter_rank = "S-Rank Supreme"
    elif total_stats > 70: hunter_rank = "A-Rank Raider"
    elif total_stats > 45: hunter_rank = "B-Rank Hunter"
    else: hunter_rank = "E-Rank Apprentice"

    st.sidebar.markdown(f"**Rank:** `{hunter_rank}`")
    st.sidebar.markdown(f"🔥 **Daily Streak:** `{st.session_state.streak} Days`")
    st.sidebar.markdown(f"💰 **Gold:** `{st.session_state.gold} G`")
    st.sidebar.markdown(f"🎒 **Equipped:** `{st.session_state.equipped if st.session_state.equipped else 'None'}`")
    st.sidebar.markdown("---")
    st.sidebar.write(f"💪 **STR:** {st.session_state.strength}")
    st.sidebar.write(f"⚡ **AGI:** {st.session_state.agility}")
    st.sidebar.write(f"🧠 **INT:** {st.session_state.intelligence}")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    xp_needed = st.session_state.level * 100
    st.header(f"👑 Player Level: {st.session_state.level}")
    st.progress(min(1.0, st.session_state.xp / xp_needed))
    st.write(f"XP: {st.session_state.xp} / {xp_needed} (XP Boost: {xp_mult}x | Gold Boost: {gold_mult}x)")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔥 Quests", "⚔️ Dungeons", "🛒 Shop", "🎒 Inventory", "🖼️ Hunter Vault", "⚠️ Penalties"
    ])

    # --- TAB 1: QUESTS ---
    with tab1:
        st.subheader("Daily Mission Checklist")
        def process_quest_payout(xp_base, gold_base, stat_target):
            final_xp, final_gold = int(xp_base * xp_mult), int(gold_base * gold_mult)
            st.session_state.xp += final_xp
            st.session_state.gold += final_gold
            if stat_target != 'none': st.session_state[stat_target] += 1
            if st.session_state.xp >= xp_needed:
                st.session_state.xp -= xp_needed
                st.session_state.level += 1
                st.balloons()
            save_game()
            st.success(f"Quest Complete! Earned {final_xp} XP and {final_gold} Gold!")
            st.rerun()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("🏋️ **Core Workout**")
            if st.button("Complete STR Quest"): process_quest_payout(25, 50, 'strength')
        with col2:
            st.info("🏃 **Cardio Track**")
            if st.button("Complete AGI Quest"): process_quest_payout(25, 50, 'agility')
        with col3:
            st.info("📚 **Mental Codex**")
            if st.button("Complete INT Quest"): process_quest_payout(25, 50, 'intelligence')

        st.markdown("---")
        st.subheader("🛠️ Forge Custom Daily Mission")
        cq_title = st.text_input("Quest Goal Name")
        cq_stat = st.selectbox("Assign Attribute Reward", ["strength", "agility", "intelligence", "none"])
        if st.button("Lock Quest Into Matrix"):
            if cq_title:
                st.session_state.custom_quests.append({"title": cq_title, "stat": cq_stat})
                save_game()
                st.rerun()

        if st.session_state.custom_quests:
            for idx, q in enumerate(st.session_state.custom_quests):
                c_col, d_col = st.columns([4, 1])
                c_col.warning(f"🎯 **{q['title']}** (Rewards +1 {q['stat'].upper()})")
                if d_col.button("Clear Quest", key=f"cq_{idx}"):
                    st.session_state.custom_quests.pop(idx)
                    process_quest_payout(20, 40, q['stat'])

    # --- TAB 2: DUNGEONS ---
    with tab2:
        st.subheader("Gate Portal System")
        dungeons = [
            {"name": "D-Rank Gate: Goblin Outpost", "power": 35, "xp": 100, "gold": 200},
            {"name": "B-Rank Gate: Shadow Cerberus", "power": 60, "xp": 250, "gold": 500},
            {"name": "S-Rank Gate: The Dragon Monarch", "power": 120, "xp": 1000, "gold": 2000}
        ]
        for d in dungeons:
            with st.expander(f"🔮 {d['name']} (Required Power: {d['power']})"):
                st.write(f"Combat Power: `{total_stats}`")
                if st.button(f"Enter Gate", key=d['name']):
                    if total_stats >= d['power']:
                        st.session_state.xp += d['xp']
                        st.session_state.gold += d['gold']
                        if st.session_state.xp >= xp_needed:
                            st.session_state.xp -= xp_needed
                            st.session_state.level += 1
                        save_game()
                        st.balloons()
                        st.rerun()
                    else: st.error("❌ COMBAT POWER TOO LOW.")

    # --- TAB 3: SYSTEM SHOP ---
    with tab3:
        st.subheader("Exchange Gold for Matrix Upgrades")
        def process_purchase(cost, item_name, is_gear=False):
            if st.session_state.gold >= cost:
                st.session_state.gold -= cost
                if is_gear and item_name not in st.session_state.inventory:
                    st.session_state.inventory.append(item_name)
                save_game()
                st.success(f"Acquired: {item_name}!")
                st.rerun()
            else: st.error("Insufficient Gold!")

        st.write("### ⚙️ Equipment Shop")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.info("🏋️ **Heavy Weights**\n\n+20% STR XP\n\n200 G")
            if st.button("Buy Weights"): process_purchase(200, "Heavy Weights", is_gear=True)
        with sc2:
            st.info("🏃 **Running Shoes**\n\n+10% AGI XP\n\n150 G")
            if st.button("Buy Shoes"): process_purchase(150, "Running Shoes", is_gear=True)
        with sc3:
            st.info("🏆 **Amulet of Greed**\n\n+50% Gold Multiplier\n\n400 G")
            if st.button("Buy Amulet"): process_purchase(400, "Amulet of Greed", is_gear=True)

    # --- TAB 4: INVENTORY ---
    with tab4:
        st.subheader("Your Armory & Equipment Matrix")
        if not st.session_state.inventory: st.write("Inventory empty.")
        else:
            for item in st.session_state.inventory:
                col_i, col_b = st.columns([3, 1])
                col_i.write(f"📦 **{item}**")
                if st.session_state.equipped == item: col_b.write("`EQUIPPED`")
                elif col_b.button("Equip", key=f"equip_{item}"):
                    st.session_state.equipped = item
                    save_game()
                    st.rerun()

    # --- TAB 5: HUNTER VAULT ---
    with tab5:
        st.subheader("🖼️ Hunter Progression Memory Vault")
        uploaded_file = st.file_uploader("Upload New Progress Entry (JPG/PNG)", type=["jpg", "jpeg", "png"])
        caption_input = st.text_input("Enter Entry Log Note")
        
        if st.button("Secure to Vault"):
            if uploaded_file and caption_input:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = os.path.splitext(uploaded_file.name)[1]
                secure_filename = f"{st.session_state.username}_{timestamp}{file_extension}"
                full_save_path = os.path.join(IMAGE_FOLDER, secure_filename)
                
                with open(full_save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state.gallery_logs.append({
                    "filename": secure_filename,
                    "caption": caption_input,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                save_game()
                st.success("Visual status record logged.")
                st.rerun()

        st.markdown("---")
        if st.session_state.gallery_logs:
            for entry in reversed(st.session_state.gallery_logs):
                img_path = os.path.join(IMAGE_FOLDER, entry["filename"])
                if os.path.exists(img_path):
                    col_img, col_txt = st.columns([1, 2])
                    with col_img: st.image(img_path, use_container_width=True)
                    with col_txt:
                        st.markdown(f"📅 **Logged:** `{entry['date']}`")
                        st.write(f"📝 **Note:** {entry['caption']}")
                    st.markdown("---")

    # --- TAB 6: PENALTIES ---
    with tab6:
        st.subheader("System Calibration Zone")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("Increment Streak Combo (+1 Day)"):
                st.session_state.streak += 1
                save_game()
                st.rerun()
        with col_p2:
            if st.button("Trigger System Penalty"):
                st.session_state.streak = 0
                st.session_state.xp = max(0, st.session_state.xp - 30)
                st.session_state.gold = max(0, st.session_state.gold - 50)
                save_game()
                st.rerun()
