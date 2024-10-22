# Created At: 2024-10-22
# Author: Sanath Narasimhan

import cv2
from PIL import Image
import os
import io
from bg_remover import initialize_api_key, remove_background_from_image
from image2pixel import pixelate

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = initialize_api_key()

def video_to_frames(video_path, output_dir, frame_rate=1):
    """
    Converts a video into frames and saves them as images.

    :param video_path: Path to the input video file
    :param output_dir: Directory to save the extracted frames
    :param frame_rate: Save one frame per 'frame_rate' seconds
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames
    duration = frame_count / fps  # Duration of the video in seconds

    print(f"Video FPS: {fps}, Frame Count: {frame_count}, Duration: {duration:.2f} seconds")

    # Read and process frames
    count = 0
    saved_frame_count = 0
    success, frame = cap.read()

    while success:
        # Save one frame per 'frame_rate' seconds
        if count % int(fps * frame_rate) == 0:
            # Convert the frame (which is in OpenCV's BGR format) to RGB format
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            pil_image_no_background = remove_background_from_image(pil_image,api_key)

            if pil_image_no_background:
                # Convert bytes back to PIL Image
                pil_image_no_background = Image.open(io.BytesIO(pil_image_no_background))

                # Save the frame as an image
                frame_filename = os.path.join(output_dir, f"frame_noBG_{saved_frame_count:05d}.png")
                pil_image_no_background.save(frame_filename)
                print(f"Saved frame: {frame_filename}")


                saved_frame_count += 1

            else:
                # Save the frame as an image
                frame_filename = os.path.join(output_dir, f"frame_{saved_frame_count:05d}.png")
                pil_image.save(frame_filename)
                print(f"Saved frame: {frame_filename}")


                saved_frame_count += 1

        # Read the next frame
        success, frame = cap.read()
        count += 1

    # Release the video capture object
    cap.release()
    print(f"Total frames saved: {saved_frame_count}")

def frames_to_gif(frames_dir, output_gif, duration=100, loop=0):
    """
    Converts a sequence of frames into a GIF.
    
    :param frames_dir: Directory where frames are stored
    :param output_gif: Path to the output GIF file
    :param duration: Duration (in milliseconds) for each frame
    :param loop: Number of loops in the GIF (0 means infinite loop)
    """
    # Collect all frame filenames and sort them
    frames = [os.path.join(frames_dir, f) for f in sorted(os.listdir(frames_dir)) if f.endswith(".png")]
    
    # Ensure frames exist
    if not frames:
        print("No frames found in the specified directory.")
        return
    
    # Open each frame, convert to pixel style, and append to a list
    #images = [Image.open(frame) for frame in frames]
    images = [pixelate(frame, width=175, dither='Floyd-Steinberg', strength=25, palette_name='app') for frame in frames]
    
    # Save as an animated GIF
    images[0].save(output_gif, save_all=True, append_images=images[1:], duration=duration, loop=loop, disposal=2, optimize=True)
    print(f"GIF saved at {output_gif}")

# Example usage
"""
video_path = "samples/thinking.mp4"  # Path to your video file
output_dir = "frames/thinking"  # Directory where the frames will be saved
video_to_frames(video_path, output_dir, frame_rate=1)  # Extract 1 frame per second
"""
output_dir = "frames/bombastic"

output_gif = "bombastic_animation_500.gif"  # Path where the GIF will be saved
frames_to_gif(output_dir, output_gif, duration=500, loop=0)  # 100 ms per frame, infinite loop