from flask import Flask, request, jsonify, url_for
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import logging
import uuid

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

def generate_image_with_text(image_url, font_name, color, position, text="Do you accept credit card?", text_size=36):
    try:
        # Define a browser-like User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }

        # Fetch image from URL with custom User-Agent
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise error for bad HTTP response
        image = Image.open(BytesIO(response.content))
    except requests.RequestException as e:
        logging.error(f"Error fetching image: {e}")
        return None, "Failed to download image"
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return None, "Invalid image format"

    try:
        # Create a drawing context
        draw = ImageDraw.Draw(image)

        # Load the specified font
        font_path = os.path.join("fonts", font_name)  # Assuming fonts are stored in a "fonts" folder
        if not os.path.exists(font_path):
            logging.error(f"Font not found: {font_path}")
            return None, "Font file not found"

        font = ImageFont.truetype(font_path, text_size)  # Using the specified text_size
    except IOError as e:
        logging.error(f"Error loading font: {e}")
        return None, "Font file is invalid or missing"
    except Exception as e:
        logging.error(f"Unexpected error loading font: {e}")
        return None, "Unexpected error in font processing"

    # Get image width and height
    image_width, image_height = image.size

    def wrap_text(text, font, max_width):
        """Wrap text into multiple lines to fit within the given width."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if draw.textlength(test_line, font=font) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    max_width = image_width - 40  # 20 pixels padding on each side
    wrapped_lines = wrap_text(text, font, max_width)

    # Define line height and extra spacing
    try:
        line_height = font.getbbox("A")[3] - font.getbbox("A")[1]
    except Exception:
        line_height = 40  # Fallback height if getbbox() fails
        logging.warning("Using default line height due to getbbox() failure")

    line_spacing = 10
    total_text_height = len(wrapped_lines) * (line_height + line_spacing)

    # Determine Y-position based on selected position
    if position == "top":
        y_position = 20  # Padding from top
    elif position == "middle":
        y_position = (image_height - total_text_height) // 2
    elif position == "bottom":
        y_position = image_height - total_text_height - 20  # Padding from bottom
    else:
        logging.error(f"Invalid position: {position}")
        return None, "Invalid text position"

    try:
        # Convert color from "R,G,B" format to tuple
        text_color = tuple(map(int, color.split(',')))
        if len(text_color) != 3 or not all(0 <= c <= 255 for c in text_color):
            raise ValueError("Invalid RGB values")
    except Exception as e:
        logging.error(f"Invalid color format: {e}")
        return None, "Invalid color format. Use 'R,G,B' (e.g., '255,0,0' for red)"

    shadow_color = (255, 255, 255)  # White shadow for contrast

    # Add the wrapped text with a shadow effect
    y_offset = y_position
    for line in wrapped_lines:
        line_width = draw.textlength(line, font=font)
        x_offset = (image_width - line_width) // 2  # Center text horizontally

        # Draw shadow (offset to create a shadow effect)
        draw.text((x_offset + 2, y_offset + 2), line, font=font, fill=shadow_color)
        # Draw main text
        draw.text((x_offset, y_offset), line, font=font, fill=text_color)

        # Move Y position down for the next line
        y_offset += line_height + line_spacing

    try:
        # Determine output format and save image
        output_format = "PNG"  # Change this if needed
        output_image_name = f"{uuid.uuid4()}.png"  # Generate a unique filename
        output_image_path = os.path.join("static", output_image_name)  # Save in static folder
        image.save(output_image_path, format=output_format)
    except Exception as e:
        logging.error(f"Error saving image: {e}")
        return None, "Error saving the final image"

    # Construct the full URL for the saved image
    full_image_url = request.url_root + 'static/' + output_image_name  # Use request.url_root to get the base URL
    return full_image_url, None

@app.route('/edit_image', methods=['POST'])
def edit_image():
    try:
        # Get parameters from request
        data = request.json
        image_url = data.get('image_url')
        font_name = data.get('font_name')
        color = data.get('color')
        position = data.get('position')
        text = data.get('text', "Do you accept credit card?")  # Existing parameter with a default value
        text_size = data.get('text_size', 36)  # New parameter with a default value of 36

        # Validate inputs
        if not image_url or not font_name or not color or not position:
            logging.warning("Missing required parameters in request")
            return jsonify({"error": "Missing required parameters"}), 400

        # Generate the edited image
        sub_image_url, error_message = generate_image_with_text(image_url, font_name, color, position, text, text_size)  # Pass the new text_size parameter

        if sub_image_url:
            return jsonify({"sub_image_url": sub_image_url}), 200
        else:
            logging.error(f"Image generation failed: {error_message}")
            return jsonify({"error": error_message}), 500

    except Exception as e:
        logging.critical(f"Unexpected server error: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(port=4000)
