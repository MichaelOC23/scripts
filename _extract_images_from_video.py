    
import os
import sys
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from reportlab.pdfgen import canvas
from PIL import Image

def extract_frames(video_path, output_dir, interval=5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    os.system(f'ffmpeg -i "{video_path}" -vf "fps=1/{interval}" "{output_dir}/frame_%04d.png"')

def compare_images(img1, img2, threshold=0.95):
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    similarity_index, _ = ssim(img1_gray, img2_gray, full=True)
    print(f"\033[1;34mSimilarity index: {similarity_index}\033[0m")
    return similarity_index < threshold

def remove_similar_images(image_dir, threshold=0.9):
    images = sorted(os.listdir(image_dir))
    last_img = None
    
    for image in images:
        img_path = os.path.join(image_dir, image)
        img = cv2.imread(img_path)
        
        if last_img is None:
            last_img = img
            continue
        
        if not compare_images(last_img, img, threshold):
            print(f"\033[1;95mRemoving {img_path}\033[0m")
            os.remove(img_path)
        else:
            print(f"\033[1;96mRetaining {img_path}\033[0m")
            last_img = img

def create_pdf_from_images(image_dir, pdf_path):
    images = sorted([img for img in os.listdir(image_dir) if img.endswith(('.png', '.jpg', '.jpeg'))])
    
    c = canvas.Canvas(pdf_path)

    for image in images:
        img_path = os.path.join(image_dir, image)
        img = Image.open(img_path)
        width, height = img.size
        
        # Create a new page with the size of the image
        c.setPageSize((width, height))
        
        # Draw the image at full size
        c.drawImage(img_path, 0, 0, width=width, height=height)
        c.showPage()
    
    c.save()

def process_videos_in_folder(folder_path=None, interval=5, threshold=0.9):
    if folder_path is None:
        folder_path = os.path.dirname(os.path.abspath(__file__))

    count = 0
    total = len([filename for filename in os.listdir(folder_path) if filename.endswith(('.mp4', '.mov', '.m4v'))])
    for filename in os.listdir(folder_path):
        count += 1
        print(f"\033[1;94mProcessing video {count}/{total}: {filename}\033[0m")
        if filename.endswith(('.mp4', '.mov', '.m4v')):
            video_path = os.path.join(folder_path, filename)
            output_dir = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_images_")
            pdf_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}_frames.pdf")
            if os.path.exists(pdf_path):
                print(f"\033[1;93mPDF already exists: {pdf_path}\033[0m")
                continue
            
            # Extract frames
            extract_frames(video_path, output_dir, interval)
            
            # Remove similar images
            remove_similar_images(output_dir, threshold)
            
            # Create PDF from remaining images
            create_pdf_from_images(output_dir, pdf_path)
            
            # Remove the images folder
            os.system(f'rm -r "{output_dir}"')
        
            
            

if __name__ == "__main__":
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    process_videos_in_folder(folder_path, interval=2, threshold=0.95)