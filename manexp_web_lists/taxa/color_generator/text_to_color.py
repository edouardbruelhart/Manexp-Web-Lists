import colorsys
import hashlib


def text_to_color(text: str) -> str:
    """
    Returns always the same hexadecimal color for a given text

    Args:
        text: The text to convert to hexadecimal color

    Returns:
        str: Hexadecimal color
    """
    # Hash it
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Get hue from part of the hash
    hue = int(digest[:8], 16) % 360

    # Define saturation and lightness
    saturation = 0.60
    lightness = 0.50

    # Generate RGB
    r, g, b = colorsys.hls_to_rgb(hue / 360.0, lightness, saturation)

    # Convert RGB to hexadecimal
    hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    return hex_color
