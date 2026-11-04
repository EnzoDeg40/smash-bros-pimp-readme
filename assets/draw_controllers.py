import math
import os

from PIL import Image, ImageDraw

OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "controllers")
SCALE = 4
CANVAS = 1000
ICON_SIZE = 320
WHITE = 255
HOLE = 0


class Icon:
    def __init__(self):
        self.mask = Image.new("L", (CANVAS * SCALE, CANVAS * SCALE), 0)
        self.draw = ImageDraw.Draw(self.mask)
        self.angle = 0
        self.offset = (0, 0)
        self.flip = 1

    def place(self, angle=0, offset=(0, 0), flip=1):
        self.angle = math.radians(angle)
        self.offset = offset
        self.flip = flip

    def point(self, x, y):
        x *= self.flip
        rotated_x = x * math.cos(self.angle) - y * math.sin(self.angle)
        rotated_y = x * math.sin(self.angle) + y * math.cos(self.angle)
        return (
            (rotated_x + self.offset[0]) * SCALE,
            (rotated_y + self.offset[1]) * SCALE,
        )

    def shape(self, points, fill=WHITE):
        self.draw.polygon([self.point(*p) for p in smooth(points)], fill=fill)

    def polygon(self, points, fill=WHITE):
        self.draw.polygon([self.point(*p) for p in points], fill=fill)

    def circle(self, x, y, radius, fill=WHITE):
        cx, cy = self.point(x, y)
        r = radius * SCALE
        self.draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)

    def line(self, points, width, fill=WHITE, curved=False):
        path = smooth(points, closed=False) if curved else points
        self.draw.line(
            [self.point(*p) for p in path],
            fill=fill,
            width=width * SCALE,
            joint="curve",
        )
        self.circle(*path[0], width / 2, fill)
        self.circle(*path[-1], width / 2, fill)

    def rect(self, x0, y0, x1, y1, radius=0, fill=WHITE):
        self.draw.rounded_rectangle(
            (x0 * SCALE, y0 * SCALE, x1 * SCALE, y1 * SCALE),
            radius=radius * SCALE,
            fill=fill,
        )

    def cross(self, x, y, size, thickness, fill=HOLE):
        self.line([(x - size, y), (x + size, y)], thickness, fill)
        self.line([(x, y - size), (x, y + size)], thickness, fill)

    def stick(self, x, y, radius):
        self.circle(x, y, radius, HOLE)
        self.circle(x, y, radius * 0.55, WHITE)

    def buttons(self, x, y, spread, radius):
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            self.circle(x + dx * spread, y + dy * spread, radius, HOLE)

    def save(self, name):
        cropped = self.mask.crop(self.mask.getbbox())
        ratio = ICON_SIZE / max(cropped.size)
        size = (round(cropped.width * ratio), round(cropped.height * ratio))
        icon = Image.new("RGBA", size, (255, 255, 255, 0))
        icon.putalpha(cropped.resize(size, Image.LANCZOS))
        icon.save(os.path.join(OUTPUT_FOLDER, f"{name}.png"))


def smooth(points, closed=True, steps=24):
    # Catmull-Rom spline through the points
    count = len(points)
    segments = count if closed else count - 1
    result = []
    for i in range(segments):
        if closed:
            p0, p1 = points[(i - 1) % count], points[i]
            p2, p3 = points[(i + 1) % count], points[(i + 2) % count]
        else:
            p0, p1 = points[max(i - 1, 0)], points[i]
            p2, p3 = points[i + 1], points[min(i + 2, count - 1)]
        for step in range(steps):
            t = step / steps
            result.append(
                tuple(
                    0.5
                    * (
                        2 * p1[axis]
                        + (p2[axis] - p0[axis]) * t
                        + (2 * p0[axis] - 5 * p1[axis] + 4 * p2[axis] - p3[axis]) * t**2
                        + (3 * p1[axis] - p0[axis] - 3 * p2[axis] + p3[axis]) * t**3
                    )
                    for axis in (0, 1)
                )
            )
    if not closed:
        result.append(points[-1])
    return result


def symmetric(half):
    # half goes from the top center to the bottom center along the left side
    return half + [(1000 - x, y) for x, y in reversed(half[1:-1])]


def gamecube():
    icon = Icon()
    icon.shape(
        symmetric(
            [
                (500, 290),
                (380, 250),
                (260, 220),
                (150, 255),
                (70, 370),
                (35, 530),
                (60, 700),
                (135, 770),
                (215, 730),
                (275, 640),
                (345, 600),
                (425, 590),
                (500, 600),
            ]
        )
    )
    icon.stick(245, 400, 88)
    icon.cross(375, 505, 38, 24)
    icon.circle(640, 515, 50, HOLE)
    icon.circle(640, 515, 25, WHITE)
    icon.circle(765, 375, 68, HOLE)
    icon.circle(645, 405, 32, HOLE)
    icon.line([(868, 325), (880, 440)], 42, HOLE)
    icon.line([(680, 285), (790, 262)], 42, HOLE)
    icon.save("gamecube")


def xbox():
    icon = Icon()
    icon.shape(
        symmetric(
            [
                (500, 230),
                (360, 222),
                (240, 232),
                (165, 290),
                (112, 400),
                (62, 560),
                (40, 700),
                (75, 785),
                (150, 780),
                (232, 695),
                (312, 610),
                (400, 580),
                (500, 580),
            ]
        )
    )
    icon.stick(290, 350, 74)
    icon.cross(392, 490, 44, 26)
    icon.stick(608, 490, 66)
    icon.buttons(715, 350, 64, 31)
    icon.circle(500, 300, 36, HOLE)
    icon.save("xbox")


def ps5():
    icon = Icon()
    icon.shape(
        symmetric(
            [
                (500, 225),
                (300, 210),
                (185, 222),
                (125, 285),
                (80, 430),
                (35, 640),
                (25, 790),
                (70, 850),
                (140, 815),
                (222, 685),
                (312, 618),
                (400, 610),
                (500, 610),
            ]
        )
    )
    icon.rect(345, 235, 655, 430, 30, HOLE)
    icon.rect(363, 253, 637, 412, 18, WHITE)
    icon.stick(372, 520, 64)
    icon.stick(628, 520, 64)
    icon.cross(215, 365, 46, 28)
    x, y = 785, 365
    icon.polygon([(x, y - 92), (x - 34, y - 34), (x + 34, y - 34)], HOLE)
    icon.circle(x + 62, y, 30, HOLE)
    icon.line([(x - 22, y + 40), (x + 22, y + 84)], 16, HOLE)
    icon.line([(x + 22, y + 40), (x - 22, y + 84)], 16, HOLE)
    icon.rect(x - 90, y - 28, x - 34, y + 28, 4, HOLE)
    icon.save("ps5")


def keyboard():
    icon = Icon()
    icon.rect(30, 270, 970, 730, 54)
    key_height = 74
    gap = 20
    for row, (start, keys) in enumerate(((84, 9), (84, 9), (112, 8))):
        top = 318 + row * (key_height + gap)
        for key in range(keys):
            left = start + key * 95
            icon.rect(left, top, left + 72, top + key_height, 12, HOLE)
    top = 318 + 3 * (key_height + gap)
    icon.rect(84, top, 156, top + key_height, 12, HOLE)
    icon.rect(179, top, 251, top + key_height, 12, HOLE)
    icon.rect(274, top, 726, top + key_height, 12, HOLE)
    icon.rect(749, top, 821, top + key_height, 12, HOLE)
    icon.rect(844, top, 916, top + key_height, 12, HOLE)
    icon.save("keyboard")


def switch():
    icon = Icon()
    icon.rect(170, 70, 470, 930, 130)
    icon.rect(320, 70, 470, 930, 22)
    icon.rect(530, 70, 830, 930, 130)
    icon.rect(530, 70, 680, 930, 22)
    icon.stick(325, 310, 86)
    icon.buttons(325, 630, 74, 36)
    icon.buttons(675, 310, 74, 36)
    icon.stick(675, 630, 86)
    icon.save("switch")


def switch_pro():
    icon = Icon()
    icon.shape(
        symmetric(
            [
                (500, 240),
                (330, 232),
                (215, 242),
                (135, 320),
                (85, 470),
                (45, 650),
                (50, 780),
                (115, 830),
                (190, 780),
                (268, 665),
                (345, 605),
                (500, 600),
            ]
        )
    )
    icon.stick(285, 355, 78)
    icon.cross(395, 500, 44, 26)
    icon.stick(605, 500, 70)
    icon.buttons(718, 355, 66, 32)
    icon.rect(420, 300, 468, 348, 6, HOLE)
    icon.circle(556, 324, 27, HOLE)
    icon.save("switch_pro")


def wii():
    icon = Icon()
    icon.line(
        [(235, 800), (235, 915), (390, 965), (560, 965), (650, 915)],
        20,
        curved=True,
    )
    icon.rect(530, 40, 770, 930, 76)
    icon.cross(650, 200, 62, 32)
    icon.circle(650, 400, 50, HOLE)
    icon.circle(650, 545, 22, HOLE)
    icon.circle(650, 690, 34, HOLE)
    icon.circle(650, 805, 34, HOLE)
    icon.shape(
        [
            (235, 300),
            (330, 385),
            (355, 550),
            (305, 760),
            (235, 810),
            (165, 760),
            (115, 550),
            (140, 385),
        ]
    )
    icon.stick(235, 440, 64)
    icon.save("wii")


def tablet():
    icon = Icon()
    icon.rect(30, 300, 970, 790, 52)
    icon.rect(225, 360, 915, 730, 22, HOLE)
    for top in (370, 480, 590):
        icon.rect(90, top, 170, top + 75, 14, HOLE)
    # hit circle on the active area, for the osu! players
    icon.circle(390, 545, 88, WHITE)
    icon.circle(390, 545, 58, HOLE)
    # pen
    tip = (560, 610)
    tail = (880, 90)
    length = math.dist(tip, tail)
    ux, uy = (tail[0] - tip[0]) / length, (tail[1] - tip[1]) / length
    neck = (tip[0] + ux * 90, tip[1] + uy * 90)
    icon.line([neck, tail], 112, HOLE)
    icon.line([neck, tail], 68, WHITE)
    icon.polygon(
        [
            tip,
            (neck[0] - uy * 34, neck[1] + ux * 34),
            (neck[0] + uy * 34, neck[1] - ux * 34),
        ]
    )
    icon.save("tablet")


def steam_frame():
    icon = Icon()
    for flip, x in ((1, 290), (-1, 710)):
        icon.place(angle=12 * flip, offset=(x, 440), flip=flip)
        icon.line(
            [(-140, -160), (-235, -60), (-240, 150), (-170, 300), (-80, 330)],
            36,
            curved=True,
        )
        icon.shape(
            [
                (-135, -190),
                (0, -240),
                (135, -190),
                (165, -70),
                (122, 60),
                (98, 220),
                (88, 390),
                (40, 450),
                (-40, 450),
                (-88, 390),
                (-98, 220),
                (-122, 60),
                (-165, -70),
            ]
        )
        icon.stick(-20, -120, 78)
        icon.circle(68, 10, 34, HOLE)
        icon.circle(-16, 40, 34, HOLE)
    icon.save("steam_frame")


if __name__ == "__main__":
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    gamecube()
    xbox()
    ps5()
    keyboard()
    switch()
    switch_pro()
    wii()
    tablet()
    steam_frame()
