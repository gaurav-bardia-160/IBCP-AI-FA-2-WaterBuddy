
# 💧 WaterBuddy: Your Daily Hydration Companion

[![Live App on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](YOUR_STREAMLIT_APP_LINK_HERE)
![Python](https://img.shields.io/badge/Python-3.12%2B-3B82F6?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production_Ready-22C55E?style=for-the-badge)

> **🌐 Live Web Application:** [**Click Here to Launch WaterBuddy on Streamlit Cloud **](https://ibcp-ai-fa-2-waterbuddy-6xcdcbzuh5jxrtrghaef2z.streamlit.app/)  


## 📖 Project Overview
**WaterBuddy** is an interactive, intelligent daily hydration companion developed in *Python** using **Streamlit**. WaterBuddy goes beyond static water counting by combining **age-based hydration benchmarks**, **progress rings**, **an interactive milestone mascot**, and a **sleep-aware custom reminder system with voice and push alerts**.

---

## 🎯 The Problem It Solves
1. **Chronic Mild Dehydration & Forgetfulness:** Students, professionals, and seniors frequently forget to drink water during busy study or work schedules, leading to fatigue, headaches, and reduced cognitive focus.
2. **One-Size-Fits-All Targets:** Many basic trackers use a generic `2000 ml` goal for everyone, ignoring physiological differences across age groups (kids, teens, adults, and seniors) or personal lifestyle targets.
3. **Standard Unit Confusion:** Users rarely know the exact milliliter (`ml`) volume of every sip—they drink from their own specific cups, glasses, and bottles.
4. **Disruptive Nighttime Alerts:** Traditional reminder apps send notifications at fixed hours even when the user is asleep.

**How WaterBuddy Solves This:**  
WaterBuddy personalizes hydration from the very first screen—calibrating goals by age group, adapting to the user's actual cup and bottle sizes, scheduling smart reminders strictly during the user's **awake window**, and persisting all progress automatically so data is never lost on refresh.

---

## 👥 Key Stakeholders & Target Audience

| Stakeholder Group | Role / Interest | How WaterBuddy Benefits Them |
| :--- | :--- | :--- |
| **🧒 Kids (6–12 yrs) & Teens (13–18 yrs)** | Primary End Users | Age-appropriate targets (`1600 ml` / `2200 ml`) and playful encouragement from **Shelly the Turtle** mascot at every milestone. |
| **🧑‍💻 Working Adults (19–50 yrs)** | Primary End Users | Customizable targets (`2500 ml` standard), custom-interval voice/push reminders during work hours, and 1-click cup/bottle logging. |
| **👵 Seniors (65+ yrs)** | Primary End Users | High-contrast dark UI, large readable metrics, gentle voice reminders, and safe hydration benchmarks (`2000 ml`). |

---

## ✨ Complete Feature Set

### 1. 🏠 Personalised Onboarding & Profile Management
* **Interactive Setup Screen:** Captures the user's **Name**, **Age Group**, **Personal Daily Water Target (ml)**, **Cup/Glass Capacity (ml)**, **Water Bottle Capacity (ml)**, **Single-Sip Capacity (ml)**, and **Wake/Sleep Schedule**.
* **Auto-Suggested Age Benchmarks:**
  * **Kids (6–12 years):** `1600 ml`
  * **Teens (13–18 years):** `2200 ml`
  * **Adults (19–50 years):** `2500 ml`
  * **Seniors (65+ years):** `2000 ml`
* **Top-Right Live Profile Popover:** Users can edit their name, age group, target, drinkware capacities, and reminder schedule anytime directly from the top-right profile menu.

### 2. 🟢🟡 Hydration Rings (Pure Python PIL Graphics)
* Dynamically drawn in real time using Python's **`Pillow (PIL.ImageDraw)`** library:
  * **Outer Green Ring:** Tracks progress toward the user's **Personal Daily Target**.
  * **Inner Yellow Ring:** Tracks progress against the **Recommended Age Group Benchmark**.
  * **Completion Checkmark (`✓`):** Automatically renders a crisp white checkmark inside the center of the rings once **100%** of the personal goal is achieved, accompanied by celebratory balloons.

### 3. 🐢 Interactive Milestone Mascot ("Shelly the Turtle")
Reacts live with age-aware motivational messages at exact completion milestones:
* **0% – 24% (`🐢💤`):** *Ready to Hydrate* — Waiting for the first sip of the day.
* **25% – 49% (`🐢😊`):** *25% Milestone: Great Start!* — Shelly wakes up and smiles.
* **50% – 74% (`🐢🌊`):** *50% Milestone: Halfway There!* — Swimming steadily toward the goal.
* **75% – 99% (`🐢🚀`):** *75% Milestone: Almost Done!* — Final stretch motivation.
* **100%+ (`🐢👑🎉`):** *100% Goal Achieved!* — Victory celebration!

### 4. 🔔 Smart Sleep-Aware Reminders (Voice + Push Notifications)
* **Custom 12-Hour AM/PM Time Picker:** Easy dropdown selectors for **Wake-Up Time** and **Sleep Time** (no confusing 24-hour clock).
* **Custom Reminder Interval (1–360 mins):** Users can choose the exact number of minutes between reminders on both the Setup Screen and the Main Dashboard.
* **5-Minute Wake-Up Buffer:** Schedules the first reminder **5 minutes after waking up** (e.g., wake at `08:45 AM` → first reminder at `08:50 AM`), then repeats at the user's chosen interval until sleep time.
* **Automatic Sleep Pause:** Automatically pauses all alerts during sleeping hours.
* **Voice & Desktop Push Alerts:** Speaks a personalized voice reminder out loud and triggers both an in-app toast notification and a desktop popup window.

### 5. 🥛 Custom Drinkware Logging & Cups-to-ml Converter
* **1-Click Drinkware Buttons:** Log `+1 Cup` or `+1 Bottle` using the user's exact saved capacities, or log any custom `ml` amount.
* **Live Cups ↔ ml Converter:** Converts any number of cups into milliliters based on the user's custom cup size and logs it with one click.
* **Today's Intake Report & Daily Reset:** Displays a timestamped history of drinks logged today and includes a **Reset Day & Start Fresh** button.

### 6. 💾 Automatic Data Persistence Across Browser Refreshes
* Built-in JSON state engine (`waterbuddy_state.json`) automatically saves profile settings, logged intake, drink history, and reminder states so **refreshing the browser (`F5`) never resets user progress**.

---

## 🎨 User Interface (UI) Design
* **Modern Dark Bento-Grid Layout:** Inspired by modern health dashboards with high-contrast midnight backgrounds (`#080C14`) and deep indigo cards (`#162238`).
* **Color-Coded Metric Tiles:**
  * 🟦 **Blue Tile:** Total Intake (`ml` + equivalent user cups)
  * 🟩 **Green Tile:** Daily Goal (`ml` + comparison against age standard)
  * 🟨 **Amber Tile:** Remaining Water Needed (`ml` + cups left)
  * 🟥 **Rose Tile:** Goal Achieved Percentage (`%`)
* **Daily Hydration Tips Card:** Provides actionable health tips with a **New Tip** generator button right on the main dashboard.

---

## 🛠️ Technologies Used
* **Language:** Python 3.12+
* **Web Framework:** [Streamlit](https://streamlit.io/)
* **Graphics Engine:** Pillow (`PIL.Image`, `PIL.ImageDraw`)
* **Background Timer:** `streamlit-autorefresh`
* **State Persistence:** `st.session_state` + Local `json` Storage

---
