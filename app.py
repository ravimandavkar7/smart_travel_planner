import streamlit as st
import sqlite3
import base64
import os
from openai import OpenAI
import uuid
from supabase import create_client
import razorpay
import time

unique_link = f"https://rzp.io/rzp/v9eFBjz?{int(time.time())}"



def month_in_season(user_month, season_range):
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]

    try:
        start, end = season_range.split("-")
        start_idx = months.index(start)
        end_idx = months.index(end)

        # Case 1: normal range (April-June)
        if start_idx <= end_idx:
            valid_months = months[start_idx:end_idx+1]

        # Case 2: cross-year (October-March)
        else:
            valid_months = months[start_idx:] + months[:end_idx+1]

        return user_month in valid_months

    except:
        return False


if "show_ai_confirm" not in st.session_state:
    st.session_state.show_ai_confirm = False

if "use_ai" not in st.session_state:
    st.session_state.use_ai = False

if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
else:
    st.error("❌ Supabase secrets not found. Please check Streamlit Secrets.")


def check_ai_used(user_id):
    response = supabase.table("userlogs")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("used_ai", 1)\
        .execute()

    return len(response.data) > 0


def log_user(user_id, destination, days, budget, used_ai):
    supabase.table("userlogs").insert({
        "user_id": user_id,
        "destination": destination,
        "days": days,
        "budget": budget,
        "used_ai": used_ai
    }).execute()

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def set_bg(image_file):
    if not os.path.exists(image_file):
        st.warning(f"Image not found: {image_file}")
        return
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """, unsafe_allow_html=True)


conn = sqlite3.connect("tripplanner.db")

cursor = conn.cursor()

st.markdown("""
<style>

/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #111;
}

/* Labels (titles, text) */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown {
    color: white !important;
}

/* Input fields (VERY IMPORTANT FIX) */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] select {
    color: black !important;
    background-color: white !important;
}

</style>
""", unsafe_allow_html=True)


#for filter
st.sidebar.header("🔍 Find Best Destinations")

month = st.sidebar.selectbox(
    "Select Travel Month",
    ["January","February","March","April","May","June",
     "July","August","September","October","November","December"]
)

user_budget = st.sidebar.number_input(
    "Enter Your Budget (₹)",
    min_value=1000,
    step=1000
)

persons = st.sidebar.number_input(
    "👨‍👩‍👧 Number of Persons",
    min_value=1,
    step=1
)

per_person_budget = user_budget / persons

st.sidebar.info(f"💰 Per Person Budget: ₹{int(per_person_budget)}")

search_clicked = st.sidebar.button("🔎 Search")

if search_clicked:

    cursor.execute("""SELECT DISTINCT ds.Destination, ds.best_season FROM Destination ds JOIN AvgBudget ab ON ds.DestinationId = ab.DestinationId WHERE 
    ab.Budget <= ?""",(per_person_budget,))
    rows = cursor.fetchall()

    filtered_places = []

    for row in rows:
        name = row[0]
        season = row[1]
        avg_budget = row[2]

        if month_in_season(month, season) and avg_budget <= per_person_budget:
            filtered_places.append(name)

    st.sidebar.subheader("🌍 Recommended")

    if filtered_places:
        for place in filtered_places:
            st.sidebar.write(f"📍 {place}")
    else:
        st.sidebar.warning("No destinations found")


st.title("Smart Travel Planner ✈️")


# Dropdown from DB
cursor.execute("SELECT Destination FROM Destination")
destinations = [row[0] for row in cursor.fetchall()]

selected = st.selectbox("Select Destination", destinations)

cursor.execute("""
SELECT DestinationId, Min_day, avg_budget,image_path
FROM Destination
WHERE Destination=?
""", (selected,))

data = cursor.fetchone()

destination_id = data[0]
min_day = data[1]
avg_budget = data[2]
image_path=data[3]




# ✅ APPLY BACKGROUND HERE
set_bg(image_path)

# 1️⃣ Dark Overlay (handles any image)
st.markdown("""
<style>
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.75);
    z-index: 0;
}

.stApp > * {
    position: relative;
    z-index: 1;
}
</style>
""", unsafe_allow_html=True)


# 2️⃣ Main Content Container (MOST IMPORTANT)
st.markdown("""
<style>
.block-container {
    background-color: rgba(0, 0, 0, 0.6);
    padding: 2rem;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)


# 3️⃣ Force Text Color
st.markdown("""
<style>
h1, h2, h3, h4, h5, h6,  {
    color: white !important;
}
.stLinkButton p{ color: #000000}
div, span{
color: white 
}
.stLinkButton a:hover p{ color : white}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Selectbox background */
div[data-baseweb="select"] > div {
    background-color: rgba(0, 0, 0, 0.7) !important;
    color: white !important;
    border-radius: 10px;
}

/* Selected value text */
div[data-baseweb="select"] span {
    color: white !important;
}

/* Dropdown menu */
ul {
    background-color: black !important;
    color: white !important;
}

/* Dropdown items */
li {
    color: white !important;
}

/* Hover effect */
li:hover {
    background-color: rgba(255,255,255,0.2) !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Main button */
.stButton > button {
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: 1px solid white;
    font-weight: bold;
}

/* Hover effect */
.stButton > button:hover {
    background-color: white;
    color: black;
    border: 1px solid black;
}

/* Active (click) effect */
.stButton > button:active {
    background-color: #444;
    color: white;
}

</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>

/* Fix overall page spacing */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
    max-width: 800px;
    margin: auto;
}

/* Title styling */
h1 {
    text-align: center;
    margin-top: 0px !important;
    margin-bottom: 25px !important;
}

/* Reduce gap between elements */
div[data-testid="stVerticalBlock"] {
    gap: 0.8rem !important;
}

/* Reduce spacing between inputs */
div[data-testid="stSelectbox"],
div[data-testid="stNumberInput"] {
    margin-bottom: 0px !important;
}

/* Button spacing */
.stButton {
    margin-top: 15px;
}

</style>
""", unsafe_allow_html=True)





min_day = int(data[1])
days = st.selectbox(
    "Select Number of Days",
    [min_day]
)

avg_budget=int(data[2])
budget = st.selectbox(
    "Select Budget ₹",
    [avg_budget, avg_budget + 2000, avg_budget + 5000]
)


cursor.execute("""
SELECT day_number, Description
FROM Itinerary
WHERE DestinationId = ?
AND day_number <= ?
ORDER BY day_number
""",  (destination_id, days))

result = cursor.fetchall()

	
if st.button("Generate Plan"):

    log_user(st.session_state.user_id, selected, min_day, avg_budget, 0)

    cursor.execute("""
    select day_number,title,it.Description 
    from Itinerary it join Destination ds on(it.DestinationId=ds.DestinationId)
    WHERE Destination=?
    ORDER BY day_number
    """, (selected,))

    result = cursor.fetchall()

    st.subheader("Your Itinerary")

    for i in range(days):
        if i < len(result):
            st.write(f"Day {i+1}: {result[i][1]}: {result[i][2]}")
        else:
            st.warning(f"📅 Day {i+1}: 💎 Detailed plan available in Premium (₹299)")
       c
    stay_budget=budget * 0.4
    st.subheader("Budget Breakdown")
    st.write("Stay:", stay_budget)
    st.write("Travel:", budget * 0.3)
    st.write("Food:", budget * 0.2)
    st.write("Misc:", budget * 0.1)

    st.write(f"💡 Estimated hotel budget: ₹{stay_budget:.0f}")

    st.subheader("📍 Top Places to Visit")

    cursor.execute("""
    SELECT place_name,type,rating,description
    FROM Places
    WHERE DestinationId = ?
    """, (destination_id,))

    places = cursor.fetchall()

    for place in places:
        st.write(f"{place[0]} ({place[1]}) Place Rating ⭐{place[2]}: {place[3]}")


    st.subheader("🏨 Recommended Hotels")
    cursor.execute("""
    SELECT hotel_name,price_per_night,rating,location
    FROM Hotels
    WHERE DestinationId = ?
    """, (destination_id,))

    hotels = cursor.fetchall()
    nights = days - 1
    
    if nights <= 0:
        nights = 1
    
    per_night_budget = (budget * 0.4) / nights
   
    st.write(f"💡 Hotels under ₹{per_night_budget:.0f} per night")
    for hotel in hotels:
        price = float(hotel[1])
        
        if price <= per_night_budget:
            st.markdown(f"**🏨 {hotel[0]}**")
            st.write(f"Price: ₹{hotel[1]} per night per person | Hotel Review Rating⭐: {hotel[2]} | location: {hotel[3]}")
        else:
            st.write("Curruntly No Hotel is available in your Budget Kindly contact for Budget Hotel.")


    st.subheader("🚗 Travel Options")

    cursor.execute("""
    SELECT mode, source_city, approx_cost, duration
    FROM Transport
    WHERE DestinationId = ?
    """, (destination_id,))

    transport = cursor.fetchall()

    for t in transport:
        st.write(f"{t[0]} from {t[1]} - ₹{t[2]} ({t[3]})")
           
    st.subheader("💎 Premium Travel Planning")

    st.warning("Get 3–5 best hotels, contact numbers & transport guidance for Just ₹299")

    st.info("📲 Pay ₹299 and send screenshot on WhatsApp")

    st.link_button(
        "📞 Contact on WhatsApp",
        "https://wa.me/919167159485"
    )

    st.info(f"""
    💡 Based on your total budget of ₹{budget}, we will:
     
    🏨 **Find best hotels within your budget ({stay_budget})**\n 
    📞 **Share verified hotel contact details**\n 
    🚆 **Plan transport (bus/train/flight)**\n  
    💰 **Optimize your complete trip cost**\n  
    """)


st.info("""
💬 Didn’t find your destination?

📲 Contact us on WhatsApp — we’ll provide basic travel guidance for FREE.
""")

st.link_button("📲 Chat on WhatsApp", "https://wa.me/919167159485")
