from PIL import Image, ImageFilter, ImageEnhance, ImageOps

def apply_effect(image_path, effect):

    img = Image.open(image_path).convert("RGB")

    if effect == "hd":
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.5)

    elif effect == "manga":
        img = img.convert("L")
        img = ImageOps.posterize(img.convert("RGB"), 2)

    elif effect == "avatar":
        img = img.filter(ImageFilter.SMOOTH_MORE)

    elif effect == "action":
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    elif effect == "drawing":
        img = img.filter(ImageFilter.CONTOUR)

    elif effect == "artistic":
        img = img.filter(ImageFilter.DETAIL)

    return img