import os
import sys
import json
import math
import subprocess
import threading
import streamlit as st
import random
from datetime import datetime, time, timedelta
from PIL import Image, ImageDraw

# ==========================================
# AUTO-INSTALL EXTERNAL LIBRARIES
# ==========================================
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit-autorefresh"])
    from streamlit_autorefresh import st_autorefresh

# ==========================================
# AUTO-SETUP APP THEME (Pure Python)
# ==========================================
def ensure_theme():
    os.makedirs(".streamlit", exist_ok=True)
    config_path = os.path.join(".streamlit", "config.toml")
    theme_config = (
        '[theme]\n'
        'base = "dark"\n'
        'primaryColor = "#3B82F6"\n'
        'backgroundColor = "#080C14"\n'
        'secondaryBackgroundColor = "#162238"\n'
        'textColor = "#F8FAFC"\n'
    )
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(theme_config)

ensure_theme()

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="WaterBuddy: Hydration Companion",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# DATA & CONSTANTS
# ==========================================
DATA_FILE = "waterbuddy_state.json"

AGE_GOALS = {
    "Kids (6-12 years)": 1600,
    "Teens (13-18 years)": 2200,
    "Adults (19-50 years)": 2500,
    "Seniors (65+ years)": 2000
}

HYDRATION_TIPS = [
    "Drink a glass of water first thing in the morning to kickstart your metabolism.",
    "Keep your water bottle within arm's reach so you sip throughout the day.",
    "Eat water-rich foods like watermelon, cucumbers, and oranges.",
    "Drink a glass of water 30 minutes before every meal to aid digestion.",
    "Feeling tired or unfocused? Have a cup of water before reaching for caffeine.",
    "Take a quick hydration break every time you finish a study or work task.",
    "Infuse your water with lemon, cucumber, or mint for a refreshing natural flavor."
]

# ==========================================
# PERSISTENT STORAGE (Prevents Reset on Refresh)
# ==========================================
def save_persistent_state():
    """Saves all session state data to a local JSON file so browser refresh never loses data."""
    data = {
        "setup_complete": st.session_state.setup_complete,
        "user_name": st.session_state.user_name,
        "age_group": st.session_state.age_group,
        "daily_goal": st.session_state.daily_goal,
        "cup_capacity": st.session_state.cup_capacity,
        "bottle_capacity": st.session_state.bottle_capacity,
        "one_time_drink": st.session_state.one_time_drink,
        "reminder_interval": st.session_state.reminder_interval,
        "wake_time": st.session_state.wake_time.strftime("%H:%M"),
        "sleep_time": st.session_state.sleep_time.strftime("%H:%M"),
        "reminders_enabled": st.session_state.reminders_enabled,
        "last_reminder_sent": st.session_state.last_reminder_sent.isoformat() if st.session_state.last_reminder_sent else None,
        "intake": st.session_state.intake,
        "history": st.session_state.history,
        "current_tip": st.session_state.current_tip,
        "celebrated": st.session_state.celebrated
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def load_persistent_state():
    """Loads saved state from disk when the page is refreshed."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            st.session_state.setup_complete = data.get("setup_complete", False)
            st.session_state.user_name = data.get("user_name", "")
            st.session_state.age_group = data.get("age_group", "Adults (19-50 years)")
            st.session_state.daily_goal = int(data.get("daily_goal", AGE_GOALS[st.session_state.age_group]))
            st.session_state.cup_capacity = int(data.get("cup_capacity", 250))
            st.session_state.bottle_capacity = int(data.get("bottle_capacity", 500))
            st.session_state.one_time_drink = int(data.get("one_time_drink", 250))
            st.session_state.reminder_interval = int(data.get("reminder_interval", 30))
            
            w_str = data.get("wake_time", "08:45")
            s_str = data.get("sleep_time", "23:00")
            st.session_state.wake_time = datetime.strptime(w_str, "%H:%M").time()
            st.session_state.sleep_time = datetime.strptime(s_str, "%H:%M").time()
            
            st.session_state.reminders_enabled = data.get("reminders_enabled", True)
            last_rem = data.get("last_reminder_sent")
            st.session_state.last_reminder_sent = datetime.fromisoformat(last_rem) if last_rem else None
            st.session_state.intake = int(data.get("intake", 0))
            st.session_state.history = data.get("history", [])
            st.session_state.current_tip = data.get("current_tip", random.choice(HYDRATION_TIPS))
            st.session_state.celebrated = data.get("celebrated", False)
            return True
        except Exception:
            return False
    return False

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "state_loaded" not in st.session_state:
    loaded = load_persistent_state()
    if not loaded:
        st.session_state.setup_complete = False
        st.session_state.user_name = ""
        st.session_state.age_group = "Adults (19-50 years)"
        st.session_state.daily_goal = AGE_GOALS[st.session_state.age_group]
        st.session_state.cup_capacity = 250
        st.session_state.bottle_capacity = 500
        st.session_state.one_time_drink = 250
        st.session_state.reminder_interval = 30
        st.session_state.wake_time = time(8, 45)
        st.session_state.sleep_time = time(23, 0)
        st.session_state.reminders_enabled = True
        st.session_state.last_reminder_sent = None
        st.session_state.intake = 0
        st.session_state.history = []
        st.session_state.current_tip = random.choice(HYDRATION_TIPS)
        st.session_state.celebrated = False
    st.session_state.state_loaded = True

# ==========================================
# PURE PYTHON CUSTOM WIDGETS & LOGIC
# ==========================================
def extract_ampm(t_obj):
    h = t_obj.hour
    m = t_obj.minute
    a = "AM"
    if h >= 12:
        a = "PM"
        if h > 12: h -= 12
    if h == 0: h = 12
    m_str = f"{(m // 5) * 5:02d}"
    return h, m_str, a

def ampm_time_picker(label, default_time, key_prefix):
    st.caption(f"**{label}**")
    def_h, def_m, def_a = extract_ampm(default_time)
    c1, c2, c3 = st.columns(3)
    with c1: h = st.selectbox("Hr", [1,2,3,4,5,6,7,8,9,10,11,12], index=[1,2,3,4,5,6,7,8,9,10,11,12].index(def_h), key=f"{key_prefix}_h", label_visibility="collapsed")
    with c2: m = st.selectbox("Min", ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"], index=["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"].index(def_m), key=f"{key_prefix}_m", label_visibility="collapsed")
    with c3: a = st.selectbox("AM/PM", ["AM", "PM"], index=["AM", "PM"].index(def_a), key=f"{key_prefix}_a", label_visibility="collapsed")
    hr_24 = h
    if a == "AM" and h == 12: hr_24 = 0
    elif a == "PM" and h != 12: hr_24 += 12
    return time(hr_24, int(m))

def speak_voice_python(text):
    def _speak():
        try:
            safe_text = text.replace("'", "''")
            ps_script = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_text}')"
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        except Exception:
            pass
    threading.Thread(target=_speak, daemon=True).start()

def send_desktop_popup(title, message):
    def _popup():
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showinfo(title, message)
            root.destroy()
        except Exception:
            pass
    threading.Thread(target=_popup, daemon=True).start()

def trigger_voice_and_push_reminder(name, one_time_ml, remaining_ml, goal_ml):
    if remaining_ml <= 0:
        spoken_text = f"Hello {name}. Congratulations! You have completed your hydration goal today."
        push_text = f"Goal Complete! You have already reached {goal_ml} ml today."
    else:
        spoken_text = f"Hello {name}. It is time for your hydration break. Please drink {one_time_ml} milliliters of water now."
        push_text = f"Hydration Reminder: Drink {one_time_ml} ml of water now! ({remaining_ml} ml left)"
    st.toast(push_text)
    send_desktop_popup("Hydration Reminder", push_text)
    speak_voice_python(spoken_text)

def log_water(amount, label="Drink"):
    if amount > 0:
        old_intake = st.session_state.intake
        st.session_state.intake += amount
        current_time = datetime.now().strftime("%I:%M %p")
        st.session_state.history.insert(0, f"{current_time} — Added **{amount} ml** ({label})")
        if old_intake < st.session_state.daily_goal and st.session_state.intake >= st.session_state.daily_goal:
            if not st.session_state.celebrated:
                st.balloons()
                st.session_state.celebrated = True
        save_persistent_state()

def reset_tracker():
    st.session_state.intake = 0
    st.session_state.history = []
    st.session_state.celebrated = False
    st.session_state.last_reminder_sent = None
    st.session_state.current_tip = random.choice(HYDRATION_TIPS)
    save_persistent_state()

def get_interactive_mascot(percentage, age_group, name):
    is_kid = "Kids" in age_group
    if percentage < 25: return "🐢💤", "Ready to Hydrate", f"Tap a drink button to wake Shelly up, {name}!" if is_kid else f"Log your first cup to start your day, {name}."
    elif percentage < 50: return "🐢😊", "25% Milestone: Great Start!", f"Yay! Shelly is awake and smiling, {name}!" if is_kid else f"Good start, {name}. Keep the momentum going."
    elif percentage < 75: return "🐢🌊", "50% Milestone: Halfway There!", "Splash! Shelly is swimming right along!" if is_kid else f"Awesome progress, {name}. You are 50% done."
    elif percentage < 100: return "🐢🚀", "75% Milestone: Almost Done!", "Super Turtle speed! Just a little left!" if is_kid else "Fantastic effort. You are in the home stretch."
    else: return "🐢👑🎉", "100% Goal Achieved!", f"WOOHOO! Shelly is doing a victory dance!" if is_kid else f"Congratulations, {name}. You conquered your goal!"

def draw_hydration_rings(personal_pct, recommended_pct):
    size = 320
    center = size // 2
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r_outer = 140
    width_outer = 28
    bbox_outer = [center - r_outer, center - r_outer, center + r_outer, center + r_outer]
    draw.arc(bbox_outer, start=0, end=360, fill=(34, 197, 94, 55), width=width_outer)
    if personal_pct > 0:
        angle_outer = min(personal_pct, 100) / 100.0 * 360.0
        draw.arc(bbox_outer, start=-90, end=-90 + angle_outer, fill=(34, 197, 94, 255), width=width_outer)
    r_inner = 98
    width_inner = 28
    bbox_inner = [center - r_inner, center - r_inner, center + r_inner, center + r_inner]
    draw.arc(bbox_inner, start=0, end=360, fill=(250, 204, 21, 55), width=width_inner)
    if recommended_pct > 0:
        angle_inner = min(recommended_pct, 100) / 100.0 * 360.0
        draw.arc(bbox_inner, start=-90, end=-90 + angle_inner, fill=(250, 204, 21, 255), width=width_inner)
    if personal_pct >= 100:
        tick_points = [(center - 28, center + 2), (center - 8, center + 24), (center + 32, center - 22)]
        draw.line(tick_points, fill=(255, 255, 255, 255), width=10, joint="curve")
        for pt in tick_points: draw.ellipse([pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5], fill=(255, 255, 255, 255))
    return img

# ==========================================
# SCREEN 1: HOME / ONBOARDING SETUP SCREEN
# ==========================================
if not st.session_state.setup_complete:
    st.write("")
    _, center_col, _ = st.columns([0.5, 2.4, 0.5])
    with center_col:
        with st.container(border=True):
            st.header(":blue[Welcome to WaterBuddy!]")
            st.caption("Set up your profile, drinkware capacities, and custom reminder schedule to begin.")
            
            name_input = st.text_input("What is your name?", value=st.session_state.user_name, placeholder="Enter your name (Required)")
            selected_age = st.selectbox("Select Your Age Group:", options=list(AGE_GOALS.keys()), index=list(AGE_GOALS.keys()).index(st.session_state.age_group))
            
            suggested_target = AGE_GOALS[selected_age]
            if selected_age != st.session_state.age_group:
                st.session_state.age_group = selected_age
                st.session_state.daily_goal = suggested_target
            
            st.info(f"**Recommended Target for {selected_age}:** {suggested_target} ml")
            goal_input = st.number_input("Your Personal Daily Water Target (ml):", min_value=500, max_value=6000, value=st.session_state.daily_goal, step=100)
            
            st.subheader(":violet[Your Drinkware & Single-Sip Capacity]")
            d_col1, d_col2, d_col3 = st.columns(3)
            with d_col1: cup_input = st.number_input("1 Cup Capacity (ml):", min_value=50, max_value=1000, value=st.session_state.cup_capacity, step=25)
            with d_col2: bottle_input = st.number_input("1 Bottle Capacity (ml):", min_value=100, max_value=3000, value=st.session_state.bottle_capacity, step=50)
            with d_col3: one_time_input = st.number_input("Drink at One Time (ml):", min_value=50, max_value=1000, value=st.session_state.one_time_drink, step=25)

            st.subheader(":orange[Your Sleep, Wake & Custom Reminder Schedule]")
            s_col1, s_col2, s_col3 = st.columns(3)
            with s_col1: wake_input = ampm_time_picker("Wake-Up Time:", st.session_state.wake_time, "sw")
            with s_col2: sleep_input = ampm_time_picker("Sleep Time:", st.session_state.sleep_time, "ss")
            with s_col3:
                st.caption("**Custom Reminder Interval**")
                interval_input = st.number_input("Remind after (mins):", min_value=1, max_value=360, value=int(st.session_state.reminder_interval), step=1, label_visibility="collapsed")
            
            st.write("")
            if st.button("Proceed to Dashboard", type="primary", use_container_width=True):
                if not name_input.strip(): st.error("Please enter your name before proceeding.")
                else:
                    st.session_state.user_name = name_input.strip()
                    st.session_state.age_group = selected_age
                    st.session_state.daily_goal = int(goal_input)
                    st.session_state.cup_capacity = int(cup_input)
                    st.session_state.bottle_capacity = int(bottle_input)
                    st.session_state.one_time_drink = int(one_time_input)
                    st.session_state.reminder_interval = int(interval_input)
                    st.session_state.wake_time = wake_input
                    st.session_state.sleep_time = sleep_input
                    st.session_state.setup_complete = True
                    save_persistent_state()
                    st.rerun()

# ==========================================
# SCREEN 2: MAIN HYDRATION DASHBOARD
# ==========================================
else:
    # Auto-refresh the app every 60 seconds
    st_autorefresh(interval=60000, limit=None, key="background_timer")

    total_intake = st.session_state.intake
    goal = st.session_state.daily_goal
    standard_target = AGE_GOALS[st.session_state.age_group]
    cup_cap = st.session_state.cup_capacity
    bottle_cap = st.session_state.bottle_capacity
    one_time_ml = st.session_state.one_time_drink
    interval_mins = int(st.session_state.reminder_interval)
    
    remaining = max(0, goal - total_intake)
    percentage = round((total_intake / goal) * 100, 1) if goal > 0 else 0.0
    std_pct = round((total_intake / standard_target) * 100, 1) if standard_target > 0 else 0.0

    # --- TOP BAR ---
    top_left, top_right = st.columns([3.2, 1], vertical_alignment="center")
    with top_left:
        st.header(f":blue[{st.session_state.user_name}'s] WaterBuddy")
        st.markdown(
            f":blue-background[**{st.session_state.age_group}**] | "
            f":violet-background[**Cup: {cup_cap} ml**] | "
            f":orange-background[**Remind Every: {interval_mins} mins**] | "
            f":green-background[**Wake: {st.session_state.wake_time.strftime('%I:%M %p')} - Sleep: {st.session_state.sleep_time.strftime('%I:%M %p')}**]"
        )
    with top_right:
        with st.popover(f"Profile: {st.session_state.user_name}", use_container_width=True):
            st.subheader("Edit Your Profile")
            new_name = st.text_input("Name:", value=st.session_state.user_name)
            new_age = st.selectbox("Age Group:", options=list(AGE_GOALS.keys()), index=list(AGE_GOALS.keys()).index(st.session_state.age_group))
            if new_age != st.session_state.age_group:
                st.session_state.age_group = new_age
                st.session_state.daily_goal = AGE_GOALS[new_age]
                save_persistent_state()
                st.rerun()
            new_goal = st.number_input("Personal Daily Target (ml):", min_value=500, max_value=6000, value=int(st.session_state.daily_goal), step=100)
            new_cup = st.number_input("1 Cup Capacity (ml):", min_value=50, max_value=1000, value=int(st.session_state.cup_capacity), step=25)
            new_bottle = st.number_input("1 Bottle Capacity (ml):", min_value=100, max_value=3000, value=int(st.session_state.bottle_capacity), step=50)
            new_one_time = st.number_input("Drink at One Time (ml):", min_value=50, max_value=1000, value=int(st.session_state.one_time_drink), step=25)
            new_interval = st.number_input("Remind me every (mins):", min_value=1, max_value=360, value=int(st.session_state.reminder_interval), step=1)
            new_wake = ampm_time_picker("Wake-Up Time:", st.session_state.wake_time, "pw")
            new_sleep = ampm_time_picker("Sleep Time:", st.session_state.sleep_time, "ps")
            
            if st.button("Save Changes", type="primary", use_container_width=True):
                if not new_name.strip(): st.error("Name cannot be empty.")
                else:
                    st.session_state.user_name = new_name.strip()
                    st.session_state.daily_goal = int(new_goal)
                    st.session_state.cup_capacity = int(new_cup)
                    st.session_state.bottle_capacity = int(new_bottle)
                    st.session_state.one_time_drink = int(new_one_time)
                    st.session_state.reminder_interval = int(new_interval)
                    st.session_state.wake_time = new_wake
                    st.session_state.sleep_time = new_sleep
                    save_persistent_state()
                    st.toast("Profile settings updated!")
                    st.rerun()
            if st.button("Back to Setup Screen", use_container_width=True):
                st.session_state.setup_complete = False
                save_persistent_state()
                st.rerun()
    st.divider()

    # ==========================================
    # 3-COLUMN DASHBOARD LAYOUT
    # ==========================================
    left_col, mid_col, right_col = st.columns([1.4, 1.2, 1.25], gap="medium")

    with left_col:
        m_c1, m_c2 = st.columns(2, gap="small")
        with m_c1:
            st.info(f"**Total Intake**\n### {total_intake} ml\n{round(total_intake / cup_cap, 1)} of your cups")
            rem_text = "Goal Reached!" if remaining == 0 else f"{round(remaining / cup_cap, 1)} cups left"
            st.warning(f"**Remaining Needed**\n### {remaining} ml\n{rem_text}")
        with m_c2:
            diff = goal - standard_target
            diff_text = "Matches age target" if diff == 0 else f"{diff:+d} ml vs age"
            st.success(f"**Daily Goal**\n### {goal} ml\n{diff_text}")
            ach_text = "100%+ Complete" if percentage >= 100 else f"{round(100 - percentage, 1)}% remaining"
            st.error(f"**Goal Achieved**\n### {percentage}%\n{ach_text}")

        mascot, headline, message = get_interactive_mascot(percentage, st.session_state.age_group, st.session_state.user_name)
        with st.container(border=True):
            mac_col1, mac_col2 = st.columns([1, 2.5], vertical_alignment="center")
            with mac_col1: st.title(mascot)
            with mac_col2: st.subheader(f":green[{headline}]")
            if percentage >= 100: st.success(message)
            else: st.info(message)
            st.divider()
            t_col1, t_col2 = st.columns([2.2, 1], vertical_alignment="center")
            with t_col1: st.markdown("**:violet[Daily Hydration Tip]**")
            with t_col2:
                if st.button("New Tip", use_container_width=True):
                    st.session_state.current_tip = random.choice(HYDRATION_TIPS)
                    save_persistent_state()
                    st.rerun()
            st.warning(st.session_state.current_tip)

    with mid_col:
        with st.container(border=True):
            st.subheader(":violet[Today's Intake Report]")
            if st.session_state.history:
                for entry in st.session_state.history[:4]: st.info(entry)
            else: st.info("No water logged yet today. Use the buttons to start.")
            if st.button("Reset Day & Start Fresh", use_container_width=True):
                reset_tracker()
                st.toast("Daily progress reset.")
                st.rerun()

        now = datetime.now()
        today = now.date()
        wake_dt = datetime.combine(today, st.session_state.wake_time)
        sleep_dt = datetime.combine(today, st.session_state.sleep_time)
        if sleep_dt < wake_dt:
            if now.time() < wake_dt.time(): wake_dt -= timedelta(days=1)
            else: sleep_dt += timedelta(days=1)

        first_reminder = wake_dt + timedelta(minutes=5)
        is_awake = wake_dt <= now < sleep_dt

        with st.container(border=True):
            st.subheader(":blue[Smart Reminders]")
            
            rem_toggle = st.toggle("Enable Automatic Reminders", value=st.session_state.reminders_enabled)
            if rem_toggle != st.session_state.reminders_enabled:
                st.session_state.reminders_enabled = rem_toggle
                save_persistent_state()

            # Direct Custom Reminder Time Selector on the Main Dashboard
            new_dash_interval = st.number_input(
                "Remind me after every (minutes):",
                min_value=1,
                max_value=360,
                value=interval_mins,
                step=1
            )
            if new_dash_interval != interval_mins:
                st.session_state.reminder_interval = int(new_dash_interval)
                interval_mins = int(new_dash_interval)
                save_persistent_state()
                st.rerun()

            if is_awake:
                if now < first_reminder:
                    next_reminder = first_reminder
                else:
                    delta_mins = (now - first_reminder).total_seconds() / 60.0
                    intervals_passed = int(delta_mins // interval_mins)
                    next_reminder = first_reminder + timedelta(minutes=(intervals_passed + 1) * interval_mins)
                    latest_passed = first_reminder + timedelta(minutes=intervals_passed * interval_mins)
                    
                    if st.session_state.reminders_enabled and remaining > 0:
                        if st.session_state.last_reminder_sent is None or latest_passed > st.session_state.last_reminder_sent:
                            trigger_voice_and_push_reminder(st.session_state.user_name, one_time_ml, remaining, goal)
                            st.session_state.last_reminder_sent = latest_passed
                            save_persistent_state()

                st.success(
                    f"**Status: Awake Window Active**\n\n"
                    f"First reminder: **{first_reminder.strftime('%I:%M %p')}** | Interval: **Every {interval_mins} min(s)**\n\n"
                    f"Next reminder at: **{next_reminder.strftime('%I:%M %p')}**"
                )
            else:
                st.warning(f"**Status: Sleep Hours Active**\n\nReminders paused until {st.session_state.wake_time.strftime('%I:%M %p')}.")

        with st.container(border=True):
            st.subheader(":orange[Cups to ml Converter]")
            st.caption(f"Based on your saved cup capacity ({cup_cap} ml):")
            num_cups = st.number_input("Number of Cups:", min_value=0.5, max_value=20.0, value=2.0, step=0.5)
            converted_ml = int(num_cups * cup_cap)
            st.warning(f"**{num_cups} cup(s)** = **{converted_ml} ml**")
            if st.button(f"Log {converted_ml} ml Now", type="primary", use_container_width=True):
                log_water(converted_ml, f"{num_cups} Cups")
                st.rerun()

    with right_col:
        with st.container(border=True):
            st.subheader(":green[Hydration Rings]")
            ring_image = draw_hydration_rings(percentage, std_pct)
            _, ring_col, _ = st.columns([0.2, 2, 0.2])
            with ring_col: st.image(ring_image, use_container_width=True)
            st.success(f"**Outer Green (Personal):** {percentage}% ({total_intake}/{goal} ml)")
            st.warning(f"**Inner Yellow (Age Goal):** {std_pct}% ({total_intake}/{standard_target} ml)")

        with st.container(border=True):
            st.subheader(":blue[Log Water Intake]")
            st.caption("Select your cup, bottle, or enter a custom amount:")
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"+1 Cup ({cup_cap} ml)", use_container_width=True):
                    log_water(cup_cap, "1 Cup")
                    st.rerun()
            with b2:
                if st.button(f"+1 Bottle ({bottle_cap} ml)", use_container_width=True):
                    log_water(bottle_cap, "1 Bottle")
                    st.rerun()
            c1, c2 = st.columns([1.8, 1], vertical_alignment="bottom")
            with c1: custom_ml = st.number_input("Custom amount (ml):", min_value=10, max_value=3000, value=300, step=50)
            with c2:
                if st.button("Add Custom", type="primary", use_container_width=True):
                    log_water(custom_ml, "Custom")
                    st.rerun()
