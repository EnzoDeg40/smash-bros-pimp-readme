import json
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

# on the card, before it is exported at its final size
FACE_HEIGHT = 110
FACE_Y = 125
MIN_CHARACTER_BOTTOM = 300
DEFAULT_FRAMING = (0.5, 0.15, 0.2)
BAND_STRIPE_PERIOD = 14
BAND_STRIPE_SLANT = 0.5
BAND_STRIPE_DEPTH = 0.15
CONTROLLER_OPACITY = 0.8

color = {
    "p1": (252, 4, 4),
    "p2": (4, 100, 236),
    "p3": (244, 172, 4),
    "p4": (4, 156, 28),
    "p5": (252, 116, 12),
    "p6": (4, 180, 204),
    "p7": (252, 124, 188),
    "p8": (116, 76, 244),
}

plate_color = {
    "p1": (228, 164, 156),
    "p2": (156, 188, 228),
    "p3": (236, 212, 140),
    "p4": (156, 212, 164),
    "p5": (244, 196, 156),
    "p6": (156, 220, 228),
    "p7": (236, 180, 192),
    "p8": (164, 148, 220),
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


def load_image_controller(name: str) -> Image.Image:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    base_path = os.path.join(project_root, "assets", "controllers")
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


def load_framing(name: str, variante: int = 1) -> tuple[float, float, float]:
    # where the face is on the cropped image: x and y centers, then its height,
    # all as ratios. Only variants with a different pose have their own entry
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    with open(os.path.join(project_root, "assets", "framing.json")) as f:
        framing = json.load(f)

    poses = framing.get(name, {})
    return tuple(poses.get(str(variante), poses.get("1", DEFAULT_FRAMING)))


def frame_on_face(
    img: Image.Image, framing: tuple[float, float, float], card_width: int
) -> tuple[Image.Image, tuple[int, int]]:
    face_x, face_y, face_height = framing
    img = resize_image_proportional(
        img, target_height=round(FACE_HEIGHT / face_height)
    )

    x = round(card_width / 2 - face_x * img.width)
    y = round(FACE_Y - face_y * img.height)
    # short characters must still reach the nameplate
    y = max(y, MIN_CHARACTER_BOTTOM - img.height)

    return img, (x, y)


def card_inner_mask(card_img: Image.Image, max_border_brightness: int = 15) -> Image.Image:
    card_img = card_img.convert("RGBA")
    pixels = card_img.load()
    width, height = card_img.size

    # white pixels stop the fill: only the transparent margin and the border let it through
    mask = Image.new("L", card_img.size, 0)
    mask_pixels = mask.load()
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a > 0 and max(r, g, b) > max_border_brightness:
                mask_pixels[x, y] = 255

    ImageDraw.floodfill(mask, (0, 0), 128)

    return mask.point(lambda value: 0 if value == 128 else 255)


def clip_to_mask(
    img: Image.Image, mask: Image.Image, position: tuple[int, int] = (0, 0)
) -> Image.Image:
    layer = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    layer.paste(img, position)
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))

    return layer


def crop_transparent_margin(img: Image.Image, min_alpha: int = 128) -> Image.Image:
    alpha = img.getchannel("A")

    return img.crop(alpha.point(lambda value: 255 if value >= min_alpha else 0).getbbox())


def layer_images(
    base_img: Image.Image, overlay_img: Image.Image, position: tuple[int, int] = (0, 0)
) -> Image.Image:
    base_img = base_img.convert("RGBA")
    overlay_img = overlay_img.convert("RGBA")

    # alpha_composite rather than paste: paste would make the card see-through
    # wherever the overlay is semi-transparent
    result_img = base_img.copy()
    result_img.alpha_composite(overlay_img, dest=position)

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
    font_name: str = "Gotham Black Regular.ttf",
    font_size: int = 32,
    text_color: str | tuple = "black",
    outline_color: str | tuple = "white",
    outline_width: int = 3,
    center_horizontal: bool = True,
    center_vertical: bool = False,
    max_width: int | None = None,
) -> Image.Image:
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = load_font(font_name, font_size)

    # find text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    # shrink long names so they stay inside the nameplate
    if max_width is not None and text_width > max_width:
        font = load_font(font_name, int(font_size * max_width / text_width))
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

    # center on capital letters, so accents and descenders don't shift the baseline
    _, cap_top, _, cap_bottom = font.getbbox("H")
    text_height = cap_bottom - cap_top
    img_width, img_height = img.size

    # determine position
    if position is None:
        x = (img_width - text_width) / 2 if center_horizontal else 0
        y = (img_height - text_height) / 2 - cap_top if center_vertical else 0
    else:
        x, y = position
        if center_horizontal:
            x = (img_width - text_width) / 2
        if center_vertical:
            y = y - text_height / 2 - cap_top

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


def tint_front(
    front_img: Image.Image,
    band_color: tuple[int, int, int],
    nameplate_color: tuple[int, int, int],
    min_nameplate_brightness: int = 150,
    band_brightness: int = 130,
    max_striped_brightness: int = 116,
    min_alpha: int = 10,
    min_brightness: int = 10,
) -> Image.Image:
    front_img = front_img.convert("RGBA")
    pixels = front_img.load()
    width, height = front_img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # only shades of gray are tinted, black stays black
            if a <= min_alpha or not r == g == b or r <= min_brightness:
                continue

            if r >= min_nameplate_brightness:
                # the nameplate is opaque: the character must not show through
                intensity = r / 255.0
                tint = nameplate_color
                a = 255
            else:
                # the band's lightest gray gives the player color itself
                intensity = min(r / band_brightness, 1.0)
                tint = band_color
                # the dark side of the band has soft diagonal stripes
                if r <= max_striped_brightness:
                    wave = math.sin(
                        2 * math.pi * (x + BAND_STRIPE_SLANT * y) / BAND_STRIPE_PERIOD
                    )
                    intensity *= 1 - BAND_STRIPE_DEPTH * (0.5 + 0.5 * wave)

            pixels[x, y] = (
                int(tint[0] * intensity),
                int(tint[1] * intensity),
                int(tint[2] * intensity),
                a,
            )

    return front_img


def draw_text_player_number(
    img: Image.Image,
    number: int,
    position: tuple[int, int],
    font_name: str = "Gotham Black Regular.ttf",
    font_size: int = 24,
    text_color: str | tuple = "black",
    outline_color: str | tuple = "white",
    outline_width: int = 5,
    outline_offset: tuple[int, int] = (2, 2),
) -> Image.Image:
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = load_font(font_name, font_size)

    text = str(number)

    x, y = position

    # draw outline, thicker on the lower right
    outline = Image.new("L", img.size, 0)
    ImageDraw.Draw(outline).text(
        (x + outline_offset[0], y + outline_offset[1]),
        text,
        font=font,
        fill=255,
        stroke_width=outline_width,
        stroke_fill=255,
    )

    # what the fill can't reach from outside is the inside of a P, 4, 6 or 8: it stays white
    reached = outline.point(lambda value: 255 if value >= 128 else 0)
    ImageDraw.floodfill(reached, (0, 0), 128)
    holes = reached.point(lambda value: 255 if value == 0 else 0)
    outline = ImageChops.lighter(outline, holes.filter(ImageFilter.MaxFilter(3)))
    img.paste(outline_color, mask=outline)

    # draw main text
    draw.text((x, y), text, font=font, fill=text_color)

    return img


def draw_controller_icon(
    img: Image.Image,
    controller: str,
    center: tuple[int, int] = (62, 390),
    max_size: tuple[int, int] = (64, 44),
) -> Image.Image:
    icon = load_image_controller(controller)
    ratio = min(max_size[0] / icon.width, max_size[1] / icon.height)
    icon = icon.resize(
        (round(icon.width * ratio), round(icon.height * ratio)), Image.LANCZOS
    )
    # not fully opaque: the band color shows through the icon
    icon.putalpha(icon.getchannel("A").point(lambda a: int(a * CONTROLLER_OPACITY)))
    position = (center[0] - icon.width // 2, center[1] - icon.height // 2)

    return layer_images(img, icon, position=position)


def generate_image(
    username: str,
    name: str,
    variante: int = 1,
    player: int = 0,
    show: bool = False,
    controller: str | None = None,
) -> Image.Image | None:
    try:
        cpu_img = load_image_game("cpu")
        front_img = load_image_game("front")

        character_img = load_image_character(name, variante=variante)
        character_img = crop_image_rgba(character_img)
        character_img, character_position = frame_on_face(
            character_img, load_framing(name, variante), cpu_img.width
        )
        inner_mask = card_inner_mask(cpu_img)
        if player >= 1 and player <= 8:
            cpu_img = apply_color_tint(cpu_img, tint_color=color[f"p{player}"])
            front_img = tint_front(
                front_img,
                band_color=color[f"p{player}"],
                nameplate_color=plate_color[f"p{player}"],
            )
        character_img = clip_to_mask(character_img, inner_mask, position=character_position)
        r = layer_images(cpu_img, character_img)
        r = layer_images(r, front_img, position=(5, 276))

        r = draw_text_username(
            r,
            text=username,
            position=(0, 307),
            font_size=32,
            outline_width=0,
            center_horizontal=True,
            center_vertical=True,
            max_width=199,
        )

        if player >= 1 and player <= 8:
            r = draw_text_player_number(
                r,
                number=f"P{player}",
                position=(140, 360),
                font_size=60,
            )

        if controller:
            r = draw_controller_icon(r, controller)

        r = crop_transparent_margin(r)
        r = resize_image_proportional(r, target_width=200)

        if show:
            r.show()
        return r
    except Exception as e:
        print(f"Error generating image for {name}: {e}")
        return None


if __name__ == "__main__":
    generate_image("enzo", "mario", variante=1, player=1, show=True)
    generate_image("pamela", "peach", variante=1, player=2, show=True)
    generate_image("alex", "link", variante=2, player=3, show=True)
    generate_image("chris", "samus", variante=1, player=4, show=True)
    generate_image("jordan", "pikachu", variante=1, player=5, show=True)
    generate_image("taylor", "kirby", variante=1, player=6, show=True)
    generate_image("morgan", "fox", variante=1, player=7, show=True)
    generate_image("casey", "yoshi", variante=1, player=8, show=True)