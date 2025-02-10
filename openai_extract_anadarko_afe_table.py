import fitz
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

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
    )

    result = ""

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            result += chunk.choices[0].delta.content

    return json.loads(result)

def main(pdf_path:str):
    pdf_text = extract_text_from_pdf(pdf_path=pdf_path)
    # print(pdf_text)
    result = extract_well_table_information(pdf_text=pdf_text)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    load_dotenv()
    pdf_path = os.path.join("/home/ubuntu/afe/projects/moosehorn-3-mile/target_well_information", "MOOSEHORN_54_1_41_44-pages.pdf")
    main(pdf_path=pdf_path)






