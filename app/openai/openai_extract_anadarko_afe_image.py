from openai import OpenAI
import base64
import json
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io
import os

def extract_images_from_pdf(pdf_path, output_folder="extracted_images"):
    """Extract images from a PDF and save them as PNG files."""
    os.makedirs(output_folder, exist_ok=True)
    images = convert_from_path(pdf_path)
    
    image_paths = []
    for i, img in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        img.save(image_path, "PNG")
        image_paths.append(image_path)
    
    return image_paths

def contains_new_drill_text(image_path):
    """Check if the image contains the text 'NEW DRILL' using OCR."""
    text = pytesseract.image_to_string(Image.open(image_path))
    return "NEW DRILL" in text.upper()

def encode_image(image_path):
    """Convert image to Base64 for OpenAI API."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def extract_text_from_image(image_path):
    """Use OpenAI GPT-4V model to extract text from an image."""
    image_base64 = encode_image(image_path)

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
                    Extract the lines of text between the line starting with 'NEW DRILL' and "END OF TERMINUS"
                    """
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": """
                        Extract the lines of text between the line starting with 'NEW DRILL' and "END OF TERMINUS"""
                    },
                    {"type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        temperature=0,
        max_tokens=1000
    )

    # Convert response to dictionary if necessary
    response_dict = response.to_dict() if hasattr(response, "to_dict") else response

        # Access content correctly
    content = ""
    choices = response_dict.get("choices", [])
    if choices and "message" in choices[0]:
        content = choices[0]["message"].get("content", "").strip().replace("\n", " ")
    
    return content

def process_pdf(pdf_path):
    """Process a PDF, extract images, filter by 'NEW DRILL', and extract text using GPT-4V."""
    images = extract_images_from_pdf(pdf_path)
    extracted_data = []

    for image_path in images:
        if contains_new_drill_text(image_path):
            extracted_text = extract_text_from_image(image_path)
            extracted_data.append(extracted_text)

    return extracted_data

def save_json(data, filename="output.json"):
    """Save extracted data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    print(f"Extracted data saved to {filename}")

if __name__ == "__main__":
    pdf_path = "MOOSEHORN_54_1_41_44-pages.pdf"

    extracted_data = process_pdf(pdf_path)

    if extracted_data:
        print("Extracted JSON:\n", json.dumps(extracted_data, indent=4))
        save_json(extracted_data)
    else:
        print("No relevant 'NEW DRILL' images found in the PDF.")
