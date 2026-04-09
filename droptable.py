import sqlite3

conn = sqlite3.connect("tripplanner.db")
cursor = conn.cursor()

# drop table Table
cursor.execute("""
drop TABLE [Destination]""")

# Create Itinerary Table
cursor.execute("""
drop TABLE [Itinerary]""")

# Create Places Table
cursor.execute("""
drop TABLE [Places]""")

# Create Hotels Table
cursor.execute("""
drop TABLE [Hotels]""")

# Create Transport Table
cursor.execute("""
drop TABLE [Transport]""")


# Create Budegt Table
cursor.execute("""
drop TABLE [Budget]""")


conn.commit()
conn.close()

print("Tables Drop successfully!")