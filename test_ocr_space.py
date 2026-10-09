"""Smoke test for the OCR.Space API.

Usage:
    python test_ocr_space.py path\\to\\scanned.pdf
    python test_ocr_space.py path\\to\\scanned.pdf --engine 2 --output ocr-result.txt
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
    import fitz
    from pypdf import PdfReader, PdfWriter
except ImportError as exc:
    print(
        "Missing dependency. Install it with: "
        "pip install requests python-dotenv pypdf pymupdf",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


OCR_ENDPOINT = "https://api.ocr.space/parse/image"
PDF_PAGES_PER_REQUEST = 2
COMPRESSED_DPI = 160
JPEG_QUALITY = 75


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test OCR.Space with one document.")
    parser.add_argument("document", type=Path, help="Path to a PDF or image file")
    parser.add_argument(
        "--engine",
        type=int,
        choices=(1, 2, 3),
        default=2,
        help="OCR.Space engine to use (default: 2)",
    )
    parser.add_argument(
        "--language",
        default="eng",
        help="OCR language code (default: eng)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for saving extracted text",
    )
    parser.add_argument(
        "--max-chunks",
        type=int,
        help="Only upload the first N PDF chunks for testing",
    )
    return parser.parse_args()


class OCRRequestError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def ocr_request(
    file_name: str,
    file_content: bytes,
    api_key: str,
    engine: int,
    language: str,
) -> str:
    try:
        response = requests.post(
            OCR_ENDPOINT,
            files={"file": (file_name, io.BytesIO(file_content))},
            data={
                "apikey": api_key,
                "language": language,
                "OCREngine": str(engine),
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
            f"Request failed: {exc}",
            status_code=exc.response.status_code if exc.response is not None else None,
        ) from exc
    except requests.RequestException as exc:
        raise OCRRequestError(f"Request failed: {exc}") from exc
    except ValueError:
        raise RuntimeError(
            "OCR.Space returned a non-JSON response: "
            f"{response.text[:1000]}"
        ) from None

    if payload.get("IsErroredOnProcessing"):
        messages = payload.get("ErrorMessage") or payload.get("ErrorDetails")
        raise RuntimeError(f"OCR.Space processing failed: {messages}")

    parsed_results = payload.get("ParsedResults") or []
    return "\n\n".join(
        result.get("ParsedText", "").strip()
        for result in parsed_results
        if result.get("ParsedText")
    ).strip()


def compress_pdf_chunk(file_content: bytes) -> bytes:
    """Render a PDF chunk as grayscale JPEG pages inside a smaller PDF."""
    source = fitz.open(stream=file_content, filetype="pdf")
    compressed = fitz.open()
    scale = COMPRESSED_DPI / 72
    try:
        for page in source:
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(scale, scale),
                colorspace=fitz.csGRAY,
                alpha=False,
            )
            image = pixmap.tobytes("jpeg", jpg_quality=JPEG_QUALITY)
            output_page = compressed.new_page(
                width=pixmap.width,
                height=pixmap.height,
            )
            output_page.insert_image(output_page.rect, stream=image)
        return compressed.tobytes(garbage=4, deflate=True, clean=True)
    finally:
        source.close()
        compressed.close()


def pdf_chunks(document: Path) -> list[tuple[str, bytes]]:
    reader = PdfReader(str(document))
    chunks = []
    for start in range(0, len(reader.pages), PDF_PAGES_PER_REQUEST):
        writer = PdfWriter()
        for page in reader.pages[start:start + PDF_PAGES_PER_REQUEST]:
            writer.add_page(page)
        buffer = io.BytesIO()
        writer.write(buffer)
        end = min(start + PDF_PAGES_PER_REQUEST, len(reader.pages))
        chunks.append((f"{document.stem}-pages-{start + 1}-{end}.pdf", buffer.getvalue()))
    return chunks


def main() -> int:
    args = parse_args()
    document = args.document.expanduser().resolve()

    if not document.is_file():
        print(f"Document not found: {document}", file=sys.stderr)
        return 1

    load_dotenv(Path(__file__).with_name(".env"))
    api_key = os.getenv("OCR_API_KEY") or os.getenv("OCR_SPACE_API_KEY")
    if not api_key:
        print(
            "OCR API key not found. Add OCR_API_KEY to the project .env file.",
            file=sys.stderr,
        )
        return 1

    if document.suffix.lower() == ".pdf":
        try:
            chunks = pdf_chunks(document)
        except Exception as exc:
            print(f"Could not split PDF into page chunks: {exc}", file=sys.stderr)
            return 1
        print(
            f"PDF has {len(PdfReader(str(document)).pages)} pages. "
            f"Sending up to {PDF_PAGES_PER_REQUEST} pages per OCR request."
        )
    else:
        chunks = [(document.name, document.read_bytes())]

    if args.max_chunks is not None:
        if args.max_chunks < 1:
            print("--max-chunks must be at least 1.", file=sys.stderr)
            return 1
        chunks = chunks[:args.max_chunks]
        print(f"Testing only the first {len(chunks)} chunk(s).")

    extracted_parts = []
    for index, (file_name, file_content) in enumerate(chunks, start=1):
        print(
            f"Uploading chunk {index}/{len(chunks)}: {file_name} "
            f"({len(file_content) / 1024 / 1024:.2f} MB)..."
        )
        try:
            text = ocr_request(
                file_name,
                file_content,
                api_key,
                args.engine,
                args.language,
            )
        except OCRRequestError as exc:
            if document.suffix.lower() == ".pdf" and exc.status_code == 413:
                print(
                    f"Chunk is too large. Retrying with {COMPRESSED_DPI} DPI "
                    f"grayscale JPEG compression..."
                )
                try:
                    compressed_content = compress_pdf_chunk(file_content)
                    print(
                        f"Compressed chunk size: "
                        f"{len(compressed_content) / 1024 / 1024:.2f} MB"
                    )
                    text = ocr_request(
                        file_name,
                        compressed_content,
                        api_key,
                        args.engine,
                        args.language,
                    )
                except (OCRRequestError, RuntimeError) as compressed_exc:
                    print(
                        f"OCR failed for compressed {file_name}: "
                        f"{compressed_exc}",
                        file=sys.stderr,
                    )
                    return 1
            else:
                print(f"OCR failed for {file_name}: {exc}", file=sys.stderr)
                return 1
        except RuntimeError as exc:
            print(f"OCR failed for {file_name}: {exc}", file=sys.stderr)
            return 1
        if text:
            extracted_parts.append(text)

    extracted_text = "\n\n".join(extracted_parts).strip()
    if not extracted_text:
        print("OCR completed, but no text was extracted.", file=sys.stderr)
        return 1

    print(f"OCR succeeded. Extracted {len(extracted_text)} characters.")
    if args.output:
        output = args.output.expanduser().resolve()
        output.write_text(extracted_text + "\n", encoding="utf-8")
        print(f"Saved extracted text to {output}")
    else:
        print("\nExtracted text:\n")
        print(extracted_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
