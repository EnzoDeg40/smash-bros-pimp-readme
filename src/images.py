import os

from PIL import Image, ImageDraw, ImageFont

color = {
    "p1": (158, 238, 169),
    "p2": (255, 179, 71),
    "p3": (255, 107, 107),
    "p4": (178, 102, 255),
    "p5": (71, 199, 255),
    "p6": (255, 71, 255),
    "p7": (255, 255, 71),
    "p8": (102, 255, 178),
}


def load_image_character(name: str, variante: int = 1) -> Image.Image:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    base_path = os.path.join(project_root, "assets", "fighters")
    if variante == 1:
        filename = f"{name}/main.png"
    else:
        filename = f"{name}/main{variante}.png"
    path = os.path.join(base_path, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist.")

    img = Image.open(path).convert("RGBA")
    return img


def load_image_game(name: str) -> Image.Image:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    base_path = os.path.join(project_root, "assets", "game")
    filename = f"{name}.png"
    path = os.path.join(base_path, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist.")

    img = Image.open(path).convert("RGBA")
    return img


def crop_image_rgba(img: Image.Image) -> Image.Image:
    pixels = img.load()
    width, height = img.size

    left = 0
    for x in range(width):
        found = False
        for y in range(height):
            if pixels[x, y][3] == 255:
                left = x
                found = True
                break
        if found:
            break

    right = width - 1
    for x in range(width - 1, -1, -1):
        found = False
        for y in range(height):
            if pixels[x, y][3] == 255:
                right = x
                found = True
                break
        if found:
            break

    top = 0
    for y in range(height):
        found = False
        for x in range(width):
            if pixels[x, y][3] == 255:
                top = y
                found = True
                break
        if found:
            break

    bottom = height - 1
    for y in range(height - 1, -1, -1):
        found = False
        for x in range(width):
            if pixels[x, y][3] == 255:
                bottom = y
                found = True
                break
        if found:
            break

    return img.crop((left, top, right + 1, bottom + 1))


def resize_image_proportional(
    img: Image.Image, target_width: int | None = None, target_height: int | None = None
) -> Image.Image:
    width, height = img.size

    if target_width is None and target_height is None:
        return img

    if target_width is not None and target_height is not None:
        return img.resize((target_width, target_height), Image.LANCZOS)

    if target_width is not None:
        ratio = target_width / width
        new_height = int(height * ratio)
        return img.resize((target_width, new_height), Image.LANCZOS)

    if target_height is not None:
        ratio = target_height / height
        new_width = int(width * ratio)
        return img.resize((new_width, target_height), Image.LANCZOS)


def crop_image_center(
    img: Image.Image, target_width: int | None = None, target_height: int | None = None
) -> Image.Image:
    width, height = img.size

    if target_width is None and target_height is None:
        return img

    left = 0
    top = 0
    right = width
    bottom = height

    if target_width is not None and target_width < width:
        left = (width - target_width) // 2
        right = left + target_width

    if target_height is not None and target_height < height:
        top = (height - target_height) // 2
        bottom = top + target_height

    return img.crop((left, top, right, bottom))


def layer_images(
    base_img: Image.Image, overlay_img: Image.Image, position: tuple[int, int] = (0, 0)
) -> Image.Image:
    base_img = base_img.convert("RGBA")
    overlay_img = overlay_img.convert("RGBA")

    result_img = base_img.copy()
    result_img.paste(overlay_img, position, overlay_img)

    return result_img


def load_font(font_name: str, size: int) -> ImageFont.FreeTypeFont:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    font_path = os.path.join(project_root, "assets", "fonts", font_name)

    try:
        return ImageFont.truetype(font_path, size)
    except Exception as e:
        print(f"⚠️  Unable to load font {font_name}: {e}")
        return ImageFont.load_default()


def draw_text_username(
    img: Image.Image,
    text: str,
    position: tuple[int, int] | None = None,
    font_name: str = "fonnts.com-kropotkin_bold.otf",
    font_size: int = 32,
    text_color: str | tuple = "black",
    outline_color: str | tuple = "white",
    outline_width: int = 3,
    center_horizontal: bool = True,
    center_vertical: bool = False,
) -> Image.Image:
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = load_font(font_name, font_size)

    text = text.upper()

    # find text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    img_width, img_height = img.size

    # determine position
    if position is None:
        x = (img_width - text_width) / 2 if center_horizontal else 0
        y = (img_height - text_height) / 2 if center_vertical else 0
    else:
        x, y = position
        if center_horizontal:
            x = (img_width - text_width) / 2
        if center_vertical:
            y = y - text_height / 2

    # draw outline
    for offset_x in range(-outline_width, outline_width + 1):
        for offset_y in range(-outline_width, outline_width + 1):
            if offset_x != 0 or offset_y != 0:
                draw.text(
                    (x + offset_x, y + offset_y), text, font=font, fill=outline_color
                )

    # draw main text
    draw.text((x, y), text, font=font, fill=text_color)

    return img


def apply_color_tint(
    img: Image.Image,
    tint_color: tuple[int, int, int] = (158, 238, 169),
    ignore_black: bool = True,
    min_alpha: int = 10,
    min_brightness: int = 10,
) -> Image.Image:
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # ignore transparent pixels
            if a <= min_alpha:
                continue

            # check if it's a shade of gray
            if r == g == b:
                # ignore black if requested
                if ignore_black and r <= min_brightness:
                    continue

                # apply tint based on brightness
                intensity = r / 255.0
                new_r = int(tint_color[0] * intensity)
                new_g = int(tint_color[1] * intensity)
                new_b = int(tint_color[2] * intensity)
                pixels[x, y] = (new_r, new_g, new_b, a)

    return img


def draw_text_player_number(
    img: Image.Image,
    number: int,
    position: tuple[int, int],
    font_name: str = "Gotham Black Regular.ttf",
    font_size: int = 24,
    text_color: str | tuple = "black",
    outline_color: str | tuple = "white",
    outline_width: int = 2,
) -> Image.Image:
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = load_font(font_name, font_size)

    text = str(number)

    x, y = position

    # draw outline
    for offset_x in range(-outline_width, outline_width + 1):
        for offset_y in range(-outline_width, outline_width + 1):
            if offset_x != 0 or offset_y != 0:
                draw.text(
                    (x + offset_x, y + offset_y), text, font=font, fill=outline_color
                )

    # draw main text
    draw.text((x, y), text, font=font, fill=text_color)

    return img


def generate_image(
    username: str, name: str, variante: int = 1, player: int = 0
) -> bool:
    try:
        cpu_img = load_image_game("cpu")
        front_img = load_image_game("front")

        character_img = load_image_character(name, variante=variante)
        character_img = crop_image_rgba(character_img)
        character_img = resize_image_proportional(character_img, target_height=350)
        if player >= 1 and player <= 8:
            cpu_img = apply_color_tint(cpu_img, tint_color=color[f"p{player}"])
            front_img = apply_color_tint(front_img, tint_color=color[f"p{player}"])
        r = layer_images(cpu_img, character_img, position=(0, 30))
        r = layer_images(r, front_img, position=(5, 276))

        r = draw_text_username(
            r,
            text=username.upper(),
            position=(0, 308),
            font_size=32,
            outline_width=0,
            center_horizontal=True,
            center_vertical=True,
        )

        if player >= 1 and player <= 8:
            r = draw_text_player_number(
                r,
                number=f"123456P{player}",
                position=(140, 360),
                font_size=60,
            )

        r.show()
        return True
    except Exception as e:
        print(f"Error generating image for {name}: {e}")
        return False


if __name__ == "__main__":
    generate_image("enzo", "mario", variante=1, player=1)
    generate_image("pamela", "peach", variante=1, player=2)
    generate_image("alex", "link", variante=2, player=3)
    generate_image("chris", "samus", variante=1, player=4)
    generate_image("jordan", "pikachu", variante=1, player=5)
    generate_image("taylor", "kirby", variante=1, player=6)
    generate_image("morgan", "fox", variante=1, player=7)
    generate_image("casey", "yoshi", variante=1, player=8)