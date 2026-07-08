import streamlit as st
from streamlit_oauth import OAuth2Component

# --- GOOGLE OAUTH CONFIGURATION ---
CLIENT_ID = "736118061561-hrrg7sfghbhhv5c51fhq75s9vie31uba.apps.googleusercontent.com"
CLIENT_SECRET = "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"
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REFRESH_TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_TOKEN_URL = "https://oauth2.googleapis.com/revoke"

st.set_page_config(page_title="THE SYSTEM", page_icon="⚡", layout="wide")

# Initialize OAuth Component
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, REFRESH_TOKEN_URL, REVOKE_TOKEN_URL)

# Check if user is already logged in via Google
if "token" not in st.session_state:
    st.title("⚡ THE SYSTEM ENGINE v3.4 ⚡")
    st.subheader("Welcome, Hunter. Please authenticate to access the interface.")
    
    # Render Google Login Button
    result = oauth2.authorize_button(
        name="Continue with Google",
        icon="https://www.google.com/favicon.ico",
        redirect_uri="https://level-up-system-engine.streamlit.app/",
        scope="openid email profile",
        key="google_auth"
    )
    
    if result:
        st.session_state["token"] = result
        st.rerun()
else:
    # User is securely logged in!
    user_email = st.session_state["token"].get("user_id", "Hunter")

    # --- YOUR SYSTEM APP ENGINE ---
    st.sidebar.markdown("## 👤 HUNTER STATUS")
    st.sidebar.write(f"**Account:** {user_email}")
    st.sidebar.markdown("*Rank:* E-Rank Apprentice")
    st.sidebar.markdown("🔥 *Daily Streak:* 0 Days")
    st.sidebar.markdown("💰 *Gold:* 100 G")
    st.sidebar.markdown("🎒 *Equipped:* None")
    st.sidebar.markdown("💪 *STR:* 10")
    st.sidebar.markdown("⚡ *AGI:* 10")
    st.sidebar.markdown("🧠 *INT:* 10")

    if st.sidebar.button("🚪 Logout"):
        del st.session_state["token"]
        st.rerun()

    st.title("⚡ THE SYSTEM ENGINE v3.4 ⚡")
    st.header("👑 Player Level: 1")
    st.caption("XP: 0 / 100 (XP Boost: 1.0x | Gold Boost: 1.0x)")

    tabs = st.tabs(["🔥 Quests", "⚔️ Dungeons", "🛒 Shop", "🎒 Inventory", "🖼️ Hunter Vault", "⚠️ Penalties"])

    with tabs[0]:
        st.subheader("Daily Mission Checklist")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🏋️\n*Core Workout*")
            st.button("Complete STR Quest")
        with col2:
            st.markdown("🏃\n*Cardio Track*")
            st.button("Complete AGI Quest")
        with col3:
            st.markdown("📚\n*Mental Codex*")
            st.button("Complete INT Quest")

        st.markdown("---")
        st.subheader("🛠️ Forge Custom Daily Mission")
        st.text_input("Quest Goal Name")
        st.selectbox("Assign Attribute Reward", ["strength", "agility", "intelligence"])
        st.button("Lock Quest Into Matrix")

    st.markdown("---")
    st.caption("*Status embed installed correctly*")
