from langchain_community.document_loaders import PyPDFLoader
import asyncio, os, time
from dotenv import load_dotenv
import fitz  # PyMuPDF
import boto3
import json
import pandas as pd

def main(pdf_path: str):
    table_json = extracxt_text_using_aws_textract("stevethomascpapublic", "MOOSEHORN_54_1_41_44-pages.pdf")
    print(table_json)

    # pdf_text = extract_text_from_pdf(pdf_path=pdf_path)
    # well_table_information = extract_well_table_information(pdf_text=pdf_text)
    # print(well_table_information)   
    # loader = PyPDFLoader(afe_pdf)
    # pages = []
    # async for page in loader.alazy_load():
    #     pages.append(page)

    # print(f"{pages[0].metadata}\n")
    # print(pages[0].page_content)

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = doc[0].get_text("text")  # Extract text from first page
    doc.close()
    return text

def extracxt_text_using_aws_textract(s3_bucket: str, pdf_file: str) -> str:
    # Initialize Textract client
    textract = boto3.client("textract", region_name="us-east-1")

    # Start Textract job
    response = textract.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": s3_bucket, "Name": pdf_file}},
        FeatureTypes=["TABLES"]
    )

    job_id = response["JobId"]
    print(f"Started Textract job with ID: {job_id}")

    # Wait for completion
    while True:
        status = textract.get_document_analysis(JobId=job_id)
        if status["JobStatus"] in ["SUCCEEDED", "FAILED"]:
            break
        time.sleep(5)

    if status["JobStatus"] == "FAILED":
        print("Textract analysis failed.")
        exit()

    # Extract table data
    blocks = status["Blocks"]
    table_data = []

    for block in blocks:
        if block["BlockType"] == "TABLE":
            print(block)
            rows = []
            for relationship in block.get("Relationships", []):
                if relationship["Type"] == "CHILD":
                    row_cells = []
                    for cell_id in relationship["Ids"]:
                        cell_block = next(b for b in blocks)
                        if cell_block and "Text" in cell_block:
                            row_cells.append(cell_block["Text"])
                        else:
                            row_cells.append("")  # Append empty string if no text
                    rows.append(row_cells)
            table_data.append(rows)

    # Convert to JSON
    table_json = json.dumps(table_data, indent=2)
    return table_json

def extract_well_table_information(pdf_text: str) -> str:
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    # Define the prompt for Titan LLM
    prompt = f"""
    Context: This request involves extracting tabular data from a PDF document and formatting it as a comma-separated values (CSV) file.

    Task: Locate and extract the table of data found on page 1, positioned directly below the text with in XML tags "<pdf_text>" and "</pdf_text>". The table contains information about well elections and requirements.

    "Indicate your election below and return a physical copy to the undersigned with the executed AFE. Please include any well requirements with the returned election."

    Expected Output Format:

    Convert the extracted table into structured CSV format with appropriate column headers.
    Ensure data is properly aligned, preserving numeric values and text fields accurately.
    The CSV should be readable in Excel or a database (avoid unnecessary line breaks).
    If any columns are merged or missing, make a best guess based on context, but do not fabricate data.

    <pdf_text>
    {pdf_text}
    </pdf_text>
    """

    # Define request payload for AWS Bedrock Titan LLM
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
    csv_content = response_body.get("results")[0]["outputText"]
    return csv_content

if __name__ == "__main__":
    load_dotenv()
    pdf_path = os.path.join("/home/ubuntu/afe/projects/moosehorn-3-mile/target_well_information", "MOOSEHORN_54_1_41_44-pages.pdf")
    main(pdf_path=pdf_path)