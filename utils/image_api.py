import os
import requests
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1524492459426-edcc9088710b?auto=format&fit=crop&q=80&w=800",
    "https://images.unsplash.com/photo-1506461883276-594a12b11cf3?auto=format&fit=crop&q=80&w=800",
    "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&q=80&w=800"
]

def get_place_images(place_name):
    if not UNSPLASH_ACCESS_KEY:
        return FALLBACK_IMAGES
    
    url = f"https://api.unsplash.com/search/photos?query={place_name}&client_id={UNSPLASH_ACCESS_KEY}&per_page=3"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        results = [img['urls']['regular'] for img in data['results']]
        return results if results else FALLBACK_IMAGES
    except requests.exceptions.RequestException:
        print(f"⚠️ Warning: Could not reach Unsplash API (Network/DNS issue). Using fallback images.")
        return FALLBACK_IMAGES
    except Exception as e:
        print(f"⚠️ Warning: Unexpected Unsplash error ({e}). Using fallback images.")
        return FALLBACK_IMAGES
