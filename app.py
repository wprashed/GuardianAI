import cv2
import numpy as np
import os

def is_nsfw_and_delete(image_path):
    """
    Detects NSFW content (e.g., exposed private parts) and deletes the image if flagged.
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to load image '{image_path}'. Skipping...")
        return

    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define skin color range in HSV
    lower_skin = np.array([0, 48, 80], dtype=np.uint8)  # Lower bound for skin tones
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)  # Upper bound for skin tones

    # Create a mask for skin tones
    skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Apply morphological operations to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)

    # Calculate the percentage of skin pixels in the entire image
    total_pixels = image.shape[0] * image.shape[1]
    skin_pixels = cv2.countNonZero(skin_mask)
    skin_percentage = (skin_pixels / total_pixels) * 100

    # Focus on the lower half of the image (to detect exposed private parts)
    height, width = image.shape[:2]
    lower_half_mask = skin_mask[height // 2:, :]  # Extract the lower half of the skin mask
    lower_half_skin_pixels = cv2.countNonZero(lower_half_mask)
    lower_half_skin_percentage = (lower_half_skin_pixels / (total_pixels / 2)) * 100

    # Find contours in the skin mask to detect large skin regions
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_skin_regions = [cnt for cnt in contours if cv2.contourArea(cnt) > 5000]  # Filter large regions

    print(f"\nProcessing image: {image_path}")
    print(f"Skin Percentage (Entire Image): {skin_percentage:.2f}%")
    print(f"Skin Percentage (Lower Half): {lower_half_skin_percentage:.2f}%")
    print(f"Large Skin Regions: {len(large_skin_regions)}")

    # Define thresholds for NSFW classification
    skin_threshold = 25  # Adjust this value based on testing
    lower_half_skin_threshold = 35  # Higher threshold for the lower half
    min_large_skin_regions = 2  # Minimum number of large skin regions to flag as NSFW

    # Check if the image meets all criteria
    if (
        skin_percentage > skin_threshold and
        lower_half_skin_percentage > lower_half_skin_threshold and
        len(large_skin_regions) >= min_large_skin_regions
    ):
        print("NSFW content (exposed private parts) detected. Deleting the image...")
        try:
            os.remove(image_path)  # Delete the image file
            print(f"Image deleted: {image_path}")
        except Exception as e:
            print(f"Error deleting the image: {e}")
    else:
        print("Image is safe. No action taken.")

def batch_process_folder(folder_path):
    """
    Processes all images in the specified folder and deletes NSFW images.
    """
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    # Supported image extensions
    supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file has a supported image extension
        if any(filename.lower().endswith(ext) for ext in supported_extensions):
            image_path = os.path.join(folder_path, filename)
            is_nsfw_and_delete(image_path)

# Example usage
folder_path = "images"  # Replace with the path to your folder containing images
batch_process_folder(folder_path)