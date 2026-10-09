from pathlib import Path
from typing import List, Any
import io
import os

import fitz
import requests
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from pypdf import PdfReader, PdfWriter


OCR_ENDPOINT = "https://api.ocr.space/parse/image"
OCR_PAGES_PER_CHUNK = 2
OCR_COMPRESSED_DPI = 160
OCR_JPEG_QUALITY = 75


class OCRRequestError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _load_environment() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _ocr_request(
    file_name: str,
    file_content: bytes,
    api_key: str,
    engine: str,
    language: str,
) -> str:
    try:
        response = requests.post(
            OCR_ENDPOINT,
            files={"file": (file_name, io.BytesIO(file_content))},
            data={
                "apikey": api_key,
                "language": language,
                "OCREngine": engine,
                "isOverlayRequired": "false",
                "detectOrientation": "true",
                "scale": "true",
            },
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        raise OCRRequestError(
            f"OCR.Space request failed: {exc}",
            status_code=exc.response.status_code if exc.response is not None else None,
        ) from exc
    except requests.RequestException as exc:
        raise OCRRequestError(f"OCR.Space request failed: {exc}") from exc
    except ValueError as exc:
        raise OCRRequestError(
            f"OCR.Space returned a non-JSON response: {response.text[:1000]}"
        ) from exc

    if payload.get("IsErroredOnProcessing"):
        messages = payload.get("ErrorMessage") or payload.get("ErrorDetails")
        raise OCRRequestError(f"OCR.Space processing failed: {messages}")

    return "\n\n".join(
        result.get("ParsedText", "").strip()
        for result in payload.get("ParsedResults") or []
        if result.get("ParsedText")
    ).strip()


def _compress_pdf_chunk(file_content: bytes) -> bytes:
    source = fitz.open(stream=file_content, filetype="pdf")
    compressed = fitz.open()
    scale = OCR_COMPRESSED_DPI / 72
    try:
        for page in source:
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(scale, scale),
                colorspace=fitz.csGRAY,
                alpha=False,
            )
            image = pixmap.tobytes("jpeg", jpg_quality=OCR_JPEG_QUALITY)
            output_page = compressed.new_page(
                width=pixmap.width,
                height=pixmap.height,
            )
            output_page.insert_image(output_page.rect, stream=image)
        return compressed.tobytes(garbage=4, deflate=True, clean=True)
    finally:
        source.close()
        compressed.close()


def _pdf_chunks(file_path: Path) -> list[tuple[str, bytes]]:
    reader = PdfReader(str(file_path))
    chunks = []
    for start in range(0, len(reader.pages), OCR_PAGES_PER_CHUNK):
        writer = PdfWriter()
        for page in reader.pages[start:start + OCR_PAGES_PER_CHUNK]:
            writer.add_page(page)
        buffer = io.BytesIO()
        writer.write(buffer)
        end = min(start + OCR_PAGES_PER_CHUNK, len(reader.pages))
        chunks.append(
            (f"{file_path.stem}-pages-{start + 1}-{end}.pdf", buffer.getvalue())
        )
    return chunks


def _load_scanned_pdf_with_ocr(file_path: Path, progress_callback=None) -> List[Any]:
    _load_environment()
    api_key = os.getenv("OCR_API_KEY") or os.getenv("OCR_SPACE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Scanned PDF detected, but OCR_API_KEY is not configured."
        )

    engine = os.getenv("OCR_ENGINE", "2")
    language = os.getenv("OCR_LANGUAGE", "eng")
    documents = []
    chunks = _pdf_chunks(file_path)
    print(
        f"[INFO] No selectable text found in {file_path.name}; "
        f"processing {len(chunks)} OCR chunks."
    )

    for index, (file_name, file_content) in enumerate(chunks, start=1):
        if progress_callback:
            progress_callback(
                30 + int((index - 1) / len(chunks) * 40),
                f"Scanned PDF detected. Extracting text from chunk {index}/{len(chunks)}...",
            )
        print(
            f"[INFO] OCR chunk {index}/{len(chunks)}: "
            f"{len(file_content) / 1024 / 1024:.2f} MB"
        )
        try:
            text = _ocr_request(file_name, file_content, api_key, engine, language)
        except OCRRequestError as exc:
            if exc.status_code != 413:
                raise
            compressed_content = _compress_pdf_chunk(file_content)
            print(
                f"[INFO] OCR chunk too large; retrying compressed chunk at "
                f"{len(compressed_content) / 1024 / 1024:.2f} MB."
            )
            text = _ocr_request(
                file_name,
                compressed_content,
                api_key,
                engine,
                language,
            )

        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": str(file_path), "ocr": True, "chunk": index},
                )
            )

    if not documents:
        raise RuntimeError(f"OCR completed without extracting text from {file_path}.")
    return documents

def load_document(file_path: str, progress_callback=None) -> List[Any]:
    """
    Load a single file and convert to LangChain document structure.
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    try:
        if ext == '.pdf':
            loader = PyPDFLoader(str(path))
            documents = loader.load()
            if any(document.page_content.strip() for document in documents):
                return documents
            return _load_scanned_pdf_with_ocr(path, progress_callback)
        elif ext == '.txt':
            loader = TextLoader(str(path))
        elif ext == '.csv':
            loader = CSVLoader(str(path))
        elif ext == '.xlsx':
            loader = UnstructuredExcelLoader(str(path))
        elif ext == '.docx':
            loader = Docx2txtLoader(str(path))
        elif ext == '.json':
            loader = JSONLoader(str(path))
        else:
            print(f"[ERROR] Unsupported file extension: {ext}")
            return []
        return loader.load()
    except Exception as e:
        print(f"[ERROR] Failed to load file {file_path}: {e}")
        return []

def load_all_documents(data_dir: str) -> List[Any]:
    """
    Load all supported files from the data directory and convert to LangChain document structure.
    Supported: PDF, TXT, CSV, Excel, Word, JSON
    """
    # Use project root data folder
    data_path = Path(data_dir).resolve()
    print(f"[DEBUG] Data path: {data_path}")
    documents = []

    # PDF files
    pdf_files = list(data_path.glob('**/*.pdf'))
    print(f"[DEBUG] Found {len(pdf_files)} PDF files: {[str(f) for f in pdf_files]}")
    for pdf_file in pdf_files:
        print(f"[DEBUG] Loading PDF: {pdf_file}")
        try:
            loaded = load_document(str(pdf_file))
            print(f"[DEBUG] Loaded {len(loaded)} PDF docs from {pdf_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {pdf_file}: {e}")

    # TXT files
    txt_files = list(data_path.glob('**/*.txt'))
    print(f"[DEBUG] Found {len(txt_files)} TXT files: {[str(f) for f in txt_files]}")
    for txt_file in txt_files:
        print(f"[DEBUG] Loading TXT: {txt_file}")
        try:
            loader = TextLoader(str(txt_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} TXT docs from {txt_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load TXT {txt_file}: {e}")

    # CSV files
    csv_files = list(data_path.glob('**/*.csv'))
    print(f"[DEBUG] Found {len(csv_files)} CSV files: {[str(f) for f in csv_files]}")
    for csv_file in csv_files:
        print(f"[DEBUG] Loading CSV: {csv_file}")
        try:
            loader = CSVLoader(str(csv_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} CSV docs from {csv_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load CSV {csv_file}: {e}")

    # Excel files
    xlsx_files = list(data_path.glob('**/*.xlsx'))
    print(f"[DEBUG] Found {len(xlsx_files)} Excel files: {[str(f) for f in xlsx_files]}")
    for xlsx_file in xlsx_files:
        print(f"[DEBUG] Loading Excel: {xlsx_file}")
        try:
            loader = UnstructuredExcelLoader(str(xlsx_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} Excel docs from {xlsx_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load Excel {xlsx_file}: {e}")

    # Word files
    docx_files = list(data_path.glob('**/*.docx'))
    print(f"[DEBUG] Found {len(docx_files)} Word files: {[str(f) for f in docx_files]}")
    for docx_file in docx_files:
        print(f"[DEBUG] Loading Word: {docx_file}")
        try:
            loader = Docx2txtLoader(str(docx_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} Word docs from {docx_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load Word {docx_file}: {e}")

    # JSON files
    json_files = list(data_path.glob('**/*.json'))
    print(f"[DEBUG] Found {len(json_files)} JSON files: {[str(f) for f in json_files]}")
    for json_file in json_files:
        print(f"[DEBUG] Loading JSON: {json_file}")
        try:
            loader = JSONLoader(str(json_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} JSON docs from {json_file}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load JSON {json_file}: {e}")

    print(f"[DEBUG] Total loaded documents: {len(documents)}")
    return documents

# Example usage
if __name__ == "__main__":
    docs = load_all_documents("data")
    print(f"Loaded {len(docs)} documents.")
    print("Example document:", docs[0] if docs else None)