from PIL import Image, ImageEnhance, ImageOps

def load_image(filename):
    try:
        img = Image.open(filename)
        print(f"Image loaded successfully!", img.size)
        return img
    except FileNotFoundError:
        print(f"Could not find '{filename}'. Please check the file path.")
        exit()

if __name__ == "__main__":
    img = load_image("Preprocessing/map.png")
    pixels = img.load()
    print(pixels)

    for x in range(img.width):
        for y in range(img.height):
            if pixels[x, y] != pixels[0,0]:
                pixels[x, y] = (0,0,0)

    
    img.save("Preprocessing/black_white.png")
    rotated = img.rotate(-45)
    rotated.show()
    print("Success!")

    
