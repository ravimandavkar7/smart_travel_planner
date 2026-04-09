import sqlite3

conn = sqlite3.connect("tripplanner.db")
cursor = conn.cursor()

# Destination Table
cursor.execute("""
CREATE TABLE Destination (
    DestinationId INTEGER PRIMARY KEY AUTOINCREMENT,
    Destination TEXT,
    State TEXT,
    Country TEXT,
    best_season TEXT,
    avg_budget INTEGER,
    Description TEXT,
    createddate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Min_day INTEGER,
    image_path TEXT
)
""")

# Itinerary Table
cursor.execute("""
CREATE TABLE Itinerary (
    ItineraryId INTEGER PRIMARY KEY AUTOINCREMENT,
    DestinationId INTEGER,
    day_number INTEGER,
    title TEXT,
    Description TEXT,
    createddate DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Places Table
cursor.execute("""
CREATE TABLE Places (
    PlacesId INTEGER PRIMARY KEY AUTOINCREMENT,
    DestinationId INTEGER,
    place_name TEXT,
    type TEXT,
    rating REAL,
    description TEXT,
    createddate DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Hotels Table
cursor.execute("""
CREATE TABLE Hotels (
    HotelsId INTEGER PRIMARY KEY AUTOINCREMENT,
    DestinationId INTEGER,
    hotel_name TEXT,
    price_per_night REAL,
    rating REAL,
    location TEXT,
    createddate DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Transport Table
cursor.execute("""
CREATE TABLE Transport (
    TransportId INTEGER PRIMARY KEY AUTOINCREMENT,
    DestinationId INTEGER,
    mode TEXT,
    source_city TEXT,
    approx_cost REAL,
    duration TEXT,
    createddate DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Budget Table
cursor.execute("""
CREATE TABLE Budget (
    BudgetId INTEGER PRIMARY KEY AUTOINCREMENT,
    DestinationId INTEGER,
    avg_stay_cost REAL,
    avg_food_cost REAL,
    avg_travel_cost REAL,
    misc_cost REAL,
    createddate DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Database created successfully!")