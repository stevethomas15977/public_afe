import fitz
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import boto3

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    # for page in doc:
    #     text += page.get_text("text")
    text = doc[0].get_text("text")
    doc.close()
    return text

def extract_well_table_information(pdf_text) -> dict:
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

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

    payload = {
        "inputText": prompt,
        "textGenerationConfig": {
            "temperature": 0,
            "topP": 1,
            "maxTokenCount": 2000
        }
    }

    # Invoke AWS Bedrock Titan Model
    response = bedrock.invoke_model(
        modelId="amazon.titan-text-express-v1",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload),
    )

    # Parse the response
    response_body = json.loads(response["body"].read())
    result = response_body.get("results")[0]["outputText"]
    print(result)
    return result

def main(pdf_path:str):
    pdf_text = extract_text_from_pdf(pdf_path=pdf_path)
    # print(pdf_text)
    result = extract_well_table_information(pdf_text=pdf_text)
    # print(json.dumps(result, indent=4))

if __name__ == "__main__":
    load_dotenv()
    pdf_path = os.path.join("/home/ubuntu/afe/projects/moosehorn-3-mile/target_well_information", "MOOSEHORN_54_1_41_44-pages.pdf")
    main(pdf_path=pdf_path)






