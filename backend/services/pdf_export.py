import io
import logging

try:
    from weasyprint import HTML, CSS   # WeasyPrint is a heavy dependency (requires system-level libraries like Cairo, Pango). If it's not installed, the app shouldn't crash — it should just disable PDF generation gracefully. The flag WEASYPRINT_INSTALLED is checked at runtime instead of at import time.
    WEASYPRINT_INSTALLED = True
except ImportError:
    WEASYPRINT_INSTALLED = False

logger = logging.getLogger('ats_resume_scorer')

def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
    if not WEASYPRINT_INSTALLED:
        raise ImportError("WeasyPrint is not installed. PDF generation unavailable.")
        
    documents = []
    
    # Render all 3 HTML strings to WeasyPrint Document objects
    for name, html_str in html_docs.items():
        doc = HTML(string=html_str).render()  # HTML(string=html_str) — WeasyPrint accepts raw HTML strings directly (no file needed). .render() converts it into a WeasyPrint Document object containing a list of pages. name is never used here — the loop only needs the HTML string values, not the keys.
        documents.append(doc)
    
    # Merge them into the first document
    first_doc = documents[0]
    for other_doc in documents[1:]:  # WeasyPrint has no built-in "merge PDFs" method so this is a manual page-level merge. Takes every page from documents 2, 3, 4 and appends them into document 1's page list. documents[1:] slices from index 1 to end — skips the first doc since that's the target.
        for page in other_doc.pages:
            first_doc.pages.append(page)
            
    # Write combined PDF bytes
    pdf_bytes = first_doc.write_pdf()  # write_pdf() serializes the merged document into raw bytes. Returning bytes instead of writing to a file keeps it flexible — the caller can save it to disk, stream it as an HTTP response, or attach it to an email.
    return pdf_bytes