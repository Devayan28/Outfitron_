import cv2
import numpy as np
import os
from sklearn.cluster import KMeans
import mediapipe as mp


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils



def detect_face(image_path):
    """Detect and extract face from selfie image using MediaPipe Face Detection"""
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return None, None
        
    with mp.solutions.face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=0.5) as face_detection:
        
        results = face_detection.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        if not results.detections:
            print("No face detected in selfie")
            return None, None

        # Get the largest face detection
        detection = max(results.detections, key=lambda d: d.location_data.relative_bounding_box.width * 
                                                          d.location_data.relative_bounding_box.height)
        bbox = detection.location_data.relative_bounding_box
        h, w = img.shape[:2]
        
        # Calculate pixel coordinates
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        width = int(bbox.width * w)
        height = int(bbox.height * h)
        
    
        padding = int(width * 0.3)
        x, y = max(0, x-padding), max(0, y-padding)
        width = min(img.shape[1]-x, width+2*padding)
        height = min(img.shape[0]-y, height+2*padding)
        
        face_img = img[y:y+height, x:x+width]
        cv2.imwrite('detected_face.jpg', face_img)
        return face_img, (x, y, width, height)

def extract_skin(face_img):
    """Extract skin region from face image"""
    img_hsv = cv2.cvtColor(face_img, cv2.COLOR_BGR2HSV)
    img_ycrcb = cv2.cvtColor(face_img, cv2.COLOR_BGR2YCrCb)
    
    # Skin color ranges
    lower_hsv = np.array([0, 20, 70], dtype=np.uint8)
    upper_hsv = np.array([30, 255, 255], dtype=np.uint8)
    lower_ycrcb = np.array([0, 130, 70], dtype=np.uint8)
    upper_ycrcb = np.array([255, 180, 135], dtype=np.uint8)
    
    skin_mask = cv2.bitwise_and(
        cv2.inRange(img_hsv, lower_hsv, upper_hsv),
        cv2.inRange(img_ycrcb, lower_ycrcb, upper_ycrcb)
    )
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    
    if np.count_nonzero(skin_mask) == 0:
        h, w = face_img.shape[:2]
        skin_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.ellipse(skin_mask, (w//2, h//2), (w//3, h//3), 0, 0, 360, 255, -1)
    
    skin = cv2.bitwise_and(face_img, face_img, mask=skin_mask)
    return skin, skin_mask

def get_dominant_skin_color(skin_img, skin_mask):
    """Determine dominant skin color using clustering"""
    skin_pixels = skin_img[skin_mask > 0]
    skin_pixels = skin_pixels[np.all(skin_pixels != [0, 0, 0], axis=1)]
    
    if len(skin_pixels) == 0:
        return None
    
    lab_pixels = cv2.cvtColor(skin_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB)
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(lab_pixels.reshape(-1, 3))
    
    dominant_lab = kmeans.cluster_centers_[np.argmax(np.bincount(kmeans.labels_))]
    return cv2.cvtColor(np.uint8([[dominant_lab]]), cv2.COLOR_LAB2BGR)[0][0]

def classify_skin_tone(rgb):
    """Classify skin tone and undertone"""
    hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_BGR2HSV)[0][0]
    lab = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_BGR2LAB)[0][0]
    
    brightness = (hsv[2] * 0.6 + lab[0] * 0.4)  # Weighted brightness
    
    if brightness > 200: tone = "Very Fair"
    elif brightness > 175: tone = "Fair"
    elif brightness > 140: tone = "Medium"
    elif brightness > 100: tone = "Tan"
    else: tone = "Dark"
    
    r, g, b = rgb
    if r > b + 15 and g > b + 10: undertone = "Warm"
    elif b > r + 15 and b > g + 10: undertone = "Cool"
    else: undertone = "Neutral"
    
    return tone, undertone, brightness

def analyze_skin_texture(face_img):
    """Analyze skin texture quality"""
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    texture_score = np.var(laplacian)
    
    if texture_score < 100: return "Smooth", "Fine texture"
    elif texture_score < 300: return "Normal", "Even texture"
    elif texture_score < 600: return "Combination", "Uneven texture"
    else: return "Rough", "Coarse texture"

def detect_body_proportions(fullbody_path, face_width):
    """Analyze body proportions from full-body image using MediaPipe Pose"""
    img = cv2.imread(fullbody_path)
    if img is None:
        print(f"Error reading full-body image at {fullbody_path}")
        return None
    
    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        min_detection_confidence=0.5) as pose:
        
        results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        if not results.pose_landmarks:
            print("No body landmarks detected")
            return None
        
        
        h, w = img.shape[:2]
        
        
        landmarks = results.pose_landmarks.landmark
        
        # Shoulder width (distance between left and right shoulders)
        left_shoulder = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h)
        right_shoulder = (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h)
        shoulder_width = np.sqrt((right_shoulder[0] - left_shoulder[0])**2 + 
                                (right_shoulder[1] - left_shoulder[1])**2)
        
        # Waist width (distance between left and right hips)
        left_hip = (landmarks[mp_pose.PoseLandmark.LEFT_HIP].x * w,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP].y * h)
        right_hip = (landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x * w,
                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y * h)
        waist_width = np.sqrt((right_hip[0] - left_hip[0])**2 + 
                             (right_hip[1] - left_hip[1])**2)
        
        # Hip width (distance between left and right hips, but lower)
        # Using the mid-point between hip and knee as hip measurement
        left_knee = (landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x * w,
                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y * h)
        right_knee = (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x * w,
                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y * h)
        
        left_hip_lower = ((left_hip[0] + left_knee[0])/2, (left_hip[1] + left_knee[1])/2)
        right_hip_lower = ((right_hip[0] + right_knee[0])/2, (right_hip[1] + right_knee[1])/2)
        hip_width = np.sqrt((right_hip_lower[0] - left_hip_lower[0])**2 + 
                            (right_hip_lower[1] - left_hip_lower[1])**2)
        
        # Height estimation (top of head to heels)
        head_top = (landmarks[mp_pose.PoseLandmark.NOSE].x * w,
                    landmarks[mp_pose.PoseLandmark.NOSE].y * h - 50)  # Approximate head top
        left_heel = (landmarks[mp_pose.PoseLandmark.LEFT_HEEL].x * w,
                     landmarks[mp_pose.PoseLandmark.LEFT_HEEL].y * h)
        height = np.sqrt((left_heel[0] - head_top[0])**2 + 
                         (left_heel[1] - head_top[1])**2)
        
        return {
            'shoulder': shoulder_width,
            'waist': waist_width,
            'hips': hip_width,
            'height': height,
            'landmarks': results.pose_landmarks
        }

def determine_body_type(proportions):
    """Classify body shape with precise measurements and ratios"""
    if proportions is None:
        return "Average", {}
    
    shoulder, waist, hips = proportions['shoulder'], proportions['waist'], proportions['hips']
    height = proportions['height']
    
    
    shoulder_hip_ratio = shoulder / hips
    waist_hip_ratio = waist / hips
    shoulder_height_ratio = shoulder / height
    
    
    classification_rules = [
        {
            'name': 'Hourglass',
            'condition': (waist_hip_ratio < 0.75) and (0.9 <= shoulder_hip_ratio <= 1.1),
            'confidence': min((0.75 - waist_hip_ratio), abs(1 - shoulder_hip_ratio))
        },
        {
            'name': 'Pear',
            'condition': (shoulder_hip_ratio < 0.9) and (waist_hip_ratio < 0.8),
            'confidence': (0.9 - shoulder_hip_ratio) + (0.8 - waist_hip_ratio)
        },
        {
            'name': 'Inverted Triangle',
            'condition': (shoulder_hip_ratio > 1.1),
            'confidence': (shoulder_hip_ratio - 1.1)
        },
        {
            'name': 'Rectangle',
            'condition': (waist_hip_ratio > 0.85) and (0.95 <= shoulder_hip_ratio <= 1.05),
            'confidence': (waist_hip_ratio - 0.85) + min(abs(1 - shoulder_hip_ratio), 0.05)
        }
    ]
    
    
    best_match = {'name': 'Average', 'confidence': 0}
    for rule in classification_rules:
        if rule['condition'] and rule['confidence'] > best_match['confidence']:
            best_match = {'name': rule['name'], 'confidence': rule['confidence']}
    
    
    measurements = {
        'shoulder': round(shoulder, 1),
        'waist': round(waist, 1),
        'hips': round(hips, 1),
        'height': round(height, 1),
        'shoulder_hip_ratio': round(shoulder_hip_ratio, 2),
        'waist_hip_ratio': round(waist_hip_ratio, 2)
    }
    
    return best_match['name'], measurements



def get_color_recommendations(tone, undertone):
    """Suggest flattering colors with more options"""
    palette = {
        "Very Fair": {
            "Warm": ["Peach", "Coral", "Gold", "Cream", "Camel"],
            "Cool": ["Baby Blue", "Lavender", "Silver", "Mint", "Powder Pink"],
            "Neutral": ["Dusty Rose", "Mauve", "Taupe", "Soft Gray", "Rose Brown"]
        },
        "Fair": {
            "Warm": ["Camel", "Olive Green", "Terracotta", "Mustard", "Rust"],
            "Cool": ["Royal Blue", "Emerald Green", "Plum", "Navy", "Burgundy"],
            "Neutral": ["Rose Brown", "Slate Blue", "Charcoal", "Mushroom", "Deep Teal"]
        },
        "Medium": {
            "Warm": ["Burnt Orange", "Rust", "Golden Yellow", "Amber", "Warm Red"],
            "Cool": ["Navy Blue", "Fuchsia", "Deep Purple", "Teal", "Electric Blue"],
            "Neutral": ["Burgundy", "Forest Green", "Eggplant", "Moss Green", "Deep Wine"]
        },
        "Tan": {
            "Warm": ["Terracotta", "Amber", "Warm Red", "Spice", "Cinnamon"],
            "Cool": ["Teal", "Deep Purple", "Emerald", "Sapphire", "Cool Gray"],
            "Neutral": ["Moss Green", "Mauve", "Charcoal", "Taupe", "Oyster"]
        },
        "Dark": {
            "Warm": ["Rich Browns", "Deep Oranges", "Gold", "Copper", "Warm White"],
            "Cool": ["Bright Blues", "Violet", "Cool Grays", "Icy Pink", "Jewel Tones"],
            "Neutral": ["Deep Purples", "Ruby Red", "Onyx", "Slate", "Eggplant"]
        }
    }
    return palette.get(tone, {}).get(undertone, ["Black", "White", "Denim", "Gray", "Navy"])

def get_body_type_recommendations(body_type):
    """Provide detailed clothing recommendations for each body type"""
    recommendations = {
        "Pear": {
            "Best Tops": [
                "V-necks, scoop necks, and boat necks",
                "Tops with detailing on the shoulders or sleeves",
                "Bright colors or patterns on top",
                "Structured jackets that hit at the waist"
            ],
            "Best Bottoms": [
                "Dark colored pants and skirts",
                "A-line skirts that skim over hips",
                "Bootcut or wide-leg pants",
                "High-waisted styles to elongate legs"
            ],
            "Dresses": [
                "Fit and flare silhouettes",
                "Empire waist dresses",
                "Wrap dresses that cinch at the waist",
                "Dresses with detailing on top"
            ],
            "Avoid": [
                "Skinny jeans that emphasize hip width",
                "Tops that end at the widest part of your hips",
                "Tight skirts that cling to hips",
                "Excessive detailing on hips/bottom"
            ],
            "Celebrity Examples": ["Jennifer Lopez", "Beyoncé", "Kim Kardashian"]
        },
        "Inverted Triangle": {
            "Best Tops": [
                "Scoop necks and V-necks",
                "Dark colored tops",
                "Simple, clean designs",
                "Tops that create waist definition"
            ],
            "Best Bottoms": [
                "Flared pants to balance shoulders",
                "Patterned skirts and pants",
                "A-line skirts",
                "Bootcut or wide-leg jeans"
            ],
            "Dresses": [
                "A-line dresses",
                "Wrap dresses",
                "Dresses with full skirts",
                "Empire waist dresses"
            ],
            "Avoid": [
                "Padded shoulders or shoulder detailing",
                "Tight tops with high necklines",
                "Skinny jeans without balancing tops",
                "Strapless styles"
            ],
            "Celebrity Examples": ["Angelina Jolie", "Demi Moore", "Renée Zellweger"]
        },
        "Hourglass": {
            "Best Tops": [
                "Fitted styles that show your waist",
                "Wrap tops",
                "Sweetheart or V-necklines",
                "Structured blazers"
            ],
            "Best Bottoms": [
                "High-waisted pants and skirts",
                "Pencil skirts",
                "Bootcut or straight leg pants",
                "Tailored shorts"
            ],
            "Dresses": [
                "Bodycon dresses",
                "Belted styles",
                "Wrap dresses",
                "Fit-and-flare silhouettes"
            ],
            "Avoid": [
                "Baggy, shapeless clothing",
                "High-necked tops without waist definition",
                "Boxy jackets",
                "Dropped waist styles"
            ],
            "Celebrity Examples": ["Marilyn Monroe", "Sophia Loren", "Salma Hayek"]
        },
        "Rectangle": {
            "Best Tops": [
                "Peplum tops",
                "Ruffled or detailed tops",
                "Off-the-shoulder styles",
                "Tops with waist definition"
            ],
            "Best Bottoms": [
                "High-waisted jeans",
                "A-line skirts",
                "Pleated pants",
                "Patterned bottoms"
            ],
            "Dresses": [
                "Belted dresses",
                "Fit and flare dresses",
                "Shirt dresses with belts",
                "Dresses with ruching or draping"
            ],
            "Avoid": [
                "Boxy, shapeless tops",
                "Straight up-and-down dresses",
                "Tops that hide your waist",
                "Baggy jeans"
            ],
            "Celebrity Examples": ["Cameron Diaz", "Natalie Portman", "Kate Hudson"]
        },
        "Average": {
            "Best Choices": [
                "Most styles work well",
                "Can experiment with different silhouettes",
                "Focus on proportion and fit",
                "Highlight your best features"
            ],
            "Tips": [
                "You can wear both fitted and loose styles",
                "Play with different necklines",
                "Try both high and low waistlines",
                "Experiment with patterns and textures"
            ],
            "Celebrity Examples": ["Jennifer Aniston", "Gwyneth Paltrow", "Sandra Bullock"]
        }
    }
    return recommendations.get(body_type, {})

def get_skincare_recommendations(tone, undertone, texture):
    """Generate personalized skincare routine with more details"""
    base_routine = {
        "Very Fair": {
            "Cleanser": "Gentle non-foaming cleanser (like cream or milk cleansers)",
            "Sunscreen": "SPF 50+ physical sunscreen with zinc oxide",
            "Moisturizer": "Lightweight gel-cream with hyaluronic acid",
            "Special Notes": "Very prone to sun damage - reapply sunscreen every 2 hours"
        },
        "Fair": {
            "Cleanser": "Creamy/milky cleanser or gentle foaming cleanser",
            "Sunscreen": "SPF 50 broad spectrum (chemical/physical combo)",
            "Moisturizer": "Medium-weight lotion with ceramides",
            "Special Notes": "Protect against environmental aggressors"
        },
        "Medium": {
            "Cleanser": "Gel-based cleanser with mild exfoliation",
            "Sunscreen": "SPF 30-50 with antioxidant protection",
            "Moisturizer": "Balanced cream with niacinamide",
            "Special Notes": "Watch for hyperpigmentation"
        },
        "Tan": {
            "Cleanser": "Foaming or clay cleanser for balance",
            "Sunscreen": "SPF 30 with iron oxides for pigmentation protection",
            "Moisturizer": "Rich cream with glycerin",
            "Special Notes": "May need extra hydration in dry climates"
        },
        "Dark": {
            "Cleanser": "Hydrating foam or oil cleanser",
            "Sunscreen": "Tinted SPF 30+ to prevent ashiness",
            "Moisturizer": "Butter-based with shea or mango butter",
            "Special Notes": "Look for products that won't leave white cast"
        }
    }.get(tone, {})
    
    treatments = {
        "Smooth": {
            "Treatment": "Hydration serum with hyaluronic acid",
            "Exfoliation": "Gentle enzymatic exfoliant 1-2x/week"
        },
        "Normal": {
            "Treatment": "Niacinamide serum for balance",
            "Exfoliation": "Lactic acid 2-3x/week"
        },
        "Combination": {
            "Treatment": "Zone-specific care (light on oily areas, rich on dry)",
            "Exfoliation": "Salicylic acid on oily zones, lactic on dry"
        },
        "Rough": {
            "Treatment": "Ceramide cream for barrier repair",
            "Exfoliation": "Glycolic acid 2-3x/week + physical exfoliation 1x/week"
        }
    }.get(texture, {})
    
    undertone_extras = {
        "Warm": {
            "Note": "Use calming ingredients (chamomile, aloe, centella)",
            "Avoid": "Highly acidic products that may cause redness"
        },
        "Cool": {
            "Note": "Try brightening ingredients (vitamin C, licorice root)",
            "Avoid": "Very warm-toned makeup that may look orange"
        },
        "Neutral": {
            "Note": "Balanced ingredients work well",
            "Avoid": "Extreme treatments (very high or low pH)"
        }
    }.get(undertone, {})
    
    return {**base_routine, **treatments, **undertone_extras}



def create_visual_report(results, selfie_path, fullbody_path):
    """Generate comprehensive visual report image with measurements"""
    selfie_img = cv2.imread(selfie_path)
    body_img = cv2.imread(fullbody_path)
    
    if selfie_img is None or body_img is None:
        print("Error loading images for visualization")
        return None
    
    
    selfie_img = cv2.resize(selfie_img, (400, 500))
    body_img = cv2.resize(body_img, (400, 800))
    
    
    report = np.zeros((1000, 1200, 3), dtype=np.uint8)
    report[:] = (240, 240, 240)  # Light gray background
    
    
    report[50:550, 50:450] = selfie_img  # Selfie on left
    report[50:850, 650:1050] = body_img  # Full-body on right
    
    
    skin = results["skin"]
    cv2.putText(report, "SKIN ANALYSIS", (500, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(report, f"Tone: {skin['tone']}", (500, 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(report, f"Undertone: {skin['undertone']}", (500, 140), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(report, f"Texture: {skin['texture']}", (500, 180), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    
    color_mapping = {
        "Peach": (180, 200, 255),
        "Coral": (130, 180, 255),
        "Gold": (50, 215, 255),
        "Cream": (210, 250, 255),
        "Baby Blue": (255, 200, 100),
        "Lavender": (250, 180, 250),
        "Silver": (220, 220, 220),
        "Mint": (200, 255, 200),
        "Dusty Rose": (150, 180, 210),
        "Mauve": (180, 170, 210),
        "Taupe": (180, 190, 200),
        "Black": (0, 0, 0),
        "White": (255, 255, 255),
        "Denim": (150, 100, 50)
    }
    
    for i, color in enumerate(skin['colors'][:5]):
        swatch = np.zeros((30, 30, 3), dtype=np.uint8)
        swatch[:] = color_mapping.get(color, (200, 200, 200))
        report[220+i*40:250+i*40, 500:530] = swatch
        cv2.putText(report, color, (540, 240+i*40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    # Add body analysis
    body = results["body"]
    measurements = results["measurements"]
    
    cv2.putText(report, "BODY ANALYSIS", (50, 600), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(report, f"Type: {body['type']}", (70, 650), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    # Add measurements
    cv2.putText(report, "Measurements:", (70, 700), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.putText(report, f"Shoulder: {measurements['shoulder']}px", (90, 730), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(report, f"Waist: {measurements['waist']}px", (90, 760), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(report, f"Hips: {measurements['hips']}px", (90, 790), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(report, f"Shoulder/Hip Ratio: {measurements['shoulder_hip_ratio']}", (90, 820), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(report, f"Waist/Hip Ratio: {measurements['waist_hip_ratio']}", (90, 850), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    
    cv2.putText(report, "TOP RECOMMENDATIONS:", (500, 600), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    y_pos = 650
    for cat, items in body["recommendations"].items():
        if cat in ["Best Tops", "Best Bottoms", "Dresses"]:
            cv2.putText(report, f"{cat}:", (520, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            y_pos += 30
            for item in items[:3]:  # Show top 3 recommendations per category
                cv2.putText(report, f"- {item}", (540, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                y_pos += 25
    
    
    cv2.putText(report, "SKINCARE ROUTINE", (500, 800), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    y_pos = 850
    for step, product in results["skincare"].items():
        if isinstance(product, str):  
            cv2.putText(report, f"{step}: {product}", (520, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            y_pos += 30
    
    return report



def analyze_images(selfie_path, fullbody_path):
    """Master function to analyze both images with enhanced features"""
    # Process selfie for skin analysis
    face_img, face_coords = detect_face(selfie_path)
    if face_img is None:
        print("Cannot proceed without face detection")
        return None
    
    skin, skin_mask = extract_skin(face_img)
    dominant_color = get_dominant_skin_color(skin, skin_mask)
    if dominant_color is None:
        print("Failed to determine skin color")
        return None
    
    tone, undertone, brightness = classify_skin_tone(dominant_color)
    texture, texture_desc = analyze_skin_texture(face_img)
    
    # Process full-body for proportions
    proportions = detect_body_proportions(fullbody_path, face_coords[2])
    body_type, measurements = determine_body_type(proportions)
    
    # Generate recommendations
    return {
        "skin": {
            "tone": tone,
            "undertone": undertone,
            "texture": texture,
            "colors": get_color_recommendations(tone, undertone)
        },
        "body": {
            "type": body_type,
            "recommendations": get_body_type_recommendations(body_type)
        },
        "measurements": measurements,
        "skincare": get_skincare_recommendations(tone, undertone, texture)
    }


# if(1):
    
#     selfie_path = r"C:\Users\devay\Desktop\GettyImages-2174019459 (1).webp"  # Front-facing close-up
#     fullbody_path = r"C:\Users\devay\Desktop\images.jpeg"  # Front-facing full-body
    
#     print("Starting dual-image analysis with MediaPipe...")
#     results = analyze_images(selfie_path, fullbody_path)
    
#     if results:
#         print("\n=== RESULTS ===")
#         print("Skin Tone:", results["skin"]["tone"])
#         print("Undertone:", results["skin"]["undertone"])
#         print("Texture:", results["skin"]["texture"])
#         print("Recommended Colors:", results["skin"]["colors"][:5])
        
#         print("\nBody Type:", results["body"]["type"])
#         print("Measurements:")
#         print(f"  Shoulder: {results['measurements']['shoulder']}px")
#         print(f"  Waist: {results['measurements']['waist']}px")
#         print(f"  Hips: {results['measurements']['hips']}px")
#         print(f"  Shoulder/Hip Ratio: {results['measurements']['shoulder_hip_ratio']}")
#         print(f"  Waist/Hip Ratio: {results['measurements']['waist_hip_ratio']}")
        
#         print("\nTop Clothing Recommendations:")
#         for cat, items in results["body"]["recommendations"].items():
#             if cat in ["Best Tops", "Best Bottoms", "Dresses"]:
#                 print(f"  {cat}:")
#                 for item in items[:3]:
#                     print(f"    - {item}")
        
#         print("\nSkincare Routine:")
#         for step, product in results["skincare"].items():
#             if isinstance(product, str):
#                 print(f"  {step}: {product}")
        
        
#         report_img = create_visual_report(results, selfie_path, fullbody_path)
#         if report_img is not None:
#             cv2.imwrite("style_analysis_report.jpg", report_img)
#             print("\nVisual report saved as 'style_analysis_report.jpg'")
#     else:
#         print("Analysis failed. Please check your images.")/


import argparse
import cv2  # Assuming you're using OpenCV
# Import your custom analysis functions
# from your_module import analyze_images, create_visual_report

def main():
    parser = argparse.ArgumentParser(description="Analyze style from selfie and full-body images")
    parser.add_argument('--selfie', type=str, required=True, help='Path to the selfie image')
    parser.add_argument('--fullbody', type=str, required=True, help='Path to the full-body image')
    args = parser.parse_args()

    selfie_path = args.selfie
    fullbody_path = args.fullbody

    print("Starting dual-image analysis with MediaPipe...")
    results = analyze_images(selfie_path, fullbody_path)

    if results:
        print("\n=== RESULTS ===")
        print("Skin Tone:", results["skin"]["tone"])
        print("Undertone:", results["skin"]["undertone"])
        print("Texture:", results["skin"]["texture"])
        print("Recommended Colors:", results["skin"]["colors"][:5])
        
        print("\nBody Type:", results["body"]["type"])
        print("Measurements:")
        print(f"  Shoulder: {results['measurements']['shoulder']}px")
        print(f"  Waist: {results['measurements']['waist']}px")
        print(f"  Hips: {results['measurements']['hips']}px")
        print(f"  Shoulder/Hip Ratio: {results['measurements']['shoulder_hip_ratio']}")
        print(f"  Waist/Hip Ratio: {results['measurements']['waist_hip_ratio']}")
        
        print("\nTop Clothing Recommendations:")
        for cat, items in results["body"]["recommendations"].items():
            if cat in ["Best Tops", "Best Bottoms", "Dresses"]:
                print(f"  {cat}:")
                for item in items[:3]:
                    print(f"    - {item}")
        
        print("\nSkincare Routine:")
        for step, product in results["skincare"].items():
            if isinstance(product, str):
                print(f"  {step}: {product}")
        
        report_img = create_visual_report(results, selfie_path, fullbody_path)
        if report_img is not None:
            cv2.imwrite("style_analysis_report.jpg", report_img)
            print("\nVisual report saved as 'style_analysis_report.jpg'")
    else:
        print("Analysis failed. Please check your images.")

if __name__ == "__main__":
    main()
