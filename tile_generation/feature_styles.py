"""Feature styling definitions ported from original build-toronto-tiles.py"""

# Complete feature styling configuration from the original script
FEATURE_STYLES = {
    'buildings': {
        'tags': {'building': True},
        'styles': {
            # Residential buildings
            'house': {'fill': '#d4c5b9', 'stroke': '#a69b8c', 'stroke_width': 1},
            'residential': {'fill': '#d4c5b9', 'stroke': '#a69b8c', 'stroke_width': 1},
            'apartments': {'fill': '#d4c5b9', 'stroke': '#a69b8c', 'stroke_width': 1},
            'detached': {'fill': '#d4c5b9', 'stroke': '#a69b8c', 'stroke_width': 1},
            'semidetached_house': {'fill': '#d4c5b9', 'stroke': '#a69b8c', 'stroke_width': 1},
            'terrace': {'fill': '#d4c5b9', 'stroke': '#a69b8c', 'stroke_width': 1},
            'dormitory': {'fill': '#dcc5b9', 'stroke': '#b3a08c', 'stroke_width': 1},
            'bungalow': {'fill': '#d4c5b9', 'stroke': '#a69b8c', 'stroke_width': 1},
            'cabin': {'fill': '#c4b5a9', 'stroke': '#96897c', 'stroke_width': 1},
            
            # Commercial buildings
            'commercial': {'fill': '#e6cccc', 'stroke': '#cc9999', 'stroke_width': 1},
            'office': {'fill': '#d9d0c9', 'stroke': '#b3a69c', 'stroke_width': 1},
            'industrial': {'fill': '#dcd5cc', 'stroke': '#b3a999', 'stroke_width': 1},
            'retail': {'fill': '#e6cccc', 'stroke': '#cc9999', 'stroke_width': 1},
            'warehouse': {'fill': '#e5ddd5', 'stroke': '#ccbbaa', 'stroke_width': 1},
            'supermarket': {'fill': '#ffcccc', 'stroke': '#ff9999', 'stroke_width': 1.5},
            'hotel': {'fill': '#e6d5cc', 'stroke': '#ccaa99', 'stroke_width': 1.5},
            'kiosk': {'fill': '#dcc5b9', 'stroke': '#b3a08c', 'stroke_width': 1},
            
            # Public buildings
            'civic': {'fill': '#d4d5e8', 'stroke': '#a9aac4', 'stroke_width': 2},
            'government': {'fill': '#d4d5e8', 'stroke': '#a9aac4', 'stroke_width': 2},
            'hospital': {'fill': '#fdd', 'stroke': '#da8', 'stroke_width': 2},
            'school': {'fill': '#f0e5d8', 'stroke': '#ccb399', 'stroke_width': 2},
            'university': {'fill': '#f0e5d8', 'stroke': '#ccb399', 'stroke_width': 2},
            'college': {'fill': '#f0e5d8', 'stroke': '#ccb399', 'stroke_width': 2},
            'kindergarten': {'fill': '#ffe5cc', 'stroke': '#ffcc99', 'stroke_width': 1.5},
            'public': {'fill': '#d4d5e8', 'stroke': '#a9aac4', 'stroke_width': 1.5},
            'train_station': {'fill': '#d4c5e8', 'stroke': '#a99bc4', 'stroke_width': 2},
            'transportation': {'fill': '#d4c5e8', 'stroke': '#a99bc4', 'stroke_width': 1.5},
            
            # Religious buildings
            'cathedral': {'fill': '#e6d9ff', 'stroke': '#ccb3ff', 'stroke_width': 2},
            'chapel': {'fill': '#e6d9ff', 'stroke': '#ccb3ff', 'stroke_width': 1.5},
            'church': {'fill': '#e6d9ff', 'stroke': '#ccb3ff', 'stroke_width': 2},
            'mosque': {'fill': '#d9ffe6', 'stroke': '#b3ffcc', 'stroke_width': 2},
            'temple': {'fill': '#ffe6d9', 'stroke': '#ffccb3', 'stroke_width': 2},
            'synagogue': {'fill': '#d9e6ff', 'stroke': '#b3ccff', 'stroke_width': 2},
            'shrine': {'fill': '#ffd9e6', 'stroke': '#ffb3cc', 'stroke_width': 1.5},
            
            # Special structures
            'barn': {'fill': '#d4a76a', 'stroke': '#b58652', 'stroke_width': 1},
            'bridge': {'fill': '#b8b8b8', 'stroke': '#888', 'stroke_width': 2},
            'bunker': {'fill': '#999', 'stroke': '#666', 'stroke_width': 2},
            'carport': {'fill': '#ddd', 'stroke': '#aaa', 'stroke_width': 1},
            'conservatory': {'fill': '#eeffee', 'stroke': '#aaccaa', 'stroke_width': 1},
            'construction': {'fill': '#ffcc99', 'stroke': '#ff9966', 'stroke_width': 1, 'dasharray': '5,3'},
            'garage': {'fill': '#ddd', 'stroke': '#aaa', 'stroke_width': 1},
            'garages': {'fill': '#ddd', 'stroke': '#aaa', 'stroke_width': 1},
            'greenhouse': {'fill': '#eeffee', 'stroke': '#aaccaa', 'stroke_width': 1},
            'hangar': {'fill': '#d5d5e8', 'stroke': '#aaaac4', 'stroke_width': 1.5},
            'hut': {'fill': '#c4b5a9', 'stroke': '#96897c', 'stroke_width': 1},
            'roof': {'fill': '#ddd', 'stroke': '#aaa', 'stroke_width': 0.5},
            'shed': {'fill': '#c4b5a9', 'stroke': '#96897c', 'stroke_width': 1},
            
            # Default building style
            'yes': {'fill': '#8e9aaf', 'stroke': '#5d6674', 'stroke_width': 1},
            'default': {'fill': '#8e9aaf', 'stroke': '#5d6674', 'stroke_width': 1}
        }
    },
    'roads': {
        'tags': {'highway': ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 
                             'residential', 'service', 'unclassified', 'pedestrian', 
                             'footway', 'cycleway', 'path', 'living_street', 'track',
                             'bus_guideway', 'escape', 'raceway', 'road', 'busway',
                             'motorway_link', 'trunk_link', 'primary_link', 
                             'secondary_link', 'tertiary_link', 'bridleway', 'steps',
                             'corridor', 'sidewalk']},
        'styles': {
            # Major roads
            'motorway': {'width': 8, 'color': '#e892a2', 'casing': '#dc2a67', 'casing_width': 10},
            'trunk': {'width': 7, 'color': '#f9b29c', 'casing': '#e06d5f', 'casing_width': 9},
            'primary': {'width': 6, 'color': '#fcd6a4', 'casing': '#e5c278', 'casing_width': 8},
            'secondary': {'width': 5, 'color': '#f7fabf', 'casing': '#d4d486', 'casing_width': 7},
            'tertiary': {'width': 4, 'color': '#ffffff', 'casing': '#bbb', 'casing_width': 6},
            # Links/ramps
            'motorway_link': {'width': 4, 'color': '#e892a2', 'casing': '#dc2a67', 'casing_width': 5},
            'trunk_link': {'width': 4, 'color': '#f9b29c', 'casing': '#e06d5f', 'casing_width': 5},
            'primary_link': {'width': 4, 'color': '#fcd6a4', 'casing': '#e5c278', 'casing_width': 5},
            'secondary_link': {'width': 3, 'color': '#f7fabf', 'casing': '#d4d486', 'casing_width': 4},
            'tertiary_link': {'width': 3, 'color': '#ffffff', 'casing': '#bbb', 'casing_width': 4},
            # Streets
            'residential': {'width': 3, 'color': '#ffffff', 'casing': '#999', 'casing_width': 5},
            'living_street': {'width': 3, 'color': '#f0f0f0', 'casing': '#999', 'casing_width': 5, 'dasharray': '10,3'},
            'service': {'width': 2, 'color': '#ffffff', 'casing': '#aaa', 'casing_width': 3},
            'unclassified': {'width': 3, 'color': '#ffffff', 'casing': '#999', 'casing_width': 5},
            'road': {'width': 2, 'color': '#dddddd', 'casing': '#999', 'casing_width': 3},
            # Pedestrian/bike
            'pedestrian': {'width': 3, 'color': '#ededed', 'casing': '#ccc', 'casing_width': 4},
            'footway': {'width': 1.5, 'color': '#faa', 'casing': '#f88', 'casing_width': 2, 'dasharray': '2,3'},
            'sidewalk': {'width': 1.5, 'color': '#faa', 'casing': '#f88', 'casing_width': 2},
            'cycleway': {'width': 1.5, 'color': '#aaf', 'casing': '#88f', 'casing_width': 2, 'dasharray': '2,3'},
            'path': {'width': 1, 'color': '#ccc', 'casing': '#aaa', 'casing_width': 1.5, 'dasharray': '2,2'},
            'bridleway': {'width': 2, 'color': '#d4a76a', 'casing': '#b58652', 'casing_width': 3, 'dasharray': '4,2'},
            'steps': {'width': 3, 'color': '#faa', 'casing': '#f88', 'casing_width': 4, 'dasharray': '1,1'},
            'corridor': {'width': 2, 'color': '#ffcccc', 'casing': '#ff9999', 'casing_width': 3},
            # Special purpose
            'track': {'width': 2, 'color': '#dfb', 'casing': '#9d7', 'casing_width': 3, 'dasharray': '3,3'},
            'bus_guideway': {'width': 4, 'color': '#6682ff', 'casing': '#4666ff', 'casing_width': 5},
            'busway': {'width': 4, 'color': '#6682ff', 'casing': '#4666ff', 'casing_width': 5},
            'escape': {'width': 3, 'color': '#ff9999', 'casing': '#ff6666', 'casing_width': 4, 'dasharray': '5,5'},
            'raceway': {'width': 4, 'color': '#ffcccc', 'casing': '#ff9999', 'casing_width': 5}
        }
    },
    'accessibility': {
        'tags': {
            'amenity': ['parking'],
            'wheelchair': ['yes'],
            'access': ['disabled']
        },
        'styles': {
            'wheelchair_parking': {'fill': '#e8f5e8', 'stroke': '#4caf50', 'stroke_width': 2},
            'disabled_access': {'fill': '#e3f2fd', 'stroke': '#2196f3', 'stroke_width': 2},
            'default': {'fill': '#f1f8e9', 'stroke': '#689f38', 'stroke_width': 1.5}
        }
    },
    'transit': {
        'tags': {
            'highway': ['bus_stop', 'platform', 'bus_guideway'],
            'railway': ['station', 'halt', 'platform', 'subway', 'tram', 'tram_stop', 'stop', 'subway_entrance',
                       'rail', 'light_rail', 'narrow_gauge', 'funicular', 'monorail'],
            'public_transport': ['platform', 'stop_position', 'station'],
            'amenity': ['bus_station', 'ferry_terminal'],
            'aerialway': ['station', 'loading_point', 'cable_car', 'gondola', 'chair_lift', 'drag_lift', 'rope_tow', 'zip_line'],
            'aeroway': ['terminal', 'gate', 'runway', 'taxiway', 'aerodrome']
        },
        'styles': {
            # Bus Infrastructure
            'bus_stop': {'fill': '#ff9800', 'stroke': '#ff6600', 'stroke_width': 2, 'radius': 5},
            'bus_station': {'fill': '#ff5722', 'stroke': '#d84315', 'stroke_width': 2.5, 'radius': 12},
            'bus_guideway': {'color': '#ff7043', 'width': 4, 'stroke_dasharray': '8,4'},
            
            # Railway Infrastructure  
            'station': {'fill': '#9c27b0', 'stroke': '#7b1fa2', 'stroke_width': 2.5, 'radius': 10},
            'halt': {'fill': '#ba68c8', 'stroke': '#9c27b0', 'stroke_width': 2, 'radius': 6},
            'subway_entrance': {'fill': '#2196f3', 'stroke': '#1976d2', 'stroke_width': 2, 'radius': 6},
            'rail': {'color': '#424242', 'width': 3},
            'subway': {'color': '#1976d2', 'width': 4, 'stroke_dasharray': '12,4'},
            'tram': {'color': '#00bcd4', 'width': 2.5},
            'tram_stop': {'fill': '#00bcd4', 'stroke': '#0097a7', 'stroke_width': 2, 'radius': 5},
            'light_rail': {'color': '#4caf50', 'width': 3},
            'narrow_gauge': {'color': '#795548', 'width': 2},
            'funicular': {'color': '#ff5722', 'width': 2.5, 'stroke_dasharray': '6,2'},
            'monorail': {'color': '#e91e63', 'width': 3.5},
            
            # Public Transport
            'platform': {'fill': '#ffc107', 'stroke': '#ff8f00', 'stroke_width': 1.5},
            'stop_position': {'fill': '#ffeb3b', 'stroke': '#fbc02d', 'stroke_width': 1.5, 'radius': 3},
            
            # Water Transport
            'ferry_terminal': {'fill': '#607d8b', 'stroke': '#455a64', 'stroke_width': 2, 'radius': 8},
            
            # Aerial Transport
            'cable_car': {'color': '#795548', 'width': 2, 'stroke_dasharray': '4,8'},
            'gondola': {'color': '#8bc34a', 'width': 2, 'stroke_dasharray': '4,8'},
            'chair_lift': {'color': '#cddc39', 'width': 1.5, 'stroke_dasharray': '3,6'},
            'drag_lift': {'color': '#ffeb3b', 'width': 1.5, 'stroke_dasharray': '2,4'},
            'rope_tow': {'color': '#ffc107', 'width': 1, 'stroke_dasharray': '2,2'},
            'zip_line': {'color': '#ff9800', 'width': 1.5, 'stroke_dasharray': '6,2'},
            'aerialway_station': {'fill': '#8bc34a', 'stroke': '#689f38', 'stroke_width': 2, 'radius': 7},
            'loading_point': {'fill': '#cddc39', 'stroke': '#9e9d24', 'stroke_width': 1.5, 'radius': 4},
            
            # Airport Infrastructure
            'terminal': {'fill': '#3f51b5', 'stroke': '#303f9f', 'stroke_width': 2.5, 'radius': 15},
            'gate': {'fill': '#5c6bc0', 'stroke': '#3f51b5', 'stroke_width': 1.5, 'radius': 4},
            'runway': {'fill': '#424242', 'stroke': '#212121', 'stroke_width': 2},
            'taxiway': {'fill': '#616161', 'stroke': '#424242', 'stroke_width': 1},
            'aerodrome': {'fill': '#e8eaf6', 'stroke': '#3f51b5', 'stroke_width': 2},
            
            # Default
            'default': {'fill': '#ff9800', 'stroke': '#ff6600', 'stroke_width': 2, 'radius': 5}
        }
    },
    'water': {
        'tags': {
            # Large Water Bodies
            'natural': ['water', 'bay', 'strait', 'coastline', 'beach', 'shoal', 'reef', 'wetland', 
                       'spring', 'hot_spring', 'geyser'],
            # Linear Water Features
            'waterway': ['river', 'stream', 'canal', 'drain', 'ditch', 'rapids', 'waterfall', 
                        'dam', 'weir', 'lock_gate', 'dock', 'boatyard', 'fuel'],
            # Man-made Water Features
            'amenity': ['fountain', 'swimming_pool'],
            'man_made': ['reservoir', 'water_tower', 'water_well', 'water_works', 'pier', 
                        'breakwater', 'groyne', 'lighthouse', 'floating_dock'],
            # Leisure Water Features
            'leisure': ['swimming_pool', 'water_park', 'marina', 'slipway', 'boat_sharing'],
            # Landuse Water Areas
            'landuse': ['reservoir', 'salt_pond', 'aquaculture', 'basin']
        },
        'styles': {
            # Large Water Bodies
            'water': {'fill': '#aad3df', 'stroke': '#4a80aa', 'stroke_width': 1},
            'bay': {'fill': '#87ceeb', 'stroke': '#4682b4', 'stroke_width': 1.5},
            'strait': {'fill': '#87ceeb', 'stroke': '#4682b4', 'stroke_width': 1.5},
            'coastline': {'color': '#2e5984', 'width': 2},
            'beach': {'fill': '#fff8dc', 'stroke': '#daa520', 'stroke_width': 1},
            'shoal': {'fill': '#e6f3ff', 'stroke': '#87ceeb', 'stroke_width': 1, 'opacity': 0.7},
            'reef': {'fill': '#ffcccb', 'stroke': '#ff6347', 'stroke_width': 1.5},
            'wetland': {'fill': '#b8e6b8', 'stroke': '#228b22', 'stroke_width': 1, 'pattern': 'wetland'},
            
            # Springs and Geothermal
            'spring': {'fill': '#00ffff', 'stroke': '#0080ff', 'stroke_width': 2, 'radius': 4},
            'hot_spring': {'fill': '#ff6b6b', 'stroke': '#ff3333', 'stroke_width': 2, 'radius': 5},
            'geyser': {'fill': '#ffa500', 'stroke': '#ff8c00', 'stroke_width': 2.5, 'radius': 6},
            
            # Linear Water Features
            'river': {'color': '#4a80aa', 'width': 4},
            'stream': {'color': '#6a90ba', 'width': 2},
            'canal': {'color': '#4a80aa', 'width': 3},
            'drain': {'color': '#708090', 'width': 1.5, 'stroke_dasharray': '4,2'},
            'ditch': {'color': '#708090', 'width': 1, 'stroke_dasharray': '2,2'},
            'rapids': {'color': '#ffffff', 'width': 3, 'stroke_dasharray': '2,1'},
            'waterfall': {'fill': '#e0f6ff', 'stroke': '#0080ff', 'stroke_width': 3, 'radius': 8},
            
            # Water Infrastructure
            'dam': {'fill': '#696969', 'stroke': '#2f4f4f', 'stroke_width': 3},
            'weir': {'fill': '#708090', 'stroke': '#2f4f4f', 'stroke_width': 2},
            'lock_gate': {'fill': '#8b4513', 'stroke': '#654321', 'stroke_width': 2, 'radius': 6},
            'reservoir': {'fill': '#b0e0e6', 'stroke': '#4682b4', 'stroke_width': 1.5},
            'water_tower': {'fill': '#c0c0c0', 'stroke': '#808080', 'stroke_width': 2, 'radius': 10},
            'water_well': {'fill': '#8b4513', 'stroke': '#654321', 'stroke_width': 2, 'radius': 4},
            'water_works': {'fill': '#87ceeb', 'stroke': '#4682b4', 'stroke_width': 2},
            
            # Marine Infrastructure
            'dock': {'fill': '#8b4513', 'stroke': '#654321', 'stroke_width': 2},
            'boatyard': {'fill': '#deb887', 'stroke': '#d2691e', 'stroke_width': 1.5},
            'fuel': {'fill': '#ff6347', 'stroke': '#ff4500', 'stroke_width': 2, 'radius': 6},
            'pier': {'fill': '#8b4513', 'stroke': '#654321', 'stroke_width': 2},
            'breakwater': {'fill': '#696969', 'stroke': '#2f4f4f', 'stroke_width': 2.5},
            'groyne': {'fill': '#708090', 'stroke': '#2f4f4f', 'stroke_width': 2},
            'lighthouse': {'fill': '#ff0000', 'stroke': '#8b0000', 'stroke_width': 2.5, 'radius': 8},
            'floating_dock': {'fill': '#daa520', 'stroke': '#b8860b', 'stroke_width': 1.5},
            
            # Recreation Water Features
            'fountain': {'fill': '#87ceeb', 'stroke': '#4682b4', 'stroke_width': 2, 'radius': 5},
            'swimming_pool': {'fill': '#00bfff', 'stroke': '#0080ff', 'stroke_width': 2},
            'water_park': {'fill': '#40e0d0', 'stroke': '#20b2aa', 'stroke_width': 2},
            'marina': {'fill': '#f0e68c', 'stroke': '#bdb76b', 'stroke_width': 1.5},
            'slipway': {'fill': '#bc8f8f', 'stroke': '#a0522d', 'stroke_width': 2},
            'boat_sharing': {'fill': '#87ceeb', 'stroke': '#4682b4', 'stroke_width': 1.5, 'radius': 6},
            
            # Specialized Water Areas
            'salt_pond': {'fill': '#ffc0cb', 'stroke': '#ff69b4', 'stroke_width': 1},
            'aquaculture': {'fill': '#add8e6', 'stroke': '#4682b4', 'stroke_width': 1, 'pattern': 'grid'},
            'basin': {'fill': '#b0e0e6', 'stroke': '#4682b4', 'stroke_width': 1},
            
            # Default
            'default': {'fill': '#aad3df', 'stroke': '#4a80aa', 'stroke_width': 1}
        }
    },
    'parks': {
        'tags': {
            'leisure': ['park', 'garden', 'playground', 'dog_park', 'nature_reserve'],
            'landuse': ['grass', 'recreation_ground', 'village_green']
        },
        'styles': {
            'park': {'fill': '#c8e6c9', 'stroke': '#4caf50', 'stroke_width': 1},
            'garden': {'fill': '#dcedc8', 'stroke': '#689f38', 'stroke_width': 1},
            'playground': {'fill': '#ffecb3', 'stroke': '#ffa000', 'stroke_width': 1.5},
            'dog_park': {'fill': '#fff3e0', 'stroke': '#f57c00', 'stroke_width': 1},
            'nature_reserve': {'fill': '#e8f5e8', 'stroke': '#2e7d32', 'stroke_width': 1.5},
            'grass': {'fill': '#e8f5e8', 'stroke': '#81c784', 'stroke_width': 0.5},
            'default': {'fill': '#c8e6c9', 'stroke': '#4caf50', 'stroke_width': 1}
        }
    },
    
    'healthcare': {
        'tags': {'amenity': ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy', 'veterinary'],
                 'healthcare': ['alternative', 'audiologist', 'birthing_centre', 'blood_bank', 
                               'blood_donation', 'centre', 'clinic', 'counselling', 'dentist',
                               'dialysis', 'doctor', 'hospice', 'hospital', 'laboratory',
                               'midwife', 'nurse', 'occupational_therapist', 'optometrist',
                               'pharmacy', 'physiotherapist', 'podiatrist', 'psychotherapist',
                               'rehabilitation', 'sample_collection', 'speech_therapist',
                               'vaccination_centre']},
        'styles': {
            # Major Healthcare Facilities (amenity-based)
            'hospital': {'fill': '#ffccdd', 'stroke': '#cc5577', 'stroke_width': 2.5, 'radius': 8},
            'clinic': {'fill': '#ffe0e0', 'stroke': '#cc7777', 'stroke_width': 2, 'radius': 6},
            'doctors': {'fill': '#ffe8e8', 'stroke': '#cc8888', 'stroke_width': 1.5, 'radius': 5},
            'dentist': {'fill': '#f0e8ff', 'stroke': '#9966cc', 'stroke_width': 1.5, 'radius': 5},
            'pharmacy': {'fill': '#e0ffe0', 'stroke': '#66cc66', 'stroke_width': 2, 'radius': 6},
            'veterinary': {'fill': '#fff0e0', 'stroke': '#cc9966', 'stroke_width': 1.5, 'radius': 5},
            
            # Specialized Healthcare (healthcare-based)
            'alternative': {'fill': '#f8f0ff', 'stroke': '#aa88cc', 'stroke_width': 1, 'radius': 4},
            'audiologist': {'fill': '#fff8f0', 'stroke': '#ccaa88', 'stroke_width': 1, 'radius': 4},
            'birthing_centre': {'fill': '#fff0f8', 'stroke': '#cc88aa', 'stroke_width': 2, 'radius': 6},
            'blood_bank': {'fill': '#ffe0e0', 'stroke': '#cc6666', 'stroke_width': 2, 'radius': 6},
            'blood_donation': {'fill': '#ffe8e8', 'stroke': '#cc7777', 'stroke_width': 1.5, 'radius': 5},
            'centre': {'fill': '#ffe0f0', 'stroke': '#cc7799', 'stroke_width': 2, 'radius': 6},
            'counselling': {'fill': '#f0f0ff', 'stroke': '#7799cc', 'stroke_width': 1.5, 'radius': 5},
            'dialysis': {'fill': '#e0f0ff', 'stroke': '#6699cc', 'stroke_width': 2, 'radius': 6},
            'hospice': {'fill': '#f8f8f0', 'stroke': '#aaaa88', 'stroke_width': 2, 'radius': 6},
            'laboratory': {'fill': '#f0fff0', 'stroke': '#88cc88', 'stroke_width': 1.5, 'radius': 5},
            'midwife': {'fill': '#fff0f8', 'stroke': '#cc88aa', 'stroke_width': 1.5, 'radius': 5},
            'nurse': {'fill': '#f0f8ff', 'stroke': '#88aacc', 'stroke_width': 1, 'radius': 4},
            'occupational_therapist': {'fill': '#f8fff0', 'stroke': '#aacc88', 'stroke_width': 1, 'radius': 4},
            'optometrist': {'fill': '#fff8f8', 'stroke': '#ccaaaa', 'stroke_width': 1.5, 'radius': 5},
            'physiotherapist': {'fill': '#f0fff8', 'stroke': '#88ccaa', 'stroke_width': 1.5, 'radius': 5},
            'podiatrist': {'fill': '#fff0f0', 'stroke': '#cc8888', 'stroke_width': 1, 'radius': 4},
            'psychotherapist': {'fill': '#f8f0ff', 'stroke': '#aa88cc', 'stroke_width': 1.5, 'radius': 5},
            'rehabilitation': {'fill': '#f0f8ff', 'stroke': '#88aacc', 'stroke_width': 2, 'radius': 6},
            'sample_collection': {'fill': '#f8fff8', 'stroke': '#aaccaa', 'stroke_width': 1, 'radius': 4},
            'speech_therapist': {'fill': '#fff8f0', 'stroke': '#ccaa88', 'stroke_width': 1, 'radius': 4},
            'vaccination_centre': {'fill': '#e0ffe0', 'stroke': '#66cc66', 'stroke_width': 2, 'radius': 6},
            
            # Default healthcare style
            'default': {'fill': '#ffe0e0', 'stroke': '#cc6666', 'stroke_width': 1.5, 'radius': 5}
        }
    },
    
    'food_sustenance': {
        'tags': {
            # Basic Food Amenities
            'amenity': ['restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court', 'ice_cream', 
                       'biergarten', 'nightclub'],
            # Specialized Food Shops
            'shop': ['alcohol', 'bakery', 'beverages', 'butcher', 'cheese', 'chocolate', 'coffee',
                    'confectionery', 'convenience', 'deli', 'farm', 'frozen_food', 'greengrocer',
                    'health_food', 'nuts', 'pastry', 'seafood', 'tea', 'wine', 'supermarket']
        },
        'styles': {
            # Basic Food Amenities - Warm orange/red palette for dining
            'restaurant': {'fill': '#ffcc80', 'stroke': '#ff8a65', 'stroke_width': 2, 'radius': 6},
            'cafe': {'fill': '#d7ccc8', 'stroke': '#8d6e63', 'stroke_width': 1.5, 'radius': 5},
            'fast_food': {'fill': '#ffab91', 'stroke': '#ff5722', 'stroke_width': 1.5, 'radius': 5},
            'bar': {'fill': '#ce93d8', 'stroke': '#9c27b0', 'stroke_width': 2, 'radius': 5},
            'pub': {'fill': '#ddbf94', 'stroke': '#8d6e63', 'stroke_width': 2, 'radius': 6},
            'food_court': {'fill': '#ffcc80', 'stroke': '#ff8a65', 'stroke_width': 2.5, 'radius': 8},
            'ice_cream': {'fill': '#f8bbd9', 'stroke': '#e91e63', 'stroke_width': 1.5, 'radius': 4},
            'biergarten': {'fill': '#c8e6c9', 'stroke': '#4caf50', 'stroke_width': 2, 'radius': 7},
            'nightclub': {'fill': '#b39ddb', 'stroke': '#673ab7', 'stroke_width': 2, 'radius': 6},
            
            # Grocery & General Food Stores - Green palette for fresh/healthy
            'supermarket': {'fill': '#a5d6a7', 'stroke': '#4caf50', 'stroke_width': 2.5, 'radius': 8},
            'convenience': {'fill': '#c5e1a5', 'stroke': '#689f38', 'stroke_width': 2, 'radius': 6},
            'greengrocer': {'fill': '#81c784', 'stroke': '#388e3c', 'stroke_width': 2, 'radius': 5},
            'farm': {'fill': '#aed581', 'stroke': '#689f38', 'stroke_width': 2, 'radius': 6},
            'health_food': {'fill': '#c8e6c9', 'stroke': '#4caf50', 'stroke_width': 1.5, 'radius': 5},
            'frozen_food': {'fill': '#b3e5fc', 'stroke': '#03a9f4', 'stroke_width': 1.5, 'radius': 5},
            
            # Bakery & Sweets - Yellow/golden palette for baked goods
            'bakery': {'fill': '#fff176', 'stroke': '#fbc02d', 'stroke_width': 2, 'radius': 5},
            'pastry': {'fill': '#ffcc02', 'stroke': '#ff8f00', 'stroke_width': 1.5, 'radius': 4},
            'confectionery': {'fill': '#ffcdd2', 'stroke': '#e57373', 'stroke_width': 1.5, 'radius': 4},
            'chocolate': {'fill': '#d7ccc8', 'stroke': '#8d6e63', 'stroke_width': 1.5, 'radius': 4},
            'nuts': {'fill': '#ddbf94', 'stroke': '#a1887f', 'stroke_width': 1, 'radius': 3},
            
            # Beverages - Blue palette for drinks
            'beverages': {'fill': '#90caf9', 'stroke': '#2196f3', 'stroke_width': 1.5, 'radius': 5},
            'coffee': {'fill': '#d7ccc8', 'stroke': '#6d4c41', 'stroke_width': 2, 'radius': 5},
            'tea': {'fill': '#c8e6c9', 'stroke': '#388e3c', 'stroke_width': 1.5, 'radius': 4},
            'wine': {'fill': '#f8bbd9', 'stroke': '#ad1457', 'stroke_width': 2, 'radius': 5},
            'alcohol': {'fill': '#ce93d8', 'stroke': '#7b1fa2', 'stroke_width': 2, 'radius': 5},
            
            # Meat & Dairy - Red/pink palette for animal products
            'butcher': {'fill': '#ef9a9a', 'stroke': '#f44336', 'stroke_width': 2, 'radius': 5},
            'seafood': {'fill': '#80deea', 'stroke': '#00acc1', 'stroke_width': 2, 'radius': 5},
            'cheese': {'fill': '#fff59d', 'stroke': '#f9a825', 'stroke_width': 1.5, 'radius': 4},
            'deli': {'fill': '#ffccd5', 'stroke': '#e57373', 'stroke_width': 2, 'radius': 5},
            
            # Default food establishment style
            'default': {'fill': '#ffcc80', 'stroke': '#ff8a65', 'stroke_width': 1.5, 'radius': 5}
        }
    },
    
    'financial_services': {
        'tags': {
            # Financial Amenities
            'amenity': ['bank', 'atm', 'post_office', 'bureau_de_change', 'money_transfer', 'payment_centre']
        },
        'styles': {
            # Major Financial Institutions - Blue/green palette for trust and stability
            'bank': {'fill': '#bbdefb', 'stroke': '#1976d2', 'stroke_width': 2.5, 'radius': 8},
            'atm': {'fill': '#c8e6c9', 'stroke': '#388e3c', 'stroke_width': 2, 'radius': 4},
            
            # Postal Services - Traditional red palette
            'post_office': {'fill': '#ffcdd2', 'stroke': '#d32f2f', 'stroke_width': 2.5, 'radius': 7},
            
            # Currency & Money Services - Gold/yellow palette for money
            'bureau_de_change': {'fill': '#fff59d', 'stroke': '#f57f17', 'stroke_width': 2, 'radius': 6},
            'money_transfer': {'fill': '#ffe082', 'stroke': '#ff8f00', 'stroke_width': 2, 'radius': 6},
            'payment_centre': {'fill': '#ffcc80', 'stroke': '#ef6c00', 'stroke_width': 2, 'radius': 6},
            
            # Default financial service style
            'default': {'fill': '#bbdefb', 'stroke': '#1976d2', 'stroke_width': 2, 'radius': 6}
        }
    },
    
    'shopping_retail': {
        'tags': {
            # General Retail
            'shop': ['department_store', 'general', 'kiosk', 'mall', 'supermarket', 'wholesale', 
                    'variety_store', 'second_hand', 'charity',
                    # Clothing & Fashion
                    'clothes', 'shoes', 'bag', 'boutique', 'fabric', 'jewelry', 'leather', 'watches', 'tailor',
                    # Electronics & Technology
                    'computer', 'electronics', 'mobile_phone', 'hifi', 'telecommunication',
                    # Health & Beauty
                    'beauty', 'chemist', 'cosmetics', 'hairdresser', 'massage', 'optician', 'perfumery', 'tattoo',
                    # Home & Garden
                    'furniture', 'garden_centre', 'hardware', 'doityourself', 'florist', 'appliance'],
            # Markets and retail amenities
            'amenity': ['marketplace', 'vending_machine']
        },
        'styles': {
            # General Retail - Blue palette for major retail
            'department_store': {'fill': '#e3f2fd', 'stroke': '#1976d2', 'stroke_width': 3, 'radius': 10},
            'mall': {'fill': '#e8eaf6', 'stroke': '#3f51b5', 'stroke_width': 3, 'radius': 12},
            'supermarket': {'fill': '#e0f2f1', 'stroke': '#00796b', 'stroke_width': 2.5, 'radius': 8},
            'general': {'fill': '#f3e5f5', 'stroke': '#7b1fa2', 'stroke_width': 2, 'radius': 6},
            'wholesale': {'fill': '#fce4ec', 'stroke': '#c2185b', 'stroke_width': 2, 'radius': 7},
            'variety_store': {'fill': '#fff3e0', 'stroke': '#f57c00', 'stroke_width': 2, 'radius': 6},
            'kiosk': {'fill': '#ffebee', 'stroke': '#d32f2f', 'stroke_width': 1.5, 'radius': 4},
            'second_hand': {'fill': '#efebe9', 'stroke': '#5d4037', 'stroke_width': 1.5, 'radius': 5},
            'charity': {'fill': '#e8f5e8', 'stroke': '#388e3c', 'stroke_width': 1.5, 'radius': 5},
            
            # Clothing & Fashion - Purple/pink palette for fashion
            'clothes': {'fill': '#f8bbd9', 'stroke': '#e91e63', 'stroke_width': 2, 'radius': 6},
            'shoes': {'fill': '#f3e5f5', 'stroke': '#9c27b0', 'stroke_width': 2, 'radius': 5},
            'bag': {'fill': '#ede7f6', 'stroke': '#673ab7', 'stroke_width': 1.5, 'radius': 4},
            'boutique': {'fill': '#fce4ec', 'stroke': '#ad1457', 'stroke_width': 2.5, 'radius': 6},
            'fabric': {'fill': '#e1bee7', 'stroke': '#8e24aa', 'stroke_width': 1.5, 'radius': 4},
            'jewelry': {'fill': '#fff59d', 'stroke': '#fbc02d', 'stroke_width': 2.5, 'radius': 5},
            'leather': {'fill': '#d7ccc8', 'stroke': '#6d4c41', 'stroke_width': 2, 'radius': 5},
            'watches': {'fill': '#ffecb3', 'stroke': '#ff8f00', 'stroke_width': 2, 'radius': 4},
            'tailor': {'fill': '#f8bbd9', 'stroke': '#c2185b', 'stroke_width': 1.5, 'radius': 4},
            
            # Electronics & Technology - Orange/red palette for tech
            'electronics': {'fill': '#ffccbc', 'stroke': '#ff5722', 'stroke_width': 2.5, 'radius': 7},
            'computer': {'fill': '#ffe0b2', 'stroke': '#f57c00', 'stroke_width': 2.5, 'radius': 6},
            'mobile_phone': {'fill': '#fff3e0', 'stroke': '#ef6c00', 'stroke_width': 2, 'radius': 5},
            'hifi': {'fill': '#ffccbc', 'stroke': '#d84315', 'stroke_width': 2, 'radius': 5},
            'telecommunication': {'fill': '#ffe0b2', 'stroke': '#e65100', 'stroke_width': 2, 'radius': 6},
            
            # Health & Beauty - Light green/teal palette for wellness
            'beauty': {'fill': '#e0f2f1', 'stroke': '#00796b', 'stroke_width': 2, 'radius': 5},
            'chemist': {'fill': '#e8f5e8', 'stroke': '#2e7d32', 'stroke_width': 2.5, 'radius': 6},
            'cosmetics': {'fill': '#f1f8e9', 'stroke': '#558b2f', 'stroke_width': 2, 'radius': 5},
            'hairdresser': {'fill': '#e0f7fa', 'stroke': '#0097a7', 'stroke_width': 2, 'radius': 5},
            'massage': {'fill': '#e8f5e8', 'stroke': '#388e3c', 'stroke_width': 1.5, 'radius': 4},
            'optician': {'fill': '#f3e5f5', 'stroke': '#7b1fa2', 'stroke_width': 2, 'radius': 5},
            'perfumery': {'fill': '#fce4ec', 'stroke': '#ad1457', 'stroke_width': 1.5, 'radius': 4},
            'tattoo': {'fill': '#ffebee', 'stroke': '#c62828', 'stroke_width': 1.5, 'radius': 4},
            
            # Home & Garden - Brown/green palette for home improvement
            'furniture': {'fill': '#efebe9', 'stroke': '#5d4037', 'stroke_width': 2.5, 'radius': 7},
            'garden_centre': {'fill': '#c8e6c9', 'stroke': '#388e3c', 'stroke_width': 2.5, 'radius': 7},
            'hardware': {'fill': '#eceff1', 'stroke': '#455a64', 'stroke_width': 2.5, 'radius': 6},
            'doityourself': {'fill': '#fff8e1', 'stroke': '#f9a825', 'stroke_width': 2.5, 'radius': 7},
            'florist': {'fill': '#f1f8e9', 'stroke': '#689f38', 'stroke_width': 2, 'radius': 5},
            'appliance': {'fill': '#e1f5fe', 'stroke': '#0288d1', 'stroke_width': 2, 'radius': 6},
            
            # Markets and retail amenities
            'marketplace': {'fill': '#fff3e0', 'stroke': '#f57c00', 'stroke_width': 3, 'radius': 10},
            'vending_machine': {'fill': '#e0e0e0', 'stroke': '#616161', 'stroke_width': 1, 'radius': 2},
            
            # Default retail style  
            'default': {'fill': '#e3f2fd', 'stroke': '#1976d2', 'stroke_width': 2, 'radius': 6}
        }
    },
    
    'public_facilities': {
        'tags': {
            # Essential public amenities for accessibility and convenience
            'amenity': ['toilets', 'shower', 'drinking_water', 'bench', 'shelter', 
                       'bicycle_repair_station', 'charging_station', 'waste_basket', 'recycling']
        },
        'styles': {
            # Sanitation & Hygiene Facilities - Blue palette for cleanliness
            'toilets': {'fill': '#e3f2fd', 'stroke': '#1976d2', 'stroke_width': 2.5, 'radius': 8},
            'shower': {'fill': '#bbdefb', 'stroke': '#1565c0', 'stroke_width': 2.5, 'radius': 7},
            
            # Hydration - Light blue/cyan palette for water
            'drinking_water': {'fill': '#e0f2f1', 'stroke': '#00695c', 'stroke_width': 2, 'radius': 6},
            
            # Comfort & Rest - Brown/earth palette for natural comfort
            'bench': {'fill': '#efebe9', 'stroke': '#5d4037', 'stroke_width': 2, 'radius': 5},
            'shelter': {'fill': '#f3e5f5', 'stroke': '#7b1fa2', 'stroke_width': 2.5, 'radius': 9},
            
            # Services & Maintenance - Orange/yellow palette for active services
            'bicycle_repair_station': {'fill': '#fff3e0', 'stroke': '#ef6c00', 'stroke_width': 2.5, 'radius': 7},
            'charging_station': {'fill': '#fff9c4', 'stroke': '#f9a825', 'stroke_width': 2.5, 'radius': 8},
            
            # Waste Management - Green palette for environmental responsibility
            'waste_basket': {'fill': '#e8f5e8', 'stroke': '#2e7d32', 'stroke_width': 2, 'radius': 4},
            'recycling': {'fill': '#c8e6c9', 'stroke': '#388e3c', 'stroke_width': 2.5, 'radius': 7},
            
            # Default public facility style
            'default': {'fill': '#e3f2fd', 'stroke': '#1976d2', 'stroke_width': 2, 'radius': 6}
        }
    }
}