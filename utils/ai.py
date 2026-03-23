import os
import requests
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# `_fallback_states` is defined later (budget-aware).
def _budget_tier(budget):
    """
    Small helper to vary deterministic fallbacks by budget input.
    """
    try:
        b = int(float(budget))
    except Exception:
        b = 0
    if b <= 20000:
        return "low"
    if b <= 60000:
        return "mid"
    return "high"

def get_ai_response(prompt):
    if not GROQ_API_KEY:
        # Fallback/Mock for testing if no key provided
        return "Mock AI response: India has beautiful states like Kerala, Rajasthan, and Goa."
    
    try:
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant", # The groq-compatible model (replaces openai/gpt-oss-20b)
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[Groq/OpenAI Error] {e}")
        return None

def _extract_json(text, expect="any"):
    """
    Make Grok/XAI output parsing more robust.
    Tries direct JSON, then extracts the first array/object block from surrounding text.
    """
    if not text:
        return None

    t = str(text).strip()
    # Handle fenced JSON blocks.
    if "```json" in t:
        t = t.split("```json", 1)[1].split("```", 1)[0].strip()

    try:
        return json.loads(t)
    except Exception:
        pass

    if expect in ("array", "any"):
        m = re.search(r'(\[.*\])', t, flags=re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass

    if expect in ("object", "any"):
        m = re.search(r'(\{.*\})', t, flags=re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass

    return None

def recommend_states(budget, members, travel_type, duration):
    prompt = """
    Suggest 3 Indian states for a travel group with:
    Budget: INR {}
    Members: {}
    Travel Type: {}
    Duration: {} days
    
    Return the response as a JSON array of objects, each with 'name' and 'reason'.
    Example format: [{{"name": "Kerala", "reason": "Lush greenery and backwaters"}}]
    """.format(budget, members, travel_type, duration)
    response = get_ai_response(prompt)
    
    if response:
        try:
            parsed = _extract_json(response, expect="array")
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return _fallback_states(travel_type=travel_type, duration=duration, budget=budget)
    return _fallback_states(travel_type=travel_type, duration=duration, budget=budget)

def _fallback_states(travel_type, duration, budget=None):
    """
    Deterministic fallback so `/recommend` never renders an empty grid.
    """
    t = (travel_type or "").strip().lower()
    _d = int(duration) if str(duration).isdigit() else 0
    bt = _budget_tier(budget)

    # Budget-aware ordering so plan inputs influence the output.
    if bt == "low":
        if t == "adventure":
            return [
                {"name": "Rajasthan", "reason": "Adventure-friendly routes with forts and desert scenery (budget-friendly)."},
                {"name": "Uttarakhand", "reason": "Hills + outdoors with manageable travel costs."},
                {"name": "Uttar Pradesh", "reason": "Iconic monuments and efficient city routing."},
            ]
        if t == "historical":
            return [
                {"name": "Rajasthan", "reason": "Forts and palaces with heritage-rich experiences (great value)."},
                {"name": "Uttar Pradesh", "reason": "Dense concentration of historical sites for efficient sightseeing."},
                {"name": "Madhya Pradesh", "reason": "Heritage + wildlife at generally lower costs."},
            ]
        if t == "spiritual":
            return [
                {"name": "Uttar Pradesh", "reason": "Sacred ghats and religious circuits with budget comfort."},
                {"name": "Uttarakhand", "reason": "Pilgrimage towns in scenic settings with affordable travel."},
                {"name": "Rajasthan", "reason": "Temples + traditions with flexible itineraries."},
            ]
        # default for low budget: nature-ish
        return [
            {"name": "Rajasthan", "reason": "Heritage + landscapes with strong value for money."},
            {"name": "Uttar Pradesh", "reason": "Iconic monuments and easy city travel."},
            {"name": "Madhya Pradesh", "reason": "A balanced mix of heritage and nature."},
        ]

    if bt == "high":
        if t == "nature":
            return [
                {"name": "Kerala", "reason": "Backwaters, greenery, and premium comfort for longer stays."},
                {"name": "Sikkim", "reason": "Mountain scenery with a calm, high-experience itinerary."},
                {"name": "Goa", "reason": "Beaches + indulgent day trips (great for premium travel)."},
            ]
        if t == "adventure":
            return [
                {"name": "Himachal Pradesh", "reason": "Trekking terrain with higher-end trip options."},
                {"name": "Uttarakhand", "reason": "Adventure + nature circuit with flexible lodging."},
                {"name": "Goa", "reason": "Watersports + downtime for a premium balance." if _d >= 7 else "Beaches + watersports for a premium balance."},
            ]
        if t == "historical":
            return [
                {"name": "Rajasthan", "reason": "Heritage cities + forts with upgraded experiences."},
                {"name": "Uttar Pradesh", "reason": "Iconic monuments with a more comfortable pace."},
                {"name": "Madhya Pradesh", "reason": "Heritage + wildlife with premium stays."},
            ]
        if t == "spiritual":
            return [
                {"name": "Uttar Pradesh", "reason": "Sacred routes with better comfort and slower pacing."},
                {"name": "Uttarakhand", "reason": "Pilgrimage towns with scenic luxury experiences."},
                {"name": "Rajasthan", "reason": "Temples and traditions with guided tours."},
            ]

    # mid budget and/or default
    if t == "nature":
        return [
            {"name": "Kerala", "reason": "Backwaters, greenery, and a relaxed coastal itinerary."},
            {"name": "Himachal Pradesh", "reason": "Hill scenery and comfortable sightseeing for most durations."},
            {"name": "Sikkim", "reason": "Mountain views and peaceful experiences in a compact region."},
        ]
    if t == "adventure":
        return [
            {"name": "Himachal Pradesh", "reason": "Trekking-friendly terrain and exciting outdoor activities."},
            {"name": "Uttarakhand", "reason": "Adventure options around nature and popular hill routes."},
            {"name": "Goa", "reason": "Beaches plus recovery time for longer trips." if _d >= 7 else "Beaches plus easy day trips and watersports."},
        ]
    if t == "historical":
        return [
            {"name": "Rajasthan", "reason": "Forts, palaces, and rich heritage across multiple cities."},
            {"name": "Uttar Pradesh", "reason": "Iconic monuments and a dense trail of historical sites."},
            {"name": "Madhya Pradesh", "reason": "Heritage + wildlife with a strong tourism circuit."},
        ]
    if t == "spiritual":
        return [
            {"name": "Uttar Pradesh", "reason": "Sacred ghats and timeless religious experiences."},
            {"name": "Uttarakhand", "reason": "Pilgrimage towns with scenic mountain settings."},
            {"name": "Rajasthan", "reason": "Temples, traditions, and calmer cultural routes."},
        ]

    return [
        {"name": "Kerala", "reason": "Beautiful coastal state with great variety of experiences."},
        {"name": "Rajasthan", "reason": "Rich heritage and desert landscapes for an unforgettable trip."},
        {"name": "Goa", "reason": "Stunning beaches and a fun, flexible itinerary."},
    ]

def recommend_places(state, travel_type, budget=None, members=None, age_group=None, duration=None):
    prompt = """
    Using the following trip profile:
    - State: {}
    - Travel Type: {}
    - Budget (INR): {}
    - Members: {}
    - Age Group: {}
    - Duration (days): {}

    Suggest 5 specific tourist places inside the given state that fit this profile.
    Return as a JSON array of objects, each with 'name' and 'short_description'.
    Example format: [{{"name": "Munnar", "short_description": "Hill station famous for tea plantations"}}]
    """.format(state, travel_type, budget, members, age_group, duration)
    
    response = get_ai_response(prompt)
    
    if response:
        try:
            parsed = _extract_json(response, expect="array")
            if isinstance(parsed, list):
                return parsed
        except Exception:
            # Fall back to sensible defaults so the UI isn't empty
            pass
    state_normalized = (state or "").strip().lower()
    travel_type_normalized = (travel_type or "").strip().lower()
    bt = _budget_tier(budget)
    _d = int(duration) if str(duration).isdigit() else 0

    # Curated fallbacks for popular states.
    curated = {
        "kerala": [
            ("Munnar Tea Gardens", "Scenic tea estates and breezy hill views."),
            ("Alappuzha Backwaters", "Houseboat cruising through calm canals and palm-lined shores."),
            ("Fort Kochi & Chinese Fishing Nets", "Colonial heritage, coastal walks, and local cuisine."),
            ("Kumarakom Bird Sanctuary", "Bird-watching and peaceful lakeside evenings."),
            ("Varkala Beach & Cliff Walk", "Sunset viewpoints and a scenic cliff-side promenade."),
            ("Thekkady (Periyar) Wildlife Sanctuary", "Wildlife views plus a nature-focused day."),
            ("Alleppey Houseboats", "Relaxed, romantic backwater cruise for the evenings."),
            ("Wayanad Wildlife Sanctuary", "Dense green landscapes and safari-friendly experiences."),
        ],
        "rajasthan": [
            ("Jaipur City Palace", "Majestic forts, courtyards, and heritage experiences."),
            ("Amber Fort (Amer Fort)", "Epic hilltop fort scenery and immersive history."),
            ("Udaipur Lake Pichola", "Romantic viewpoints and sunset boat rides."),
            ("Jodhpur Mehrangarh Fort", "Rugged fort views and local stories."),
            ("Jaisalmer Desert Safari (Sam Sand Dunes)", "Sand dunes, culture shows, and starry nights."),
            ("Ranthambore National Park", "Wildlife safari options and scenic landscapes."),
            ("Pushkar Lake & Ghats", "Cultural vibe, markets, and a peaceful lakeside walk."),
            ("Bikaner Junagarh Fort", "Heritage architecture with a calmer pace."),
        ],
        "goa": [
            ("Baga Beach", "Lively coastline with beach time and local energy."),
            ("Dudhsagar Falls", "Waterfall adventure with scenic viewpoints and easy treks."),
            ("Old Goa (Se Cathedral & Churches)", "Heritage churches and Portuguese-influenced history."),
            ("Anjuna Flea Market Area", "Local crafts, food stalls, and relaxed evening markets."),
            ("Panaji (Fontainhas) Old Town", "Colorful streets and a walkable city vibe."),
            ("Aguada Fort", "Seaside fort views and coastal exploration."),
            ("Arambol Beach", "Quieter beach experience and laid-back day plans."),
            ("Spice Plantation Tour", "A guided nature+culture experience in the interior."),
        ],
        "kashmir": [
            ("Dal Lake Shikara Ride", "Iconic houseboats and serene morning rides on Dal Lake."),
            ("Gulmarg Gondola & Ski Resort", "Asia's highest gondola with stunning Himalayan panoramas."),
            ("Pahalgam Valley", "Scenic meadows and river walks popular for trekking."),
            ("Sonamarg (Meadow of Gold)", "Alpine meadows, glaciers, and breathtaking scenery."),
            ("Betaab Valley", "Lush green valley surrounded by snow-capped peaks."),
            ("Nishat Bagh (Mughal Gardens)", "Terraced Mughal gardens overlooking Dal Lake."),
            ("Wular Lake", "One of Asia's largest freshwater lakes with migratory birds."),
            ("Yusmarg Meadow", "Quiet highland meadow perfect for a peaceful nature day."),
        ],
        "assam": [
            ("Kaziranga National Park", "Home to two-thirds of the world's one-horned rhinos."),
            ("Manas National Park", "UNESCO site with tigers, elephants, and rare wildlife."),
            ("Majuli Island", "World's largest river island and a cultural heritage hub."),
            ("Kamakhya Temple", "Iconic hilltop temple and a major pilgrimage site."),
            ("Sivasagar (Ahom Kingdom)", "Historical ruins of the Ahom dynasty with serene tanks."),
            ("Haflong Lake", "Scenic hill station lake in the Dima Hasao district."),
            ("Dipor Bil Wetland", "Tranquil bird-watching and sunset views near Guwahati."),
            ("Jorhat Tea Gardens", "Colonial-era tea estates with guided tasting experiences."),
        ],
        "himachal pradesh": [
            ("Shimla Mall Road & Jakhu Temple", "Colonial charm and hill views from the ridge."),
            ("Manali Rohtang Pass", "Snow-covered mountain pass with adventure activities."),
            ("Spiti Valley", "Remote high-altitude desert with ancient monasteries."),
            ("Kullu Valley", "Scenic riverside valley ideal for rafting and scenic walks."),
            ("Dharamshala & McLeod Ganj", "Tibetan culture, monasteries, and mountain hikes."),
            ("Khajjiar (Mini Switzerland)", "Lush meadows and forested hills in Chamba district."),
            ("Kasol & Kheerganga", "Backpacker trail with forests, rivers, and hot springs."),
            ("Dalhousie (Kalatop)", "Colonial hill town with peaceful nature walks."),
        ],
        "uttarakhand": [
            ("Rishikesh Ghat & River Rafting", "Spiritual town famous for yoga and Ganges rafting."),
            ("Haridwar Ganga Aarti", "Evening aarti on the Ganges - a spiritual highlight."),
            ("Jim Corbett National Park", "India's oldest national park with tiger safari options."),
            ("Nainital Lake", "Picturesque lake town in the Kumaon hills."),
            ("Auli Ski Resort", "Winter sports and Himalayan panoramas at high altitude."),
            ("Valley of Flowers", "UNESCO site blooming with alpine wildflowers (Jul-Sep)."),
            ("Mussoorie Mall Road", "Queen of Hills with colonial charm and valley views."),
            ("Kedarnath Temple", "High-altitude pilgrimage temple in the Garhwal Himalayas."),
        ],
        "maharashtra": [
            ("Mumbai Gateway of India", "Iconic colonial arch on the seafront with harbour views."),
            ("Ajanta & Ellora Caves", "UNESCO rock-cut caves with ancient Buddhist art."),
            ("Lonavala & Khandala", "Scenic hill station escapes with waterfalls and forts."),
            ("Shirdi Sai Baba Temple", "Major pilgrimage site attracting millions annually."),
            ("Mahabaleshwar", "Hill station with strawberry farms and valley viewpoints."),
            ("Kolhapur Mahalakshmi Temple", "Ancient south-facing Shakti temple with heritage context."),
            ("Tadoba Tiger Reserve", "Maharashtra's premier wildlife and tiger safari zone."),
            ("Pune Shaniwar Wada", "Historic Peshwa-era fort in the heart of Pune."),
        ],
        "tamil nadu": [
            ("Meenakshi Amman Temple, Madurai", "Iconic temple with towering gopurams and vibrant culture."),
            ("Ooty (Nilgiris Hill Station)", "Colonial hill town with tea gardens and a toy train."),
            ("Mahabalipuram (Mamallapuram)", "UNESCO shore temples and rock-carved sculptures."),
            ("Kodaikanal Lake & Coaker's Walk", "Misty hill station with scenic lake and forest trails."),
            ("Thanjavur Brihadeeswarar Temple", "UNESCO grand Chola temple with towering vimana."),
            ("Rameswaram Temple & Pamban Bridge", "Sacred pilgrimage island with a dramatic sea bridge."),
            ("Marina Beach, Chennai", "One of the world's longest urban beaches."),
            ("Mudumalai Tiger Reserve", "Wildlife corridors connecting the Nilgiris biosphere."),
        ],
        "karnataka": [
            ("Hampi (Vijayanagara Ruins)", "UNESCO ruins of the Vijayanagara Empire in boulder landscape."),
            ("Coorg (Kodagu) Coffee Estates", "Fragrant coffee plantations with misty mountain views."),
            ("Mysore Palace & Zoo", "Grand palace illuminated at night with Dasara heritage."),
            ("Jog Falls", "India's second-highest plunge waterfall in the Western Ghats."),
            ("Badami Cave Temples", "6th-century Chalukya rock-cut temples in a sandstone gorge."),
            ("Kabini River Lodge", "Wildlife resort and boat safaris for elephant sightings."),
            ("Chikmagalur Coffee Hills", "Scenic trekking and coffee estate stays."),
            ("Gokarna Beach", "Quieter alternative to Goa with pristine half-moon beaches."),
        ],
        "west bengal": [
            ("Darjeeling Tea Estates & Toy Train", "UNESCO toy train through mist-wrapped tea gardens."),
            ("Sundarbans Mangrove Forest", "UNESCO delta with Royal Bengal Tiger boat safaris."),
            ("Victoria Memorial, Kolkata", "Iconic colonial marble monument and art museum."),
            ("Howrah Bridge & Flower Market", "Iconic cantilever bridge and vibrant wholesale market."),
            ("Kalimpong Hill Town", "Quieter hill station with orchid nurseries and monasteries."),
            ("Murshidabad (Hazarduari)", "Nawab-era palace and historical site on the Ganges."),
            ("Bishnupur Temple Town", "Terracotta temple architecture of the Malla dynasty."),
            ("Dooars & Gorumara Park", "Terai forest with rhinos, elephants, and river jeep safari."),
        ],
        "meghalaya": [
            ("Living Root Bridges, Cherrapunji", "Unique bioengineered bridges woven from living tree roots."),
            ("Dawki River (Umngot)", "Incredibly clear river with transparent water boat rides."),
            ("Mawlynnong Village", "Asia's cleanest village with skywalk and natural beauty."),
            ("Shillong Peak & Ward's Lake", "Capital city with colonial charm and panoramic peaks."),
            ("Elephant Falls", "Three-tiered waterfall with scenic walking trails."),
            ("Nohkalikai Falls", "India's tallest plunge waterfall near Cherrapunji."),
            ("Mawsmai Cave", "Easy-access limestone cave in the meghalayan plateau."),
            ("Umiam Lake (Barapani)", "Reservoir lake popular for boating and water sports."),
        ],
        "andaman": [
            ("Radhanagar Beach, Havelock", "Asia's best beach with turquoise waters and coral reefs."),
            ("Neil Island (Shaheed Dweep)", "Quiet island with pristine beaches and coral gardens."),
            ("Cellular Jail, Port Blair", "Colonial jail memorial with a powerful light-and-sound show."),
            ("Elephant Beach Snorkeling", "Vibrant coral reefs and marine life close to shore."),
            ("North Bay Island", "Glass-bottom boat rides and sea walking experience."),
            ("Baratang Island Limestone Caves", "Mangrove creek boat ride to unique natural caves."),
            ("Ross Island (Netaji Subhas Chandra Bose Island)", "Ruins of British colonial headquarters on a small island."),
            ("Chidiya Tapu (Bird Island)", "Sunset point with rich bird diversity in mangroves."),
        ],
    }

    # Decide which curated places to show.
    state_items = None
    for key, value in curated.items():
        if key in state_normalized:
            state_items = value
            break

    # Budget-aware indices: ensures “places change” when budget changes.
    if bt == "low":
        indices = [0, 1, 2, 4, 5]  # more accessible staples
    elif bt == "high":
        indices = [0, 2, 3, 5, 7]  # more safari + premium-style options
    else:
        indices = [0, 1, 3, 4, 6]  # balanced mix

    # Duration slightly changes which two categories lead.
    if _d <= 5:
        indices = indices[:4] + [indices[-1]]  # keep 5 items, but prefer the first set

    if state_items:
        chosen = []
        for i in indices:
            if 0 <= i < len(state_items):
                chosen.append(state_items[i])
        # If something went wrong, fill from the start.
        while len(chosen) < 5 and state_items:
            chosen.append(state_items[len(chosen) % len(state_items)])
        bt_hint = {
            "low": "Great value for money and easy planning.",
            "mid": "A comfortable mix of key sights and relaxed pacing.",
            "high": "Premium experiences and more in-depth exploration options.",
        }.get(bt, "")
        type_hint = {
            "nature": "Nature-forward days with scenic breaks.",
            "adventure": "Active sightseeing with outdoors-first stops.",
            "historical": "Heritage-focused stops and stories around landmarks.",
            "spiritual": "Calm, mindful sightseeing with sacred-site pacing.",
        }.get(travel_type_normalized, "An immersive travel experience.")

        return [
            {"name": name, "short_description": f"{desc} {type_hint} {bt_hint}".strip()}
            for name, desc in chosen[:5]
        ]

    # Generic fallback for unknown states.
    bt_hint = {
        "low": "Budget-friendly highlights.",
        "mid": "A balanced set of must-sees.",
        "high": "More premium and immersive experiences.",
    }.get(bt, "")
    type_hint = {
        "nature": "Focus on scenic viewpoints and greenery.",
        "adventure": "Focus on outdoor activities and active sightseeing.",
        "historical": "Focus on heritage monuments and architecture.",
        "spiritual": "Focus on temples and reflective experiences.",
    }.get(travel_type_normalized, "Focus on an immersive itinerary.")

    generic_places = [
        (f"Top Scenic Spot in {state}", type_hint),
        (f"Local Heritage Walk in {state}", type_hint),
        (f"Signature Landmark of {state}", type_hint),
        (f"Hidden Gem near {state}", type_hint),
        (f"Sunset Viewpoint in {state}", type_hint),
    ]

    return [{"name": n, "short_description": f"{d} {bt_hint}".strip()} for n, d in generic_places]

def get_place_details(place_name, duration=3):
    # Ensure duration is a valid integer >= 1
    try:
        num_days = max(1, int(duration))
    except (TypeError, ValueError):
        num_days = 3

    day_list = ", ".join(['"Day {}: ..."'.format(i) for i in range(1, num_days + 1)])

    prompt = """
    Provide travel details for {}:
    1. A detailed description (2-3 sentences).
    2. Estimated cost for a couple (in INR).
    3. A EXACTLY {}-day itinerary — you MUST provide exactly {} items in the itinerary array, one per day.

    Return ONLY valid JSON in this exact format:
    {{"description": "...", "estimated_cost": "INR ...", "itinerary": [{}]}}
    """.format(place_name, num_days, num_days, day_list)

    response = get_ai_response(prompt)

    place = (place_name or "").strip() or "This destination"

    if response:
        try:
            parsed = _extract_json(response, expect="object")
            if isinstance(parsed, dict):
                itinerary = parsed.get("itinerary", [])

                # Trim if AI returned too many days
                itinerary = itinerary[:num_days]

                # Pad if AI returned too few days
                while len(itinerary) < num_days:
                    day_num = len(itinerary) + 1
                    itinerary.append(
                        "Day {}: Continue exploring {} with local sights, cuisine, and experiences.".format(day_num, place)
                    )

                parsed["itinerary"] = itinerary
                return parsed
        except Exception:
            pass

    # Safe fallback - generate the correct number of days
    itinerary = [
        "Day {}: Exploring highlights of {} - local sights, food, and experiences.".format(i, place)
        for i in range(1, num_days + 1)
    ]
    return {
        "description": "{} is a great choice for a memorable trip with a mix of local culture, scenic experiences, and easy day-to-day planning.".format(place),
        "estimated_cost": "Approx. INR 15,000 - 30,000 for a couple (varies by season)",
        "itinerary": itinerary,
    }

def answer_place_question(place_name, state_name, question):
    """
    Answer a user's question about a specific place using the Grok AI.
    Falls back to a helpful built-in response if the API is unavailable.
    """
    prompt = """You are a helpful travel assistant for Indian tourism.
The user is viewing a travel plan for '{}' in '{}'.
Answer this question in 2-4 clear, helpful sentences:

Question: {}

If unsure, give practical general advice for visiting that destination.""".format(
        place_name, state_name or "India", question
    )

    response = get_ai_response(prompt)
    if response and response.strip():
        return response.strip()

    # Smart built-in fallback answers based on common question keywords
    q = question.lower()
    place = place_name
    state = state_name or "India"

    if any(w in q for w in ["best time", "when to visit", "season", "weather", "month"]):
        return "The best time to visit {} is generally between October and March when the weather is pleasant and ideal for sightseeing. Avoid the peak summer months (April–June) for outdoor activities, though some hill stations are great in summer. Always check local conditions before planning.".format(place)

    if any(w in q for w in ["food", "eat", "cuisine", "restaurant", "dish", "local"]):
        return "{}  in {} is known for its unique local cuisine. Look for popular street food, regional thalis, and local specialties at markets and small eateries near the main attractions. Asking locals for recommendations is usually the best way to find authentic spots.".format(place, state)

    if any(w in q for w in ["hotel", "stay", "accommodation", "lodge", "resort"]):
        return "Accommodation near {} ranges from budget guesthouses to mid-range hotels and premium resorts depending on your budget. Booking 2–3 weeks in advance is recommended, especially during peak tourist season (Oct–Feb). Check Google Maps or MakeMyTrip for options close to the main attraction.".format(place)

    if any(w in q for w in ["how to reach", "how to get", "transport", "reach", "travel to", "get there", "bus", "train", "flight", "airport"]):
        return "You can reach {} by a combination of flight/train to the nearest major city in {} and then a road or rail connection to the destination. Local taxis, auto-rickshaws, and state buses are typically available. Check Redbus or IRCTC for current transport options and timings.".format(place, state)

    if any(w in q for w in ["entry fee", "ticket", "cost", "fee", "price", "charge", "budget"]):
        return "Entry fees at {} vary by attraction — many monuments and national parks in India charge between ₹50 to ₹600 for Indian nationals. Overall trip costs depend on your accommodation and travel style, but a moderate budget of ₹2,000–₹5,000 per day per person is a good starting point for most Indian destinations.".format(place)

    if any(w in q for w in ["safe", "safety", "danger", "solo", "woman", "women"]):
        return "{} is generally considered safe for tourists including solo travellers. As with any destination, stay aware of your surroundings, keep valuables secure, and share your itinerary with someone you trust. Local tourist police and helplines are available in most major destinations.".format(place)

    # Generic fallback
    return "Great choice! {} is a wonderful destination in {}. For the most accurate and up-to-date information, I recommend checking the official tourism website for {} or searching on Google for current traveller reviews and tips.".format(place, state, place)
