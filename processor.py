from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from prompts import text_analyze_prompt_ru, text_analyze_prompt_en
from langchain_core.exceptions import OutputParserException
from config import model_name, ollama_host, temperature_value, attempts_number, language
from database import get_all_tags, add_file_to_db
from extractor import extract_text
import os

text_analyze_prompt = text_analyze_prompt_en if language == "en" else text_analyze_prompt_ru

class FileMeta(BaseModel):
    title: str
    summary: str
    tags: List[str]


def analyze_text(text):
    parser = JsonOutputParser(pydantic_object=FileMeta)

    llm = ChatOllama(
        model=model_name, temperature=temperature_value, base_url=ollama_host
    )
    chain = text_analyze_prompt | llm | parser

    # Attempt analysis multiple times if parsing fails
    for i in range(attempts_number):
        try:
            return chain.invoke({"text": text, "all_tags": get_all_tags})
        except OutputParserException:
            continue

    # Return None if all attempts fail
    return None


def process_file(path):
    try:
        # Extract text from file
        extracted_text = extract_text(path)
        # Analyze extracted text
        file_meta = analyze_text(extracted_text)
        print(f"\n{file_meta}\n")
        # Check if language model returned a valid response
        if file_meta is None:
            raise RuntimeError(
                "It was not possible to get a correct response from language model after several attempts"
            )
        # Add file metadata to database
        file_meta["path"] = path
        file_meta["file_type"] = path.split("/")[-1].split(".")[-1]
        add_file_to_db(file_meta)
        print(f"File metadata for {path} has been successfully added to database.")
    except Exception as e:
        print(f"An error occurred while processing file {path}: {e}")


def process_url(url):
    try:
        # Extract text from URL
        extracted_text = extract_text(url)
        # Analyze extracted text
        file_meta = analyze_text(extracted_text)
        print(f"\n{file_meta}\n")
        # Check if llm return valid response
        if file_meta is None:
            raise RuntimeError(
                "It was not possible to get a correct response from language model after several attempts"
            )
        # Add URL metadata to database
        file_meta["path"] = url
        file_meta["file_type"] = "website"
        add_file_to_db(file_meta)
        print(f"URL metadata for {url} has been successfully added to database.")
    except Exception as e:
        print(f"An error occurred while processing URL {url}: {e}")


def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            process_file(file_path)
