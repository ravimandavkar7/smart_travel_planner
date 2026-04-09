import sqlite3

conn = sqlite3.connect("tripplanner.db")
cursor = conn.cursor()

# Insert Destination
cursor.execute("""
INSERT INTO Destination ([DestinationId], [Destination], [State], [Country], [best_season], [avg_budget], [Description], [Min_day], [image_path]) VALUES (1,'Kedarnath','Uttarakhand', 'India','May-June','10000','Kedarnath Temple','5','images/Kedarnath.jpeg'),
(2,'Dwarka','Gujarat','India','October-March','8000','Dwarkadhish Temple','2','images/dwarka.jpeg')
""")

# Insert Itinerary
cursor.execute("""
INSERT INTO Itinerary ([ItineraryId], [DestinationId], [day_number], [title], [Description]) VALUES (1, 1, 1,'Arrival','Arrival at Haridwar In the morning and travel form Haridwar to Sonprayag and Sonprayag To Guarikund and Stay at Guarikund'),
(2, 1, 2,'Trakking','Early morning travel to Gaurikund
Start trek at 6:00 AM
Reach Kedarnath by evening (4–6 PM)
Stay near temple'),
(3, 1, 3,'Darshan And Return Trek','Morning Darshan at 6:00 AM to 3 PM and also visit nearst Bhairavnath Temple 
Return trek starts at 6PM
Reach Gaurikund and travel Gaurikund to Sonprayag reach night 11 PM stay at Sonprayag'),
(4, 1, 4,'Return Journy Sonprag To Haridwar','at moring 7AM Get Bus from Sonprayag To Haridwar,reach at Haridwar at night 7-8 PM Stay At Haridwar'),
(5, 1, 5,'Departure','take train from haridwar to your Destination')
""")

# Insert Places
cursor.execute("""
INSERT INTO Places ([PlacesId], [DestinationId], [place_name], [type], [rating], [description]) VALUES(1, 1,'Kedarnath','Temple', 5,'It is one of the four sites in the Chhota Char Dham pilgrimage and is also among the Panch Kedar temples.'),
(2, 1,'Bhairav Nath','Temple', 5,'Dedicated to the protector deity of the region, it is essential to visit and offers panoramic views of the temple and valley.')
""")

# Insert Hotels
cursor.execute("""
INSERT INTO Hotels ([HotelsId], [DestinationId], [hotel_name], [price_per_night], [rating], [location]) VALUES(1, 1,'Nandi Complex Base Camp','1100', 5,'Kedarnath')
""")

# Insert Budget
cursor.execute("""
INSERT INTO Budget ([BudgetId], [DestinationId], [avg_stay_cost], [avg_food_cost], [avg_travel_cost], [misc_cost]) VALUES(1, 1,'2500-3000 PP','2000-2500 PP','2000-2500 PP','500-1000 PP')
""")

# Insert Transport
cursor.execute("""
INSERT INTO Transport ([TransportId], [DestinationId], [mode], [source_city], [approx_cost], [duration]) VALUES(1, 1,'Bus','Haridwar','500-700','10-12 hrs')
,
(2, 1,'shared taxi','Haridwar','800-1200','8-10 hrs')
""")


conn.commit()
conn.close()

print("Data inserted!")