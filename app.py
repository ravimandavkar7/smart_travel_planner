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

try:
    razorpay_client = razorpay.Client(
        auth=(
            st.secrets["RAZORPAY_KEY_ID"],
            st.secrets["RAZORPAY_SECRET"]
        )
    )
    

except Exception as e:
    st.error(f"Razorpay error: {e}")


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

def create_order(amount):
    order = razorpay_client.order.create({
        "amount": amount * 100,  # ₹49 → 4900
        "currency": "INR",
        "payment_capture": 1
    })
    return order


def verify_payment(payment_id):
    try:
        payment = razorpay_client.payment.fetch(payment_id)

        if payment["status"] == "captured" and payment["amount"] == 4900:
            return True
        else:
            return False

    except Exception as e:
        st.error(f"Verification error: {e}")
        return False



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

def generate_itinerary(destination, days, budget):
    try:
        prompt = f"""
        Create a {days}-day travel itinerary for {destination} in India.
        Budget: {budget} INR.
        Include day-wise plan, places to visit, and tips.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
    except Exception as e:
        return "⚠️ AI service not available. Please try again later."

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
h1, h2, h3, h4, h5, h6, p, div, span {
    color: white !important;
}
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
    [min_day, min_day + 1, min_day + 2]
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

ai_used = check_ai_used(st.session_state.user_id)

if "order_id" not in st.session_state:
    st.session_state.order_id = None

st.subheader("🤖 AI Itinerary (Premium Feature)")
st.warning("💎 AI Itinerary costs ₹49")


st.components.v1.html("""
<form><script src="https://checkout.razorpay.com/v1/payment-button.js" data-payment_button_id="pl_SfgzYZNF6xI9k4" async> </script> </form>""", height=500)


# STEP 2: Enter Payment ID
payment_id = st.text_input("🔑 Enter Payment ID after payment")

# STEP 3: Verify & Generate AI
if st.button("Verify Payment & Generate AI"):

    if not payment_id:
        st.error("❌ Enter payment ID")

    else:
        with st.spinner("Verifying payment..."):

            if verify_payment(payment_id):

                st.success("Payment verified ✅")
                with st.spinner("Generating AI Itinerary..."):

                    try:
                    

                        ai_result = generate_itinerary(selected, days, budget)

                        st.subheader("🤖 AI Generated Itinerary")
                        st.write(ai_result)

                        log_user_supabase(
                            st.session_state.user_id,
                            selected,
                            days,
                            budget,
                            1
                        )
                    except Exception as e:
                        st.error("❌ AI generation failed")
                        st.error(str(e))

            else:
                st.error("❌ Invalid or unpaid transaction")

	
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
            st.write(f"Day {i+1}: Free exploration")
    
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


    if selected == "Kedarnath":
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
                st.write(f"Price: ₹{hotel[1]} per night | Hotel Review Rating⭐: {hotel[2]} | location: {hotel[3]}")
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
    else:
         # 💰 Upsell model
        st.subheader("🏨 Hotels & Transport Planning")

        st.info(f"""
        💡 Based on your total budget of ₹{budget}, we will:
        
        ✔ We’ll help you find best hotels within {stay_budget} budget\n 
        ✔ Suggest best hotels within your budget\n 
        ✔ Plan transport (bus/train/flight)\n  
        ✔ Optimize your full trip cost\n  

        📩 Contact for personalized plan:
        📧 ravimandavkar7@gmail.com  
        📱 WhatsApp: +91-9167159485
        """)

