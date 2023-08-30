def range_scale(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def generate_distinct_colors(num_colors, min_lightness=0.4, max_lightness=0.7, min_saturation=0.4, max_saturation=0.7, color_offset=0):
    colors = []

    for i in range(num_colors):
        hue = i / num_colors
        saturation = min_saturation + (max_saturation - min_saturation) * (i % 2)
        lightness = min_lightness + (max_lightness - min_lightness) * ((i // 2) % 2)

        red, green, blue = hsl_to_rgb(hue, saturation, lightness)

        truecolor = True
        for color in colors:
            if (abs(color[0] - red) < color_offset and
                    abs(color[1] - green) < color_offset and
                    abs(color[2] - blue) < color_offset):
                truecolor = False
                break
        if truecolor:
            colors.append((int(red), int(green), int(blue)))

    return colors


def hsl_to_rgb(h, s, l):
    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1 / 6: return p + (q - p) * 6 * t
            if t < 1 / 2: return q
            if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1 / 3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1 / 3)

    return r * 255, g * 255, b * 255


if __name__ == "__main__":
    colors = generate_distinct_colors(10000, min_lightness=0.5,max_lightness=1.0, min_saturation=0.5, max_saturation=1.0, color_offset=50)
    count = 0
    for color in colors:
        count += 1
        print(f"{count} - {color}")
