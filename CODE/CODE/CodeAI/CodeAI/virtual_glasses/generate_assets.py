import os
from PIL import Image, ImageDraw

def create_directory():
    os.makedirs("images", exist_ok=True)

def generate_sunglasses():
    # Create a blank transparent image
    width, height = 400, 150
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw left lens (dark)
    draw.ellipse([20, 20, 170, 130], fill=(0, 0, 0, 200))
    # Draw right lens (dark)
    draw.ellipse([230, 20, 380, 130], fill=(0, 0, 0, 200))
    # Draw bridge
    draw.line([170, 50, 230, 50], fill=(0, 0, 0, 255), width=8)
    # Draw arms
    draw.line([0, 50, 20, 50], fill=(0, 0, 0, 255), width=8)
    draw.line([380, 50, 400, 50], fill=(0, 0, 0, 255), width=8)
    
    img.save("images/sunglasses.png")
    print("Created images/sunglasses.png")

def generate_prescription():
    width, height = 400, 150
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Left lens frame (thick border, transparent inside)
    draw.ellipse([20, 20, 170, 130], outline=(50, 50, 50, 255), width=8)
    # Right lens frame
    draw.ellipse([230, 20, 380, 130], outline=(50, 50, 50, 255), width=8)
    # Bridge
    draw.line([170, 50, 230, 50], fill=(50, 50, 50, 255), width=6)
    
    img.save("images/prescription.png")
    print("Created images/prescription.png")

def generate_fashion():
    width, height = 400, 150
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Left lens (pink tinted)
    draw.polygon([(20, 20), (170, 20), (150, 130), (40, 130)], outline=(255, 105, 180, 255), fill=(255, 105, 180, 100))
    # Right lens (pink tinted)
    draw.polygon([(230, 20), (380, 20), (360, 130), (250, 130)], outline=(255, 105, 180, 255), fill=(255, 105, 180, 100))
    # Bridge
    draw.line([170, 40, 230, 40], fill=(255, 105, 180, 255), width=5)
    
    img.save("images/fashion.png")
    print("Created images/fashion.png")

if __name__ == "__main__":
    print("Generating default asset images...")
    create_directory()
    generate_sunglasses()
    generate_prescription()
    generate_fashion()
    print("Done!")
