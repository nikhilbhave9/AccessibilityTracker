import os
import requests
import tensorflow as tf
import numpy as np
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# Set your Google API key here
API_KEY = 'AIzaSyCuJgnCN165bECqG4dbByoZgluvAZUZKG8'

# Define bounding box coordinates (example for a city area)
BOUNDING_BOX = {
    'north_east': (28.473925603742988, 77.07998939548736),  # NE corner
    'south_west': (28.45947619753435, 77.09217749236791),        # SW corner
}

# Function to get major locations within the bounding box
def get_major_locations(bounding_box):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f"{(bounding_box['north_east'][0] + bounding_box['south_west'][0]) / 2},{(bounding_box['north_east'][1] + bounding_box['south_west'][1]) / 2}",
        'radius': 1000,  # Adjust the radius as needed
        'type': 'point_of_interest',  # Adjust the type as needed
        'key': API_KEY
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return []

# Function to download Google Street View images
def download_street_view_image(location, heading, pitch, fov, save_path):
    base_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        'size': '640x640',  # Image size (max 640x640 for free tier)
        'location': location,
        'heading': heading,
        'pitch': pitch,
        'fov': fov,
        'key': API_KEY
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved to {save_path}")
    else:
        print(f"Error: {response.status_code} - {response.reason}")

# Load TensorFlow model for object detection
def load_model(model_path):
    model = tf.saved_model.load(model_path)
    return model

# Run detection on an image
def run_detection(model, image_path):
    image_np = np.array(Image.open(image_path))
    input_tensor = tf.convert_to_tensor(image_np)
    input_tensor = input_tensor[tf.newaxis,...]

    detections = model(input_tensor)

    return detections, image_np

# Evaluate accessibility based on detected features in images
def evaluate_accessibility(location):
    access_score = 0
    max_score = 5

    image_path = 'street_view_image.jpg'
    download_street_view_image(
        location=f"{location['geometry']['location']['lat']},{location['geometry']['location']['lng']}",
        heading=0, pitch=0, fov=90, save_path=image_path
    )

    model = load_model('ssd_mobilenet_v2_fpnlite/saved_model')
    detections, image_np = run_detection(model, image_path)

    detection_classes = detections['detection_classes'][0].numpy().astype(int)
    detection_scores = detections['detection_scores'][0].numpy()

    # Check for wheelchair ramp
    if 1 in detection_classes[detection_scores > 0.5]:  # Assume class 1 is wheelchair ramp
        access_score += 1

    # Check for elevator
    if 2 in detection_classes[detection_scores > 0.5]:  # Assume class 2 is elevator
        access_score += 1

    # Check for accessible restroom
    if 3 in detection_classes[detection_scores > 0.5]:  # Assume class 3 is accessible restroom
        access_score += 1

    # Check for accessible parking
    if 4 in detection_classes[detection_scores > 0.5]:  # Assume class 4 is accessible parking
        access_score += 1

    # Check for clear signage
    if 5 in detection_classes[detection_scores > 0.5]:  # Assume class 5 is clear signage
        access_score += 1

    return int((access_score / max_score) * 10)

# Function to evaluate mapping quality of a major location
def evaluate_mapping_quality(location):
    map_score = 0
    max_score = 5

    # Placeholder logic for mapping quality
    if 'entrance_coverage' in location.get('attributes', []):
        map_score += 1

    if 'blockage_detection' in location.get('attributes', []):
        map_score += 1

    if 'updated_info' in location.get('attributes', []):
        map_score += 1

    if 'multiple_views' in location.get('attributes', []):
        map_score += 1

    if 'accurate_location' in location.get('attributes', []):
        map_score += 1

    return int((map_score / max_score) * 10)

# Main function to check accessibility within the bounding box
def check_accessibility_within_bounding_box(bounding_box):
    locations = get_major_locations(bounding_box) # Returns locations with attributes like: (operational_status, coordinates, name, photos, , place_id, "types", vicinity/address)
    import ipdb; ipdb.set_trace()
    accessibility_scores = []

    for location in locations:
        access_score = evaluate_accessibility(location) 
        mapping_score = evaluate_mapping_quality(location)
        accessibility_scores.append({
            'name': location['name'],
            'location': location['geometry']['location'],
            'accessibility_score': access_score,
            'mapping_quality_score': mapping_score
        })
    
    return accessibility_scores

# Example usage
if __name__ == "__main__":
    scores = check_accessibility_within_bounding_box(BOUNDING_BOX)
    for score in scores:
        print(f"Location: {score['name']}")
        print(f"  Accessibility Score: {score['accessibility_score']}")
        print(f"  Mapping Quality Score: {score['mapping_quality_score']}")
