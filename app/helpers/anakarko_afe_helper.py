import boto3
import os
from pdf2image import convert_from_path
from PIL import Image
from io import BytesIO
import re
from openai import OpenAI
import fitz
import json

sections = ["SURFACE LOCATION", "PENETRATION POINT"]

attribute_regex_patterns = {
    "Well Name":  r"WELL NO\.\s*(\S+)",
    "Abstract": r"\bA-\d+\b",
    "Section": r"Section\s+(\d+)",
    "Block": r"Blk\.\s*(\d+)",
    "Township": r"TSP [^,]*",
    "County": r"(\w+)\s+Co\.",
    "X": r"X=\s*([\d.]+)",
    "Y": r"Y=\s*([\d.]+)",
    "Ground Elevation": r"Ground Elevation:\s*([\d.]+)"
}

def extract_images_from_pdf(pdf_path) -> list[Image.Image]:
    return convert_from_path(pdf_path)

def image_to_bytes(image, format="PNG"):
    with BytesIO() as buffer:
        image.save(buffer, format=format)
        return buffer.getvalue()
    
def process_text_detection(image: Image.Image) -> list[str]:
    session = boto3.Session()
    client = session.client('textract', region_name=os.environ.get("AWS_DEFUALT_REGION"))
    lines = []
    image_bytes = image_to_bytes(image)
    response = client.detect_document_text(Document={'Bytes': image_bytes})
    blocks=response['Blocks']   
    for block in blocks:
        if block['BlockType'] == "LINE":
            lines.append(block['Text'])
    return lines

def well_data(start: str, end: str, lines: list[str]) -> dict:
    start_index = 0
    end_index = 0
    for i, line in enumerate(lines):
        if start in line:
            start_index = i
        if end in line:
            end_index = i

    start_dict = {}
    start_dict[start] = {}
    for i, line in enumerate(lines[start_index:end_index]):
        for attribute, regex in attribute_regex_patterns.items():
            match = re.search(regex, line)
            if match:
                if "Well Name" in attribute:
                    # print(f"{attribute} - {match.group(1)}")
                    start_dict[start][attribute] = match.group(1)
                if "Abstract" in attribute:
                    # print(f"{attribute} - {match.group()}")
                    start_dict[start][attribute] = match.group()
                if "Block" in attribute:
                    # print(f"{attribute} - {match.group(1)}")
                    start_dict[start][attribute] = match.group(1)
                if "Section" in attribute:
                    # print(f"{attribute} - {match.group(1)}")
                    start_dict[start][attribute] = match.group(1)
                if "County" in attribute:
                    # print(f"{attribute} - {match.group(1)}")
                    start_dict[start][attribute] = match.group(1)
                if "Ground Elevation" in attribute:
                    # print(f"{attribute} - {match.group(1)}")  
                    start_dict[start][attribute] = match.group(1)  
                if "X" in attribute:
                    # print(f"{attribute} - {match.group(1)}")
                    start_dict[start][attribute] = match.group(1)
                if "Y" in attribute:
                    # print(f"{attribute} - {match.group(1)}")
                    start_dict[start][attribute] = match.group(1)

    return start_dict

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text")
    doc.close()
    return text

def extract_well_table_information(pdf_text) -> dict:
    # Set OpenAI API Key
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Prompt to OpenAI API
    prompt = f"""
        Context: This request involves extracting tabular data from a PDF document and formatting it into 
        structured JSON.

        Task: Locate and extract the table of data found on page 1, positioned directly below the text 
        within XML tags <pdf_text> and </pdf_text>. The table contains information about well elections and 
        requirements.

        Reference Text:
        "Indicate your election below and return a physical copy to the undersigned with the executed AFE. 
        Please include any well requirements with the returned election."

        Expected Output Format (JSON Structure):
        Convert the extracted table into structured JSON format with appropriate keys and values.

        Ensure data is properly aligned, preserving numeric values and text fields accurately.
        Use a list of objects, where each row in the table is represented as a JSON object.
        If any columns are merged or missing, make a best guess based on context, but do not fabricate data.

        Please provide the JSON output as plain text without any Markdown formatting or code fences.

        <pdf_text>
        {pdf_text}
        </pdf_text>
    """

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature=0.0
    )

    result = ""

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            result += chunk.choices[0].delta.content

    if len(result) > 0:
        return json.loads(result)
    else:   
        return None