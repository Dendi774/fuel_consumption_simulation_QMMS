ROUTES = {
    "route_1": {
        "name": "baclaran to tambo",
        "distance_km": 3.2,
         
         "segments": [
            {'type': 'accelerate',  'distance': 200,  'label': 'Entering Roxas Blvd'},
            {'type': 'cruise',      'distance': 800,  'label': 'Roxas Blvd straight'},
            {'type': 'cruise',      'distance': 600,  'label': 'Roxas Blvd continued'},
            {'type': 'decelerate',  'distance': 80,   'target_speed': 8.3,
                                                       'label': 'Tambo turn approach'},
            {'type': 'turn',        'distance': 60,   'label': 'Into Tambo'},
            {'type': 'decelerate',  'distance': 100,  'target_speed': 0,
                                                       'label': 'Approaching terminal'},
         ]
    }
}