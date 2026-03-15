from PIL import Image, ImageFilter, ImageEnhance


def apply_effect(image_path, effect):

    image = Image.open(image_path)

    if effect == "blur":
        image = image.filter(ImageFilter.GaussianBlur(8))

    elif effect == "sharpen":
        image = image.filter(ImageFilter.SHARPEN)

    elif effect == "bright":
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.6)

    elif effect == "contrast":
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.7)

    elif effect == "bw":
        image = image.convert("L")

    return image