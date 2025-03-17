from PIL import Image, ImageDraw, ImageFont
import textwrap
import uuid

# Open an image file
image = Image.open("image.jpg")

# Create a drawing context
draw = ImageDraw.Draw(image)

# Define the font and size
font = ImageFont.truetype("EmblemaOne-Regular.ttf", 36)

# Text to add
text = "Do you accept credit card?"

# Get the image width and height
image_width, image_height = image.size

# Define the maximum width for the text (with padding)
max_width = image_width - 40  # 20 pixels padding on each side

# Wrap the text based on the maximum width
def wrap_text(text, font, max_width):
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

wrapped_lines = wrap_text(text, font, max_width)

# Calculate the total height of the wrapped text
line_height = font.getbbox("A")[3] - font.getbbox("A")[1]  # Approximate height using a capital letter
total_text_height = len(wrapped_lines) * line_height

# Calculate the position to center the wrapped text
y_position = (image_height - total_text_height) // 2

# Text color (RGB)
text_color = (255, 255, 255)  # White color

# Add the wrapped text to the image (draw each line)
y_offset = y_position
for line in wrapped_lines:
    line_width = draw.textlength(line, font=font)
    x_offset = (image_width - line_width) // 2  # Center horizontally
    draw.text((x_offset, y_offset), line, font=font, fill=text_color)
    y_offset += line_height  # Move the y position down for the next line

# Save the edited image
try:
    output_image_name = f"{uuid.uuid4()}.png"  # Generate a unique filename
    image.save(output_image_name, format="PNG")  # Save with the unique name
    full_image_url = f"http://yourdomain.com/{output_image_name}"  # Replace with your actual domain
    print("Image saved successfully. URL:", full_image_url)
except Exception as e:
    print(f"Error saving image: {e}")

# Optionally, show the image
image.show()
