import boto3
import os
from pdf2image import convert_from_path
from PIL import Image
from io import BytesIO
import re

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

def main():
    pdf_path = "MOOSEHORN_54_1_41_44-pages.pdf"
    images = extract_images_from_pdf(pdf_path=pdf_path)
    for image in images:
        section_data = {}
        lines=process_text_detection(image=image)
        if "NEW DRILL" in lines:
            surface_location = well_data("SURFACE LOCATION", "PENETRATION POINT", lines)
            bottom_hole = well_data("LAST TAKE POINT", "END OF TERMINUS", lines)

            print(surface_location)
            print(bottom_hole)
if __name__ == "__main__":
    main()

