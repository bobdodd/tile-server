"""OSM data processor ported from original osm_tile_processor.py"""

import osmium
from shapely.geometry import Point, LineString, Polygon
from shapely.wkb import loads

class OSMHandler(osmium.SimpleHandler):
    """OSM data handler for extracting features from OSM data."""
    
    def __init__(self, bounds):
        super().__init__()
        self.bounds = bounds
        self.features = {
            'buildings': [],
            'roads': [],
            'healthcare': [],
            'food_sustenance': [],
            'financial_services': [],
            'shopping_retail': [],
            'public_facilities': [],
            'emergency_services': [],
            'tourism_accommodation': [],
            'entertainment_culture': [],
            'automotive_services': [],
            'natural_features': [],
            'office_professional': [],
            'power_utilities': [],
            'man_made_structures': [],
            'barriers_boundaries': [],
            'historic_cultural': [],
            'craft_specialized_services': [],
            'communication_technology': [],
            'education_childcare': [],
            'sports_fitness': [],
            'agricultural_rural': [],
            'military_government': [],
            'leisure_entertainment_details': [],
            'accessibility': [],
            'pedestrian_areas': [],
            'transit': [],
            'water': [],
            'parks': [],
            'landuse': [],
            'vegetation': [],
            'religious': [],
            'parking': [],
            'sensory_accessibility': [],
            'accessible_facilities': [],
            'mobility_access': [],
            'accessible_transport': []
        }
        
    def is_in_bounds(self, lat, lon):
        """Check if coordinate is within tile bounds"""
        return (self.bounds['south'] <= lat <= self.bounds['north'] and
                self.bounds['west'] <= lon <= self.bounds['east'])
    
    def node(self, n):
        """Process node features"""
        if not self.is_in_bounds(n.location.lat, n.location.lon):
            return
            
        tags = {t.k: t.v for t in n.tags}
        
        # Healthcare facilities (amenity-based)
        if tags.get('amenity') in ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy', 'veterinary']:
            self.features['healthcare'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id, 'healthcare_type': 'amenity'}
            })
        
        # Healthcare facilities (healthcare-based)
        elif tags.get('healthcare') in ['alternative', 'audiologist', 'birthing_centre', 'blood_bank', 
                                       'blood_donation', 'centre', 'clinic', 'counselling', 'dentist',
                                       'dialysis', 'doctor', 'hospice', 'hospital', 'laboratory',
                                       'midwife', 'nurse', 'occupational_therapist', 'optometrist',
                                       'pharmacy', 'physiotherapist', 'podiatrist', 'psychotherapist',
                                       'rehabilitation', 'sample_collection', 'speech_therapist',
                                       'vaccination_centre']:
            self.features['healthcare'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id, 'healthcare_type': 'healthcare'}
            })
        
        # Food & Sustenance establishments (amenity and shop-based)
        elif (tags.get('amenity') in ['restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court', 'ice_cream', 'biergarten', 'nightclub'] or
              tags.get('shop') in ['alcohol', 'bakery', 'beverages', 'butcher', 'cheese', 'chocolate', 'coffee', 'confectionery', 'convenience', 'deli', 'farm', 'frozen_food', 'greengrocer', 'health_food', 'nuts', 'pastry', 'seafood', 'tea', 'wine', 'supermarket']):
            self.features['food_sustenance'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Financial Services establishments
        elif tags.get('amenity') in ['bank', 'atm', 'post_office', 'bureau_de_change', 'money_transfer', 'payment_centre']:
            self.features['financial_services'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Shopping & Retail establishments (shop and amenity-based)
        elif (tags.get('shop') in ['department_store', 'general', 'kiosk', 'mall', 'supermarket', 'wholesale', 'variety_store', 'second_hand', 'charity', 'clothes', 'shoes', 'bag', 'boutique', 'fabric', 'jewelry', 'leather', 'watches', 'tailor', 'computer', 'electronics', 'mobile_phone', 'hifi', 'telecommunication', 'beauty', 'chemist', 'cosmetics', 'hairdresser', 'massage', 'optician', 'perfumery', 'tattoo', 'furniture', 'garden_centre', 'hardware', 'doityourself', 'florist', 'greengrocer', 'appliance'] or
              tags.get('amenity') in ['marketplace', 'vending_machine']):
            self.features['shopping_retail'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Public Facilities - Comprehensive coverage of essential public amenities
        elif tags.get('amenity') in ['toilets', 'shower', 'drinking_water', 'bench', 'shelter', 'bicycle_repair_station', 'charging_station', 'waste_basket', 'recycling']:
            self.features['public_facilities'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Emergency Services - Comprehensive coverage of emergency and safety facilities
        elif (tags.get('amenity') in ['police', 'fire_station'] or
              tags.get('emergency') in ['phone', 'defibrillator', 'fire_hydrant', 'assembly_point', 'siren']):
            self.features['emergency_services'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Tourism & Accommodation - Comprehensive coverage of tourist facilities and lodging
        elif tags.get('tourism') in ['hotel', 'hostel', 'guest_house', 'camp_site', 'attraction', 'museum', 'gallery', 'viewpoint', 'information', 'artwork', 'zoo']:
            self.features['tourism_accommodation'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Entertainment & Culture - Comprehensive coverage of cultural and recreational facilities
        elif (tags.get('amenity') in ['cinema', 'theatre', 'library', 'community_centre', 'arts_centre', 'social_centre'] or
              tags.get('leisure') in ['sports_centre', 'swimming_pool', 'golf_course', 'stadium', 'fitness_centre', 'bowling_alley', 'amusement_arcade']):
            self.features['entertainment_culture'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Automotive Services - Comprehensive coverage of vehicle-related services and infrastructure
        elif (tags.get('amenity') in ['fuel', 'car_wash', 'car_rental', 'car_sharing', 'vehicle_inspection', 'compressed_air', 'driver_training', 'parking_entrance', 'motorcycle_parking'] or
              tags.get('shop') in ['car', 'car_parts', 'car_repair', 'motorcycle', 'motorcycle_repair', 'tyres', 'truck', 'trailer'] or
              tags.get('highway') in ['motorway_junction', 'services', 'rest_area', 'emergency_bay', 'toll_gantry']):
            self.features['automotive_services'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Office & Professional Services - Comprehensive coverage of business and professional facilities
        elif tags.get('office') in ['company', 'government', 'lawyer', 'estate_agent', 'insurance', 'architect', 'accountant', 'employment_agency', 'consulting', 'financial', 'it', 'research', 'ngo', 'association', 'diplomatic', 'educational_institution', 'foundation', 'political_party', 'religion', 'tax_advisor', 'therapist', 'travel_agent', 'physician', 'coworking', 'notary', 'newspaper', 'advertising_agency', 'logistics', 'construction_company', 'energy_supplier', 'guide', 'water_utility', 'property_management', 'telecommunication']:
            self.features['office_professional'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Craft & Specialized Services - Workshops, artisans, and small production facilities
        elif tags.get('craft') in ['brewery', 'carpenter', 'electrician', 'plumber', 'tailor', 'shoemaker']:
            self.features['craft_specialized_services'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Communication & Technology - Communication infrastructure and technology services
        elif (tags.get('amenity') in ['post_box', 'telephone'] or
              tags.get('telecom') in ['data_center']):
            self.features['communication_technology'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Education & Childcare - Educational institutions and childcare facilities
        elif tags.get('amenity') in ['childcare', 'language_school', 'driving_school', 'music_school', 'research_institute']:
            self.features['education_childcare'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Sports & Fitness Facilities - Sports venues, fitness equipment, and recreational facilities
        elif (tags.get('leisure') in ['fitness_station', 'track', 'pitch', 'marina', 'slipway'] or
              tags.get('sport') in ['tennis', 'football', 'soccer', 'basketball', 'baseball', 'swimming', 'athletics', 'golf', 'hockey', 'volleyball', 'badminton', 'squash', 'table_tennis', 'boxing', 'martial_arts', 'climbing', 'cycling', 'running', 'fitness', 'gym', 'yoga', 'dance', 'skateboard', 'bmx', 'equestrian', 'sailing', 'rowing', 'canoe', 'surfing']):
            self.features['sports_fitness'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Agricultural & Rural Features - Comprehensive coverage of farming, rural infrastructure, and agricultural facilities
        elif (tags.get('landuse') in ['orchard', 'vineyard', 'allotments', 'farmyard', 'farmland', 'animal_keeping', 'plant_nursery', 'greenhouse_horticulture', 'aquaculture', 'salt_pond'] or
              tags.get('man_made') in ['silo', 'storage_tank', 'bunker_silo', 'windmill', 'watermill', 'windpump', 'watering_place'] or
              tags.get('building') in ['farm_auxiliary', 'barn', 'stable', 'sty', 'greenhouse', 'cowshed', 'chicken_coop', 'farm'] or
              tags.get('amenity') in ['animal_shelter', 'animal_boarding', 'veterinary'] or
              tags.get('craft') in ['agricultural_engines', 'beekeeper', 'distillery', 'winery'] or
              tags.get('shop') in ['farm', 'garden_centre', 'agrarian', 'feed'] or
              tags.get('leisure') in ['fishing', 'garden'] or
              tags.get('natural') in ['tree_row'] or
              tags.get('agriculture') in ['greenhouse', 'crop', 'livestock', 'dairy', 'poultry', 'beekeeping'] or
              tags.get('produce') in ['fruit', 'vegetable', 'grain', 'dairy', 'meat', 'eggs', 'honey']):
            self.features['agricultural_rural'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Military & Government Features - Comprehensive coverage of military installations and government facilities
        elif (tags.get('military') in ['airfield', 'base', 'bunker', 'barracks', 'checkpoint', 'danger_area', 'nuclear_explosion_site', 'obstacle_course', 'office', 'range', 'training_area', 'naval_base', 'depot', 'academy', 'hospital'] or
              tags.get('government') in ['administrative', 'archive', 'courthouse', 'customs', 'diplomatic', 'embassy', 'fire_department', 'legislative', 'library', 'military', 'ministry', 'office', 'parliament', 'police', 'prison', 'public_service', 'register_office', 'social_services', 'taxation', 'town_hall'] or
              tags.get('amenity') in ['courthouse', 'prison', 'police', 'fire_station', 'embassy', 'townhall', 'customs', 'ranger_station'] or
              tags.get('building') in ['government', 'military', 'courthouse', 'prison', 'fire_station', 'police'] or
              tags.get('landuse') in ['military', 'government'] or
              tags.get('office') in ['government', 'diplomatic', 'administrative', 'military'] or
              tags.get('diplomatic') in ['embassy', 'consulate', 'delegation', 'mission'] or
              tags.get('public_service') in ['social_services', 'employment_agency', 'tax_office']):
            self.features['military_government'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Leisure & Entertainment Details - Comprehensive coverage of specialized leisure and entertainment venues
        elif (tags.get('leisure') in ['dance', 'escape_game', 'hackerspace', 'adult_gaming_centre', 'miniature_golf', 'arcade', 'bingo_hall', 'casino', 'gambling', 'social_club', 'sauna', 'bandstand', 'bleachers', 'maze', 'shooting_range', 'disc_golf', 'picnic_table', 'firepit', 'bbq'] or
              tags.get('amenity') in ['casino', 'gambling', 'game_feeding', 'karaoke_box', 'love_hotel', 'nightclub', 'planetarium', 'social_facility', 'stripclub', 'swingerclub', 'brothel', 'studio'] or
              tags.get('shop') in ['games', 'lottery', 'video_games', 'music', 'musical_instrument', 'video', 'books', 'art', 'craft', 'hobby'] or
              tags.get('club') in ['sport', 'social', 'veterans', 'youth', 'senior', 'community', 'photography', 'computer', 'automobile'] or
              tags.get('tourism') in ['theme_park', 'aquarium', 'zoo'] or
              tags.get('sport') in ['billiards', 'darts', 'chess', 'go', 'beachvolleyball'] or
              tags.get('craft') in ['brewery', 'distillery', 'winery'] or
              tags.get('entertainment') in ['escape_room', 'laser_tag', 'paintball', 'axe_throwing', 'virtual_reality']):
            self.features['leisure_entertainment_details'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Power & Utilities Infrastructure - Comprehensive coverage of electrical and utility infrastructure
        elif (tags.get('power') in ['line', 'minor_line', 'cable', 'pole', 'tower', 'substation', 'transformer', 'generator', 'plant', 'switch', 'converter', 'compensator', 'portal', 'terminal', 'insulator', 'busbar', 'bay'] or
              tags.get('utility') in ['gas', 'water', 'sewerage', 'telecom', 'electrical', 'power'] or
              tags.get('man_made') in ['pipeline', 'pumping_station', 'storage_tank', 'water_tower', 'gasometer', 'silo'] or
              tags.get('pipeline') in ['gas', 'oil', 'water', 'sewerage', 'district_heating', 'steam', 'hot_water'] or
              tags.get('telecom') in ['data_center', 'exchange', 'service_device']):
            self.features['power_utilities'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Man-made Structures - Comprehensive coverage of human-built infrastructure and structures
        elif tags.get('man_made') in ['bridge', 'tunnel', 'tower', 'mast', 'antenna', 'chimney', 'pier', 'breakwater', 'groyne', 'lighthouse', 'windmill', 'watermill', 'windpump', 'adit', 'mineshaft', 'crane', 'kiln', 'works', 'embankment', 'cutline', 'dyke', 'levee', 'retaining_wall', 'city_wall', 'dike', 'surveillance', 'monitoring_station', 'survey_point', 'beacon', 'communication_tower', 'observatory', 'telescope', 'flagpole', 'cross', 'obelisk', 'column', 'campanile', 'bunker_silo', 'reservoir_covered', 'clearcut']:
            self.features['man_made_structures'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Barriers & Boundaries - Comprehensive coverage of physical barriers and administrative boundaries
        elif (tags.get('barrier') in ['fence', 'wall', 'hedge', 'gate', 'bollard', 'kerb', 'block', 'bollards', 'chain', 'rope', 'handrail', 'guardrail', 'cable_barrier', 'jersey_barrier', 'lift_gate', 'swing_gate', 'toll_booth', 'turnstile', 'stile', 'chicane', 'motorcycle_barrier', 'height_restrictor', 'sally_port', 'tank_trap', 'border_control', 'cycle_barrier', 'entrance', 'ditch', 'debris', 'log', 'spikes'] or
              tags.get('boundary') in ['administrative', 'national_park', 'postal_code', 'political', 'civil', 'maritime', 'territorial_waters', 'low_emission_zone', 'traffic_calming', 'census', 'parish', 'statistical', 'lot', 'parcel', 'forest', 'marker']):
            self.features['barriers_boundaries'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Historic & Cultural Sites - Comprehensive coverage of historical sites, monuments, cultural attractions, and archaeological features
        elif (tags.get('historic') in ['archaeological_site', 'battlefield', 'boundary_stone', 'building', 'castle', 'church', 'city_gate', 'citywalls', 'fort', 'heritage', 'manor', 'memorial', 'monastery', 'monument', 'ruins', 'tomb', 'tower', 'wayside_cross', 'wayside_shrine', 'wreck', 'pillory', 'stocks', 'gallows', 'aircraft', 'anchor', 'cannon', 'locomotive', 'ship', 'tank', 'vehicle', 'milestone', 'obelisk', 'stone', 'cross', 'statue', 'plaque', 'blue_plaque', 'ghost_sign', 'bunker', 'bridge', 'aqueduct', 'optical_telegraph', 'railway_car', 'highwater_mark', 'pa_system'] or
              tags.get('tourism') in ['museum', 'gallery', 'artwork', 'attraction', 'theme_park'] or
              tags.get('amenity') in ['grave_yard'] or
              tags.get('cultural') in ['museum', 'gallery', 'theatre', 'cinema', 'library', 'archive', 'cultural_centre', 'arts_centre', 'community_centre']):
            self.features['historic_cultural'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Enhanced Natural Features - Comprehensive coverage of terrain, landscape, and landuse features
        elif (tags.get('natural') in ['forest', 'wood', 'grassland', 'cliff', 'peak', 'valley', 'scrub', 'heath', 'sand', 'rock', 'scree', 'bare_rock', 'cave_entrance'] or
              tags.get('landuse') in ['residential', 'commercial', 'industrial', 'retail', 'farmland', 'forest', 'orchard', 'vineyard', 'cemetery', 'military', 'quarry', 'construction', 'allotments', 'education', 'institutional', 'farmyard', 'brownfield', 'garages', 'greenfield', 'depot', 'port', 'railway', 'religious', 'fairground', 'meadow', 'plant_nursery', 'conservation', 'landfill', 'logging', 'greenhouse_horticulture']):
            self.features['natural_features'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Comprehensive Transit Infrastructure
        elif (tags.get('highway') in ['bus_stop', 'platform'] or
              tags.get('railway') in ['station', 'halt', 'platform', 'subway', 'tram', 'tram_stop', 'stop', 'subway_entrance'] or
              tags.get('public_transport') in ['platform', 'stop_position', 'station'] or
              tags.get('amenity') in ['bus_station', 'ferry_terminal'] or
              tags.get('aerialway') in ['station', 'loading_point'] or
              tags.get('aeroway') in ['terminal', 'gate']):
            self.features['transit'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Accessibility features
        if tags.get('amenity') == 'parking' and tags.get('wheelchair') == 'yes':
            self.features['accessibility'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Water features (point features)
        elif (tags.get('amenity') in ['fountain', 'swimming_pool'] or
              tags.get('natural') in ['spring', 'hot_spring', 'geyser'] or
              tags.get('man_made') in ['water_tower', 'water_well', 'water_works', 'lighthouse'] or
              tags.get('leisure') in ['boat_sharing'] or
              tags.get('waterway') in ['waterfall', 'lock_gate', 'fuel']):
            self.features['water'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Park amenities (playgrounds)
        if tags.get('amenity') == 'playground':
            self.features['parks'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Individual trees
        if tags.get('natural') == 'tree':
            self.features['vegetation'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Religious places (nodes)
        if tags.get('amenity') == 'place_of_worship':
            self.features['religious'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Parking (nodes - bicycle/motorcycle parking stands)
        if tags.get('amenity') in ['parking', 'bicycle_parking', 'motorcycle_parking']:
            # Skip if it's wheelchair parking (handled by accessibility)
            if not (tags.get('amenity') == 'parking' and tags.get('wheelchair') == 'yes'):
                self.features['parking'].append({
                    'geometry': Point(n.location.lon, n.location.lat),
                    'properties': {**tags, 'osm_id': n.id}
                })
        
        # Sensory accessibility features
        if (tags.get('tactile_paving') in ['yes', 'no'] or
            tags.get('traffic_signals:sound') == 'yes' or
            tags.get('traffic_signals:vibration') == 'yes' or
            tags.get('acoustic') == 'voice_description' or
            tags.get('braille') == 'yes' or
            tags.get('audio_loop') == 'yes' or
            tags.get('sign_language') == 'yes'):
            self.features['sensory_accessibility'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Accessible facilities features
        if (tags.get('toilets:wheelchair') in ['yes', 'no'] or
            tags.get('changing_table') in ['yes', 'no'] or
            tags.get('elevator') in ['yes', 'no'] or
            tags.get('escalator') in ['yes', 'no'] or
            tags.get('conveying') in ['yes', 'no'] or
            tags.get('automatic_door') in ['yes', 'no'] or
            'door:width' in tags or
            'kerb:height' in tags or
            'incline' in tags or
            tags.get('highway') == 'elevator' or
            tags.get('highway') == 'escalator'):
            self.features['accessible_facilities'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Mobility access features
        if ('wheelchair' in tags or
            tags.get('ramp') == 'yes' or
            tags.get('ramp:wheelchair') == 'yes' or
            tags.get('ramp:stroller') == 'yes' or
            tags.get('ramp:bicycle') == 'yes' or
            'step_count' in tags or
            tags.get('handrail') == 'yes' or
            tags.get('handrail:center') == 'yes' or
            tags.get('handrail:left') == 'yes' or
            tags.get('handrail:right') == 'yes'):
            self.features['mobility_access'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Accessible transport features
        if ('capacity:disabled' in tags or
            tags.get('parking:disabled') == 'yes' or
            tags.get('priority') == 'disabled' or
            tags.get('bus:wheelchair') == 'yes' or
            tags.get('subway:wheelchair') == 'yes' or
            tags.get('tram:wheelchair') == 'yes' or
            tags.get('train:wheelchair') == 'yes'):
            self.features['accessible_transport'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
    
    def way(self, w):
        """Process way features"""
        if len(w.nodes) < 2:
            return
            
        # Get node locations
        try:
            wkb = osmium.geom.WKBFactory()
            geom = wkb.create_linestring(w)
            line = loads(geom, hex=True)
            
            # Check if the line intersects with the tile bounds
            # A line can pass through a tile even if no nodes are within it
            tile_bounds = (self.bounds['west'], self.bounds['south'], 
                          self.bounds['east'], self.bounds['north'])
            line_bounds = line.bounds  # (minx, miny, maxx, maxy)
            
            # Check if bounding boxes overlap
            if not (line_bounds[0] <= tile_bounds[2] and line_bounds[2] >= tile_bounds[0] and
                    line_bounds[1] <= tile_bounds[3] and line_bounds[3] >= tile_bounds[1]):
                return
                
        except Exception:
            return
        
        tags = {t.k: t.v for t in w.tags}
        
        # Buildings
        if 'building' in tags:
            try:
                # Try to create polygon if closed way
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['buildings'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Roads
        elif tags.get('highway') in ['motorway', 'trunk', 'primary', 'secondary', 
                                      'tertiary', 'residential', 'service', 'unclassified',
                                      'pedestrian', 'footway', 'cycleway', 'path', 
                                      'living_street', 'track', 'bus_guideway', 'escape',
                                      'raceway', 'road', 'busway', 'motorway_link', 
                                      'trunk_link', 'primary_link', 'secondary_link', 
                                      'tertiary_link', 'bridleway', 'steps', 'corridor', 'sidewalk']:
            self.features['roads'].append({
                'geometry': line,
                'properties': {**tags, 'osm_id': w.id}
            })
        
        # Water features (rivers, streams, etc.)
        elif tags.get('waterway') in ['river', 'stream', 'canal', 'drain', 'ditch']:
            self.features['water'].append({
                'geometry': line,
                'properties': {**tags, 'osm_id': w.id}
            })
        
        # Transit Infrastructure (lines and areas)
        elif (tags.get('railway') in ['rail', 'subway', 'tram', 'light_rail', 'narrow_gauge', 'funicular', 'monorail'] or
              tags.get('highway') in ['bus_guideway'] or
              tags.get('aerialway') in ['cable_car', 'gondola', 'chair_lift', 'drag_lift', 'rope_tow', 'zip_line']):
            # These are linear transit infrastructure
            self.features['transit'].append({
                'geometry': line,
                'properties': {**tags, 'osm_id': w.id}
            })
        
        # Transit Infrastructure (areas - stations, terminals, platforms)
        elif (tags.get('railway') in ['platform'] or
              tags.get('public_transport') in ['platform', 'station'] or
              tags.get('amenity') in ['bus_station', 'ferry_terminal'] or
              tags.get('aeroway') in ['terminal', 'runway', 'taxiway', 'aerodrome'] or
              tags.get('aerialway') in ['station']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['transit'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Linear platforms/infrastructure
                    self.features['transit'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Healthcare facilities (as areas/buildings)
        elif tags.get('amenity') in ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy', 'veterinary'] or \
             tags.get('healthcare') in ['alternative', 'audiologist', 'birthing_centre', 'blood_bank', 
                                       'blood_donation', 'centre', 'clinic', 'counselling', 'dentist',
                                       'dialysis', 'doctor', 'hospice', 'hospital', 'laboratory',
                                       'midwife', 'nurse', 'occupational_therapist', 'optometrist',
                                       'pharmacy', 'physiotherapist', 'podiatrist', 'psychotherapist',
                                       'rehabilitation', 'sample_collection', 'speech_therapist',
                                       'vaccination_centre']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    healthcare_type = 'amenity' if tags.get('amenity') else 'healthcare'
                    self.features['healthcare'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id, 'healthcare_type': healthcare_type}
                    })
            except Exception:
                pass
        
        # Food & Sustenance establishments (as areas/buildings)
        elif (tags.get('amenity') in ['restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court', 'ice_cream', 'biergarten', 'nightclub'] or
              tags.get('shop') in ['alcohol', 'bakery', 'beverages', 'butcher', 'cheese', 'chocolate', 'coffee', 'confectionery', 'convenience', 'deli', 'farm', 'frozen_food', 'greengrocer', 'health_food', 'nuts', 'pastry', 'seafood', 'tea', 'wine', 'supermarket']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['food_sustenance'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Financial Services establishments (as areas/buildings)
        elif tags.get('amenity') in ['bank', 'atm', 'post_office', 'bureau_de_change', 'money_transfer', 'payment_centre']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['financial_services'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Shopping & Retail establishments (as areas/buildings)
        elif (tags.get('shop') in ['department_store', 'general', 'kiosk', 'mall', 'supermarket', 'wholesale', 'variety_store', 'second_hand', 'charity', 'clothes', 'shoes', 'bag', 'boutique', 'fabric', 'jewelry', 'leather', 'watches', 'tailor', 'computer', 'electronics', 'mobile_phone', 'hifi', 'telecommunication', 'beauty', 'chemist', 'cosmetics', 'hairdresser', 'massage', 'optician', 'perfumery', 'tattoo', 'furniture', 'garden_centre', 'hardware', 'doityourself', 'florist', 'appliance'] or
              tags.get('amenity') in ['marketplace', 'vending_machine']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['shopping_retail'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Public Facilities (as areas/buildings) - Comprehensive coverage
        elif tags.get('amenity') in ['toilets', 'shower', 'drinking_water', 'bench', 'shelter', 'bicycle_repair_station', 'charging_station', 'waste_basket', 'recycling']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['public_facilities'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Emergency Services (as areas/buildings) - Comprehensive coverage
        elif (tags.get('amenity') in ['police', 'fire_station'] or
              tags.get('emergency') in ['phone', 'defibrillator', 'fire_hydrant', 'assembly_point', 'siren']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['emergency_services'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Tourism & Accommodation (as areas/buildings) - Comprehensive coverage
        elif tags.get('tourism') in ['hotel', 'hostel', 'guest_house', 'camp_site', 'attraction', 'museum', 'gallery', 'viewpoint', 'information', 'artwork', 'zoo']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['tourism_accommodation'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Entertainment & Culture (as areas/buildings) - Comprehensive coverage
        elif (tags.get('amenity') in ['cinema', 'theatre', 'library', 'community_centre', 'arts_centre', 'social_centre'] or
              tags.get('leisure') in ['sports_centre', 'swimming_pool', 'golf_course', 'stadium', 'fitness_centre', 'bowling_alley', 'amusement_arcade']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['entertainment_culture'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Automotive Services (as areas/buildings) - Comprehensive coverage
        elif (tags.get('amenity') in ['fuel', 'car_wash', 'car_rental', 'car_sharing', 'vehicle_inspection', 'compressed_air', 'driver_training', 'parking', 'parking_entrance', 'motorcycle_parking'] or
              tags.get('shop') in ['car', 'car_parts', 'car_repair', 'motorcycle', 'motorcycle_repair', 'tyres', 'truck', 'trailer'] or
              tags.get('highway') in ['services', 'rest_area']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['automotive_services'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Office & Professional Services (as areas/buildings) - Comprehensive coverage
        elif tags.get('office') in ['company', 'government', 'lawyer', 'estate_agent', 'insurance', 'architect', 'accountant', 'employment_agency', 'consulting', 'financial', 'it', 'research', 'ngo', 'association', 'diplomatic', 'educational_institution', 'foundation', 'political_party', 'religion', 'tax_advisor', 'therapist', 'travel_agent', 'physician', 'coworking', 'notary', 'newspaper', 'advertising_agency', 'logistics', 'construction_company', 'energy_supplier', 'guide', 'water_utility', 'property_management', 'telecommunication']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['office_professional'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Craft & Specialized Services (as areas/workshops) - Workshops, artisans, and small production facilities
        elif tags.get('craft') in ['brewery', 'carpenter', 'electrician', 'plumber', 'tailor', 'shoemaker']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['craft_specialized_services'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Communication & Technology (as lines/areas) - Communication infrastructure and technology services
        elif tags.get('communication') == 'line' or tags.get('telecom') in ['data_center']:
            try:
                if tags.get('communication') == 'line':
                    # Communication lines as linear features
                    geom = wkb.create_linestring(w)
                    line = loads(geom, hex=True)
                    self.features['communication_technology'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                elif w.is_closed() and tags.get('telecom') == 'data_center':
                    # Data centers as area features
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['communication_technology'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Education & Childcare (as areas/buildings) - Educational institutions and childcare facilities
        elif tags.get('amenity') in ['childcare', 'language_school', 'driving_school', 'music_school', 'research_institute']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['education_childcare'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Sports & Fitness Facilities (as areas/tracks) - Sports venues, fitness equipment, and recreational facilities
        elif (tags.get('leisure') in ['fitness_station', 'track', 'pitch', 'marina', 'slipway'] or
              tags.get('sport') in ['tennis', 'football', 'soccer', 'basketball', 'baseball', 'swimming', 'athletics', 'golf', 'hockey', 'volleyball', 'badminton', 'squash', 'table_tennis', 'boxing', 'martial_arts', 'climbing', 'cycling', 'running', 'fitness', 'gym', 'yoga', 'dance', 'skateboard', 'bmx', 'equestrian', 'sailing', 'rowing', 'canoe', 'surfing']):
            try:
                if tags.get('leisure') == 'track':
                    # Running/cycling tracks as linear features (if not closed) or areas (if closed)
                    if w.is_closed():
                        geom = wkb.create_polygon(w)
                        poly = loads(geom, hex=True)
                        self.features['sports_fitness'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': w.id}
                        })
                    else:
                        geom = wkb.create_linestring(w)
                        line = loads(geom, hex=True)
                        self.features['sports_fitness'].append({
                            'geometry': line,
                            'properties': {**tags, 'osm_id': w.id}
                        })
                elif w.is_closed():
                    # Other sports facilities as area features
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['sports_fitness'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Agricultural & Rural Features (as areas/facilities) - Comprehensive coverage of farming, rural infrastructure, and agricultural facilities
        elif (tags.get('landuse') in ['orchard', 'vineyard', 'allotments', 'farmyard', 'farmland', 'animal_keeping', 'plant_nursery', 'greenhouse_horticulture', 'aquaculture', 'salt_pond'] or
              tags.get('man_made') in ['silo', 'storage_tank', 'bunker_silo', 'windmill', 'watermill', 'windpump', 'watering_place'] or
              tags.get('building') in ['farm_auxiliary', 'barn', 'stable', 'sty', 'greenhouse', 'cowshed', 'chicken_coop', 'farm'] or
              tags.get('amenity') in ['animal_shelter', 'animal_boarding', 'veterinary'] or
              tags.get('craft') in ['agricultural_engines', 'beekeeper', 'distillery', 'winery'] or
              tags.get('shop') in ['farm', 'garden_centre', 'agrarian', 'feed'] or
              tags.get('leisure') in ['fishing', 'garden'] or
              tags.get('natural') in ['tree_row'] or
              tags.get('agriculture') in ['greenhouse', 'crop', 'livestock', 'dairy', 'poultry', 'beekeeping'] or
              tags.get('produce') in ['fruit', 'vegetable', 'grain', 'dairy', 'meat', 'eggs', 'honey']):
            try:
                if tags.get('natural') == 'tree_row':
                    # Tree rows as linear features
                    geom = wkb.create_linestring(w)
                    line = loads(geom, hex=True)
                    self.features['agricultural_rural'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                elif w.is_closed():
                    # Agricultural areas and facilities
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['agricultural_rural'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Military & Government Features (as areas/facilities) - Comprehensive coverage of military installations and government facilities
        elif (tags.get('military') in ['airfield', 'base', 'bunker', 'barracks', 'checkpoint', 'danger_area', 'nuclear_explosion_site', 'obstacle_course', 'office', 'range', 'training_area', 'naval_base', 'depot', 'academy', 'hospital'] or
              tags.get('government') in ['administrative', 'archive', 'courthouse', 'customs', 'diplomatic', 'embassy', 'fire_department', 'legislative', 'library', 'military', 'ministry', 'office', 'parliament', 'police', 'prison', 'public_service', 'register_office', 'social_services', 'taxation', 'town_hall'] or
              tags.get('amenity') in ['courthouse', 'prison', 'police', 'fire_station', 'embassy', 'townhall', 'customs', 'ranger_station'] or
              tags.get('building') in ['government', 'military', 'courthouse', 'prison', 'fire_station', 'police'] or
              tags.get('landuse') in ['military', 'government'] or
              tags.get('office') in ['government', 'diplomatic', 'administrative', 'military'] or
              tags.get('diplomatic') in ['embassy', 'consulate', 'delegation', 'mission'] or
              tags.get('public_service') in ['social_services', 'employment_agency', 'tax_office']):
            try:
                if w.is_closed():
                    # Military and government areas and facilities
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['military_government'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Leisure & Entertainment Details (as areas/facilities) - Comprehensive coverage of specialized leisure and entertainment venues
        elif (tags.get('leisure') in ['dance', 'escape_game', 'hackerspace', 'adult_gaming_centre', 'miniature_golf', 'arcade', 'bingo_hall', 'casino', 'gambling', 'social_club', 'sauna', 'bandstand', 'bleachers', 'maze', 'shooting_range', 'disc_golf', 'picnic_table', 'firepit', 'bbq'] or
              tags.get('amenity') in ['casino', 'gambling', 'game_feeding', 'karaoke_box', 'love_hotel', 'nightclub', 'planetarium', 'social_facility', 'stripclub', 'swingerclub', 'brothel', 'studio'] or
              tags.get('shop') in ['games', 'lottery', 'video_games', 'music', 'musical_instrument', 'video', 'books', 'art', 'craft', 'hobby'] or
              tags.get('club') in ['sport', 'social', 'veterans', 'youth', 'senior', 'community', 'photography', 'computer', 'automobile'] or
              tags.get('tourism') in ['theme_park', 'aquarium', 'zoo'] or
              tags.get('sport') in ['billiards', 'darts', 'chess', 'go', 'beachvolleyball'] or
              tags.get('craft') in ['brewery', 'distillery', 'winery'] or
              tags.get('entertainment') in ['escape_room', 'laser_tag', 'paintball', 'axe_throwing', 'virtual_reality']):
            try:
                if w.is_closed():
                    # Leisure and entertainment areas and facilities
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['leisure_entertainment_details'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Power & Utilities Infrastructure (as areas/facilities) - Comprehensive coverage  
        elif (tags.get('power') in ['substation', 'generator', 'plant', 'transformer'] or
              tags.get('utility') in ['gas', 'water', 'sewerage', 'telecom', 'electrical', 'power'] or
              tags.get('man_made') in ['pipeline', 'pumping_station', 'storage_tank', 'water_tower', 'gasometer', 'silo', 'wastewater_plant', 'water_works'] or
              tags.get('telecom') in ['data_center', 'exchange']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['power_utilities'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Handle linear infrastructure like power lines and pipelines
                    self.features['power_utilities'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Man-made Structures (as areas/linear features) - Comprehensive coverage
        elif tags.get('man_made') in ['bridge', 'tunnel', 'tower', 'mast', 'antenna', 'chimney', 'pier', 'breakwater', 'groyne', 'lighthouse', 'windmill', 'watermill', 'windpump', 'adit', 'mineshaft', 'crane', 'kiln', 'works', 'embankment', 'cutline', 'dyke', 'levee', 'retaining_wall', 'city_wall', 'dike', 'surveillance', 'monitoring_station', 'survey_point', 'beacon', 'communication_tower', 'observatory', 'telescope', 'flagpole', 'cross', 'obelisk', 'column', 'campanile', 'bunker_silo', 'reservoir_covered', 'clearcut']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['man_made_structures'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Handle linear structures like bridges, tunnels, embankments
                    self.features['man_made_structures'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Barriers & Boundaries (as areas/linear features) - Comprehensive coverage
        elif (tags.get('barrier') in ['fence', 'wall', 'hedge', 'gate', 'bollard', 'kerb', 'block', 'bollards', 'chain', 'rope', 'handrail', 'guardrail', 'cable_barrier', 'jersey_barrier', 'lift_gate', 'swing_gate', 'toll_booth', 'turnstile', 'stile', 'chicane', 'motorcycle_barrier', 'height_restrictor', 'sally_port', 'tank_trap', 'border_control', 'cycle_barrier', 'entrance', 'ditch', 'debris', 'log', 'spikes'] or
              tags.get('boundary') in ['administrative', 'national_park', 'postal_code', 'political', 'civil', 'maritime', 'territorial_waters', 'low_emission_zone', 'traffic_calming', 'census', 'parish', 'statistical', 'lot', 'parcel', 'forest', 'marker']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['barriers_boundaries'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Handle linear barriers like fences, walls, boundaries
                    self.features['barriers_boundaries'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Historic & Cultural Sites (as areas/linear features) - Comprehensive coverage of historical sites, monuments, and cultural areas
        elif (tags.get('historic') in ['archaeological_site', 'battlefield', 'boundary_stone', 'building', 'castle', 'church', 'city_gate', 'citywalls', 'fort', 'heritage', 'manor', 'memorial', 'monastery', 'monument', 'ruins', 'tomb', 'tower', 'wayside_cross', 'wayside_shrine', 'wreck', 'pillory', 'stocks', 'gallows', 'aircraft', 'anchor', 'cannon', 'locomotive', 'ship', 'tank', 'vehicle', 'milestone', 'obelisk', 'stone', 'cross', 'statue', 'plaque', 'blue_plaque', 'ghost_sign', 'bunker', 'bridge', 'aqueduct', 'optical_telegraph', 'railway_car', 'highwater_mark', 'pa_system'] or
              tags.get('tourism') in ['museum', 'gallery', 'artwork', 'attraction', 'theme_park'] or
              tags.get('amenity') in ['grave_yard'] or
              tags.get('cultural') in ['museum', 'gallery', 'theatre', 'cinema', 'library', 'archive', 'cultural_centre', 'arts_centre', 'community_centre']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['historic_cultural'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Handle linear historic features like historic walls, roads, boundaries
                    self.features['historic_cultural'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Enhanced Natural Features (as areas) - Comprehensive coverage of terrain and landuse
        elif (tags.get('natural') in ['forest', 'wood', 'grassland', 'cliff', 'scrub', 'heath', 'sand', 'rock', 'scree', 'bare_rock'] or
              tags.get('landuse') in ['residential', 'commercial', 'industrial', 'retail', 'farmland', 'forest', 'orchard', 'vineyard', 'cemetery', 'military', 'quarry', 'construction', 'allotments', 'education', 'institutional', 'farmyard', 'brownfield', 'garages', 'greenfield', 'depot', 'port', 'railway', 'religious', 'fairground', 'meadow', 'plant_nursery', 'conservation', 'landfill', 'logging', 'greenhouse_horticulture']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['natural_features'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Parks and leisure areas
        elif tags.get('leisure') in ['park', 'garden', 'playground', 'dog_park', 'nature_reserve'] or \
             tags.get('landuse') in ['grass', 'recreation_ground', 'village_green']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['parks'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Linear Water Features (waterways)
        elif tags.get('waterway') in ['river', 'stream', 'canal', 'drain', 'ditch', 'rapids', 'dam', 'weir', 'dock', 'boatyard']:
            self.features['water'].append({
                'geometry': line,
                'properties': {**tags, 'osm_id': w.id}
            })
        
        # Water areas - Natural water bodies
        elif tags.get('natural') in ['water', 'coastline', 'beach', 'bay', 'strait', 'shoal', 'reef', 'wetland']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Coastlines are lines
                    self.features['water'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Man-made Water Features (areas and lines)
        elif tags.get('man_made') in ['reservoir', 'pier', 'breakwater', 'groyne', 'floating_dock']:
            try:
                if w.is_closed() and tags.get('man_made') in ['reservoir']:
                    # Area features
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Linear features (piers, breakwaters, etc.)
                    self.features['water'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Leisure Water Areas
        elif tags.get('leisure') in ['swimming_pool', 'water_park', 'marina', 'slipway']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Linear slipways
                    self.features['water'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Landuse Water Areas
        elif tags.get('landuse') in ['reservoir', 'salt_pond', 'aquaculture', 'basin']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Amenity Water Areas
        elif tags.get('amenity') in ['swimming_pool']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass

    def area(self, a):
        """Process area/relation features"""
        tags = {t.k: t.v for t in a.tags}
        
        try:
            wkb = osmium.geom.WKBFactory()
            
            # Healthcare facilities (as relations)
            if tags.get('amenity') in ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy', 'veterinary'] or \
               tags.get('healthcare') in ['alternative', 'audiologist', 'birthing_centre', 'blood_bank', 
                                         'blood_donation', 'centre', 'clinic', 'counselling', 'dentist',
                                         'dialysis', 'doctor', 'hospice', 'hospital', 'laboratory',
                                         'midwife', 'nurse', 'occupational_therapist', 'optometrist',
                                         'pharmacy', 'physiotherapist', 'podiatrist', 'psychotherapist',
                                         'rehabilitation', 'sample_collection', 'speech_therapist',
                                         'vaccination_centre']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if healthcare area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        healthcare_type = 'amenity' if tags.get('amenity') else 'healthcare'
                        self.features['healthcare'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id, 'healthcare_type': healthcare_type}
                        })
                except Exception:
                    pass
            
            # Food & Sustenance establishments (as relations)
            elif (tags.get('amenity') in ['restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court', 'ice_cream', 'biergarten', 'nightclub'] or
                  tags.get('shop') in ['alcohol', 'bakery', 'beverages', 'butcher', 'cheese', 'chocolate', 'coffee', 'confectionery', 'convenience', 'deli', 'farm', 'frozen_food', 'greengrocer', 'health_food', 'nuts', 'pastry', 'seafood', 'tea', 'wine', 'supermarket']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if food establishment area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['food_sustenance'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Financial Services establishments (as relations)
            elif tags.get('amenity') in ['bank', 'atm', 'post_office', 'bureau_de_change', 'money_transfer', 'payment_centre']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if financial services area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['financial_services'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Shopping & Retail establishments (as relations)
            elif (tags.get('shop') in ['department_store', 'general', 'kiosk', 'mall', 'supermarket', 'wholesale', 'variety_store', 'second_hand', 'charity', 'clothes', 'shoes', 'bag', 'boutique', 'fabric', 'jewelry', 'leather', 'watches', 'tailor', 'computer', 'electronics', 'mobile_phone', 'hifi', 'telecommunication', 'beauty', 'chemist', 'cosmetics', 'hairdresser', 'massage', 'optician', 'perfumery', 'tattoo', 'furniture', 'garden_centre', 'hardware', 'doityourself', 'florist', 'appliance'] or
                  tags.get('amenity') in ['marketplace', 'vending_machine']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if shopping/retail area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['shopping_retail'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Public Facilities (as relations) - Comprehensive coverage
            elif tags.get('amenity') in ['toilets', 'shower', 'drinking_water', 'bench', 'shelter', 'bicycle_repair_station', 'charging_station', 'waste_basket', 'recycling']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if public facility area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['public_facilities'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Emergency Services (as relations) - Comprehensive coverage
            elif (tags.get('amenity') in ['police', 'fire_station'] or
                  tags.get('emergency') in ['phone', 'defibrillator', 'fire_hydrant', 'assembly_point', 'siren']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if emergency service area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['emergency_services'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Tourism & Accommodation (as relations) - Comprehensive coverage
            elif tags.get('tourism') in ['hotel', 'hostel', 'guest_house', 'camp_site', 'attraction', 'museum', 'gallery', 'viewpoint', 'information', 'artwork', 'zoo']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if tourism/accommodation area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['tourism_accommodation'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Entertainment & Culture (as relations) - Comprehensive coverage
            elif (tags.get('amenity') in ['cinema', 'theatre', 'library', 'community_centre', 'arts_centre', 'social_centre'] or
                  tags.get('leisure') in ['sports_centre', 'swimming_pool', 'golf_course', 'stadium', 'fitness_centre', 'bowling_alley', 'amusement_arcade']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if entertainment/culture area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['entertainment_culture'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Automotive Services (as relations) - Comprehensive coverage
            elif (tags.get('amenity') in ['fuel', 'car_wash', 'car_rental', 'car_sharing', 'vehicle_inspection', 'compressed_air', 'driver_training', 'parking', 'parking_entrance', 'motorcycle_parking'] or
                  tags.get('shop') in ['car', 'car_parts', 'car_repair', 'motorcycle', 'motorcycle_repair', 'tyres', 'truck', 'trailer'] or
                  tags.get('highway') in ['services', 'rest_area']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if automotive service area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['automotive_services'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Office & Professional Services (as relations) - Comprehensive coverage
            elif tags.get('office') in ['company', 'government', 'lawyer', 'estate_agent', 'insurance', 'architect', 'accountant', 'employment_agency', 'consulting', 'financial', 'it', 'research', 'ngo', 'association', 'diplomatic', 'educational_institution', 'foundation', 'political_party', 'religion', 'tax_advisor', 'therapist', 'travel_agent', 'physician', 'coworking', 'notary', 'newspaper', 'advertising_agency', 'logistics', 'construction_company', 'energy_supplier', 'guide', 'water_utility', 'property_management', 'telecommunication']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if office area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['office_professional'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Craft & Specialized Services (as relations) - Workshops, artisans, and small production facilities
            elif tags.get('craft') in ['brewery', 'carpenter', 'electrician', 'plumber', 'tailor', 'shoemaker']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if craft area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['craft_specialized_services'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Communication & Technology (as relations) - Communication infrastructure and technology services
            elif tags.get('telecom') in ['data_center']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if communication area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['communication_technology'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Education & Childcare (as relations) - Educational institutions and childcare facilities
            elif tags.get('amenity') in ['childcare', 'language_school', 'driving_school', 'music_school', 'research_institute']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if education area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['education_childcare'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Sports & Fitness Facilities (as relations) - Sports venues, fitness equipment, and recreational facilities
            elif (tags.get('leisure') in ['fitness_station', 'track', 'pitch', 'marina', 'slipway'] or
                  tags.get('sport') in ['tennis', 'football', 'soccer', 'basketball', 'baseball', 'swimming', 'athletics', 'golf', 'hockey', 'volleyball', 'badminton', 'squash', 'table_tennis', 'boxing', 'martial_arts', 'climbing', 'cycling', 'running', 'fitness', 'gym', 'yoga', 'dance', 'skateboard', 'bmx', 'equestrian', 'sailing', 'rowing', 'canoe', 'surfing']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if sports area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['sports_fitness'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Agricultural & Rural Features (as relations) - Comprehensive coverage of farming, rural infrastructure, and agricultural facilities
            elif (tags.get('landuse') in ['orchard', 'vineyard', 'allotments', 'farmyard', 'farmland', 'animal_keeping', 'plant_nursery', 'greenhouse_horticulture', 'aquaculture', 'salt_pond'] or
                  tags.get('man_made') in ['silo', 'storage_tank', 'bunker_silo', 'windmill', 'watermill', 'windpump', 'watering_place'] or
                  tags.get('building') in ['farm_auxiliary', 'barn', 'stable', 'sty', 'greenhouse', 'cowshed', 'chicken_coop', 'farm'] or
                  tags.get('amenity') in ['animal_shelter', 'animal_boarding', 'veterinary'] or
                  tags.get('craft') in ['agricultural_engines', 'beekeeper', 'distillery', 'winery'] or
                  tags.get('shop') in ['farm', 'garden_centre', 'agrarian', 'feed'] or
                  tags.get('leisure') in ['fishing', 'garden'] or
                  tags.get('agriculture') in ['greenhouse', 'crop', 'livestock', 'dairy', 'poultry', 'beekeeping'] or
                  tags.get('produce') in ['fruit', 'vegetable', 'grain', 'dairy', 'meat', 'eggs', 'honey']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if agricultural area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['agricultural_rural'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Military & Government Features (as relations) - Comprehensive coverage of military installations and government facilities
            elif (tags.get('military') in ['airfield', 'base', 'bunker', 'barracks', 'checkpoint', 'danger_area', 'nuclear_explosion_site', 'obstacle_course', 'office', 'range', 'training_area', 'naval_base', 'depot', 'academy', 'hospital'] or
                  tags.get('government') in ['administrative', 'archive', 'courthouse', 'customs', 'diplomatic', 'embassy', 'fire_department', 'legislative', 'library', 'military', 'ministry', 'office', 'parliament', 'police', 'prison', 'public_service', 'register_office', 'social_services', 'taxation', 'town_hall'] or
                  tags.get('amenity') in ['courthouse', 'prison', 'police', 'fire_station', 'embassy', 'townhall', 'customs', 'ranger_station'] or
                  tags.get('building') in ['government', 'military', 'courthouse', 'prison', 'fire_station', 'police'] or
                  tags.get('landuse') in ['military', 'government'] or
                  tags.get('office') in ['government', 'diplomatic', 'administrative', 'military'] or
                  tags.get('diplomatic') in ['embassy', 'consulate', 'delegation', 'mission'] or
                  tags.get('public_service') in ['social_services', 'employment_agency', 'tax_office']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if military/government area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['military_government'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Leisure & Entertainment Details (as relations) - Comprehensive coverage of specialized leisure and entertainment venues
            elif (tags.get('leisure') in ['dance', 'escape_game', 'hackerspace', 'adult_gaming_centre', 'miniature_golf', 'arcade', 'bingo_hall', 'casino', 'gambling', 'social_club', 'sauna', 'bandstand', 'bleachers', 'maze', 'shooting_range', 'disc_golf', 'picnic_table', 'firepit', 'bbq'] or
                  tags.get('amenity') in ['casino', 'gambling', 'game_feeding', 'karaoke_box', 'love_hotel', 'nightclub', 'planetarium', 'social_facility', 'stripclub', 'swingerclub', 'brothel', 'studio'] or
                  tags.get('shop') in ['games', 'lottery', 'video_games', 'music', 'musical_instrument', 'video', 'books', 'art', 'craft', 'hobby'] or
                  tags.get('club') in ['sport', 'social', 'veterans', 'youth', 'senior', 'community', 'photography', 'computer', 'automobile'] or
                  tags.get('tourism') in ['theme_park', 'aquarium', 'zoo'] or
                  tags.get('sport') in ['billiards', 'darts', 'chess', 'go', 'beachvolleyball'] or
                  tags.get('craft') in ['brewery', 'distillery', 'winery'] or
                  tags.get('entertainment') in ['escape_room', 'laser_tag', 'paintball', 'axe_throwing', 'virtual_reality']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if leisure/entertainment area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['leisure_entertainment_details'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Power & Utilities Infrastructure (as relations) - Comprehensive coverage
            elif (tags.get('power') in ['substation', 'generator', 'plant', 'transformer'] or
                  tags.get('utility') in ['gas', 'water', 'sewerage', 'telecom', 'electrical', 'power'] or
                  tags.get('man_made') in ['pipeline', 'pumping_station', 'storage_tank', 'water_tower', 'gasometer', 'silo', 'wastewater_plant', 'water_works'] or
                  tags.get('telecom') in ['data_center', 'exchange']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if power/utility area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['power_utilities'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Man-made Structures (as relations) - Comprehensive coverage
            elif tags.get('man_made') in ['bridge', 'tunnel', 'tower', 'mast', 'antenna', 'chimney', 'pier', 'breakwater', 'groyne', 'lighthouse', 'windmill', 'watermill', 'windpump', 'adit', 'mineshaft', 'crane', 'kiln', 'works', 'embankment', 'cutline', 'dyke', 'levee', 'retaining_wall', 'city_wall', 'dike', 'surveillance', 'monitoring_station', 'survey_point', 'beacon', 'communication_tower', 'observatory', 'telescope', 'flagpole', 'cross', 'obelisk', 'column', 'campanile', 'bunker_silo', 'reservoir_covered', 'clearcut']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if man-made structure area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['man_made_structures'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Barriers & Boundaries (as relations) - Comprehensive coverage
            elif (tags.get('barrier') in ['fence', 'wall', 'hedge', 'gate', 'bollard', 'kerb', 'block', 'bollards', 'chain', 'rope', 'handrail', 'guardrail', 'cable_barrier', 'jersey_barrier', 'lift_gate', 'swing_gate', 'toll_booth', 'turnstile', 'stile', 'chicane', 'motorcycle_barrier', 'height_restrictor', 'sally_port', 'tank_trap', 'border_control', 'cycle_barrier', 'entrance', 'ditch', 'debris', 'log', 'spikes'] or
                  tags.get('boundary') in ['administrative', 'national_park', 'postal_code', 'political', 'civil', 'maritime', 'territorial_waters', 'low_emission_zone', 'traffic_calming', 'census', 'parish', 'statistical', 'lot', 'parcel', 'forest', 'marker']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if barrier/boundary area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['barriers_boundaries'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Historic & Cultural Sites (as relations) - Comprehensive coverage of historical sites, monuments, and cultural areas
            elif (tags.get('historic') in ['archaeological_site', 'battlefield', 'boundary_stone', 'building', 'castle', 'church', 'city_gate', 'citywalls', 'fort', 'heritage', 'manor', 'memorial', 'monastery', 'monument', 'ruins', 'tomb', 'tower', 'wayside_cross', 'wayside_shrine', 'wreck', 'pillory', 'stocks', 'gallows', 'aircraft', 'anchor', 'cannon', 'locomotive', 'ship', 'tank', 'vehicle', 'milestone', 'obelisk', 'stone', 'cross', 'statue', 'plaque', 'blue_plaque', 'ghost_sign', 'bunker', 'bridge', 'aqueduct', 'optical_telegraph', 'railway_car', 'highwater_mark', 'pa_system'] or
                  tags.get('tourism') in ['museum', 'gallery', 'artwork', 'attraction', 'theme_park'] or
                  tags.get('amenity') in ['grave_yard'] or
                  tags.get('cultural') in ['museum', 'gallery', 'theatre', 'cinema', 'library', 'archive', 'cultural_centre', 'arts_centre', 'community_centre']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if historic/cultural area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['historic_cultural'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Enhanced Natural Features (as relations) - Comprehensive coverage of terrain and landuse
            elif (tags.get('natural') in ['forest', 'wood', 'grassland', 'cliff', 'scrub', 'heath', 'sand', 'rock', 'scree', 'bare_rock'] or
                  tags.get('landuse') in ['residential', 'commercial', 'industrial', 'retail', 'farmland', 'forest', 'orchard', 'vineyard', 'cemetery', 'military', 'quarry', 'construction', 'allotments', 'education', 'institutional', 'farmyard', 'brownfield', 'garages', 'greenfield', 'depot', 'port', 'railway', 'religious', 'fairground', 'meadow', 'plant_nursery', 'conservation', 'landfill', 'logging', 'greenhouse_horticulture']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if natural feature area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['natural_features'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Transit Infrastructure (as relations)
            elif (tags.get('railway') in ['station', 'platform'] or 
                  tags.get('public_transport') in ['platform', 'station'] or 
                  tags.get('amenity') in ['bus_station', 'ferry_terminal'] or 
                  tags.get('aeroway') in ['terminal', 'aerodrome'] or 
                  tags.get('aerialway') in ['station']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if transit area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['transit'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Buildings
            elif 'building' in tags:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['buildings'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Parks and leisure areas
            elif tags.get('leisure') in ['park', 'garden', 'playground', 'dog_park', 'nature_reserve'] or \
                 tags.get('landuse') in ['grass', 'recreation_ground', 'village_green']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['parks'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Water areas - comprehensive coverage
            elif (tags.get('natural') in ['water', 'beach', 'bay', 'strait', 'shoal', 'reef', 'wetland'] or
                  tags.get('man_made') in ['reservoir', 'water_works'] or
                  tags.get('leisure') in ['swimming_pool', 'water_park', 'marina'] or
                  tags.get('landuse') in ['reservoir', 'salt_pond', 'aquaculture', 'basin'] or
                  tags.get('amenity') in ['swimming_pool']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['water'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
                    
        except Exception:
            pass