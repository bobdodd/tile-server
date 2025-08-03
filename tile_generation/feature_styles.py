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
            'highway': ['bus_stop'],
            'railway': ['station', 'subway_entrance', 'tram_stop', 'halt'],
            'amenity': ['bus_station', 'ferry_terminal'],
            'public_transport': ['platform', 'stop_position']
        },
        'styles': {
            'bus_stop': {'fill': '#ff9800', 'stroke': '#ff6600', 'stroke_width': 2, 'radius': 5},
            'railway_station': {'fill': '#9c27b0', 'stroke': '#7b1fa2', 'stroke_width': 2, 'radius': 8},
            'subway_entrance': {'fill': '#2196f3', 'stroke': '#1976d2', 'stroke_width': 2, 'radius': 6},
            'tram_stop': {'fill': '#00bcd4', 'stroke': '#0097a7', 'stroke_width': 2, 'radius': 5},
            'bus_station': {'fill': '#ff5722', 'stroke': '#d84315', 'stroke_width': 2, 'radius': 10},
            'ferry_terminal': {'fill': '#607d8b', 'stroke': '#455a64', 'stroke_width': 2, 'radius': 8},
            'platform': {'fill': '#ffc107', 'stroke': '#ff8f00', 'stroke_width': 1.5},
            'default': {'fill': '#ff9800', 'stroke': '#ff6600', 'stroke_width': 2, 'radius': 5}
        }
    },
    'water': {
        'tags': {
            'natural': ['water', 'coastline', 'beach', 'bay', 'strait'],
            'waterway': ['river', 'stream', 'canal', 'drain', 'ditch'],
            'amenity': ['fountain']
        },
        'styles': {
            'water': {'fill': '#aad3df', 'stroke': '#4a80aa', 'stroke_width': 1},
            'river': {'color': '#4a80aa', 'width': 3},
            'stream': {'color': '#6a90ba', 'width': 2},
            'canal': {'color': '#4a80aa', 'width': 2.5},
            'fountain': {'fill': '#87ceeb', 'stroke': '#4682b4', 'stroke_width': 2, 'radius': 4},
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
    }
}