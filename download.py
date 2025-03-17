import requests

# URL of the image from Replicate
image_url = 'https://replicate.delivery/xezq/87wB8iexhQVRGy3o5bhfEcmzupqoLdnz2dAeojBsM6admKzoA/out-0.webp'

# Define the custom User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Send a GET request to fetch the image with the custom User-Agent
response = requests.get(image_url, headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Open a file in write-binary mode and save the content
    with open('downloaded_image.png', 'wb') as file:
        file.write(response.content)
    print("Image downloaded successfully!")
else:
    print(f"Failed to download image. HTTP Status code: {response.status_code}")
