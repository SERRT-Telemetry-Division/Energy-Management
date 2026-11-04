from PIL import Image, ImageEnhance, ImageOps

def load_image(filename):
    """
    Loads an image. Returns None if the file does not exist.
    """
    try:
        img = Image.open(filename)
        print(f"Image loaded successfully!", img.size)
        return img
    except FileNotFoundError:
        print(f"Could not find '{filename}'. Please check the file path.")
        return None

def to_black_and_white(img):
    """
    Paints every pixel that is not the background color (taken from the top-left pixel) black.
    Modifies the image in place and returns it.
    """
    pixels = img.load()
    background = pixels[0, 0]

    for x in range(img.width):
        for y in range(img.height):
            if pixels[x, y] != background:
                pixels[x, y] = (0, 0, 0)

    return img

if __name__ == "__main__":
    img = load_image("Preprocessing/map.png")
    if img is None:
        exit()

    to_black_and_white(img)
    img.save("Preprocessing/black_white.png")

    rotated = img.rotate(-45)
    rotated.show()
    print("Success!")
