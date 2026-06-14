ROUTES = {
    "route_1": {
        "name": "sucat to baclaran",
        "distance_km": 14.3,

        "segments": [
            {'type': 'accelerate',  'distance': 80,  'label': 'Sucat terminal departure - Dr. A. Santos Ave / SLEx service road'},
            {'type': 'decelerate',  'distance': 62.33,   'target_speed': "corner_speed",  'label': 'decelerate for U-turn at Dr. A. Santos Ave / SLEx service road junction'},
            {'type': 'turn',  'distance': 14.87, 'label': 'U-turn at Dr. A. Santos Ave / SLEx service road junction'},
            {'type': 'accelerate',  'distance': 80,  'label': 'Sucat terminal departure - Dr. A. Santos Ave / SLEx service road'},
            {'type': 'cruise',      'distance': 6490, 'label': 'from sucat to sm sucat'},
            {'type': 'decelerate',  'distance': 100,   'target_speed': "corner_speed",  'label': 'decelerate to turning speed to sm sucat'},
            {'type': 'turn',  'distance': 379.88, 'label': 'turning from sm sucat to dr. a santos ave'},
            {'type': 'accelerate',  'distance': 80,   'label': 'Re-accelerate after SM Sucat stop'},
            {'type': 'cruise',      'distance': 1110, 'label': 'Dr. A. Santos Ave - mid route with signalized intersections'},
            {'type': 'decelerate',  'distance': 100,   'target_speed': 'corner_speed',  'label': 'Intersection stop - Presidents Ave'},
            {"type": "turn", "distance": 91.96, "label": "turning from dr. a santos ave to Ninoy Aquino Ave"},
            {'type': 'accelerate',  'distance': 80,   'label': 'Re-accelerate after Ninoy Aquino Ave'},
            {"type": "cruise", "distance": 2170, "label": "Ninoy Aquino Ave - NAIA-adjacent heavy traffic"},
            {"type": "decelerate", "distance": 100, "target_speed": 'corner_speed', "label": "decelerate to turning speed to NAIA Road"},
            {"type": "accelerate", "distance": 80, "label": "turning from Ninoy Aquino Ave to NAIA Road"},
            {"type": "cruise", "distance": 1020, "label": "Cruise to roxas BLVD"},
            {"type": "decelerate", "distance": 100, "target_speed": "corner_speed", "label": "decelerate to turning speed to Roxas Blvd"},
            {"type": "turn", "distance": 30.29, "label": "turning from NAIA Road to Roxas Blvd"},
            {"type": "cruise", "distance": 2020, "label": "Cruise to Baclaran terminal"},
            {"type": "decelerate", "distance": 100, "target_speed": 'corner_speed', "label": "decelerate to stop at Baclaran terminal"},
            {"type": "turn", "distance": 20.75, "label": "turning to stop at Baclaran terminal"},
            {"type": "decelerate", "distance": 11.92, "target_speed": 0, "label": "decelerate to stop at Baclaran terminal"},
        ]
    },

    "route_2": {
        "name": "sucat to kabihasnan",
        "distance_km": 7.96,

        "segments": [
            {"type": "accelerate", "distance": 80, "label": "Baclaran Heritage Sucat Terminal departure"},
            {"type": "cruise", "distance": 6340, "label": "from sucat to sm sucat"},
            {"type": "decelerate", "distance": 100, "target_speed": "corner_speed", "label": "decelerate to turning speed to sm sucat"},
            {"type": "turn", "distance": 379.88, "label": "turning from sm sucat to dr. a santos ave"},
            {'type': 'accelerate',  'distance': 80,   'label': 'Re-accelerate after SM Sucat turn'},
            {"type": "cruise", "distance": 301.41, "label": "Cruising at Paranaque-Sucat Rd after SM Sucat Turn"},
            {"type": "decelerate", "distance": 100, "target_speed": 'corner_speed', "label": "Decelerating to turning speed to Victor Medina"},
            {"type": "accelerate", "distance": 80, "label": "turning from Paranaque-Sucat Rd to Victor Medina"},
            {"type": "cruise", "distance": 283.39, "label": "Cruising at Victor Medina"},
            {"type": "decelerate", "distance": 100, "target_speed": 'corner_speed', "label": "turning to kabihasnan Road"},
            {"type": "decelerate", "distance": 60, "target_speed": 0, "label": "Stopping at kabihasnan Road"},
        ]
    }
}



