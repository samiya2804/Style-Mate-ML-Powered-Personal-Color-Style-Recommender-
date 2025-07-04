import cv2
import numpy as np
import mediapipe as mp
import os

def get_average_color(image, center, size=5):
    x, y = center
    h, w, _ = image.shape
    half = size // 2
    x_start = max(x - half, 0)
    x_end = min(x + half + 1, w)
    y_start = max(y - half, 0)
    y_end = min(y + half + 1, h)
    region = image[y_start:y_end, x_start:x_end]
    return np.mean(region.reshape(-1, 3), axis=0)

def rgb_to_lab(color):
    rgb_color = np.uint8([[color]])
    lab_color = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2LAB)[0][0]
    L = lab_color[0] * (100 / 255)
    a = lab_color[1] - 128
    b = lab_color[2] - 128
    return np.array([round(L), round(a), round(b)])




def draw_color_swatch(image, position, color_rgb, label):
    cv2.circle(image, position, 15, tuple(map(int, color_rgb[::-1])), -1)  # BGR format
    cv2.putText(image, label, (position[0] + 20, position[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

def extract_colors_from_photo(photo_path):
    image = cv2.imread(photo_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at: {photo_path}")

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True) as face_mesh:
        results = face_mesh.process(image_rgb)

        if not results.multi_face_landmarks:
            raise Exception("No face detected!")

        face = results.multi_face_landmarks[0]
        height, width, _ = image.shape

        def landmark_to_pixel(landmark):
            return int(landmark.x * width), int(landmark.y * height)

        # Key landmarks
        hair_point = landmark_to_pixel(face.landmark[10])
        skin_point = landmark_to_pixel(face.landmark[234])
        eye_point = landmark_to_pixel(face.landmark[468])

        # Get average color
        hair_rgb = get_average_color(image_rgb, hair_point)
        skin_rgb = get_average_color(image_rgb, skin_point)
        eye_rgb = get_average_color(image_rgb, eye_point)

        # LAB conversion
        hair_lab = rgb_to_lab(hair_rgb)
        skin_lab = rgb_to_lab(skin_rgb)
        eye_lab = rgb_to_lab(eye_rgb)

        # Save overlay image
        overlay_image = image.copy()
        draw_color_swatch(overlay_image, hair_point, hair_rgb, "Hair")
        draw_color_swatch(overlay_image, skin_point, skin_rgb, "Skin")
        draw_color_swatch(overlay_image, eye_point, eye_rgb, "Eye")
        swatch_output_path = photo_path.replace(".jpg", "_swatches.jpg")
        cv2.imwrite(swatch_output_path, overlay_image)

        print("✅ Final Extracted Colors:")
        print(f"Hair LAB: {hair_lab} → RGB: {hair_rgb.astype(int).tolist()}")
        print(f"Skin LAB: {skin_lab} → RGB: {skin_rgb.astype(int).tolist()}")
        print(f"Eye  LAB: {eye_lab} → RGB: {eye_rgb.astype(int).tolist()}")
        print(f"Overlay Image saved at: {swatch_output_path}")

        return {
            'hair_lab': hair_lab.tolist(),
            'skin_lab': skin_lab.tolist(),
            'eye_lab': eye_lab.tolist(),
            'hair_rgb': hair_rgb.astype(int).tolist(),
            'skin_rgb': skin_rgb.astype(int).tolist(),
            'eye_rgb': eye_rgb.astype(int).tolist(),
            'overlay_path': swatch_output_path
        }
