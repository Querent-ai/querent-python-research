import fitz

from querent.logging.logger import setup_logger
class PDFConnector:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = None
        self.logger = setup_logger(__name__, "PDFConnector")

    def open_pdf(self):
        """Open the PDF file."""
        self.doc = fitz.open(self.file_path)

    def authenticate(self, password):
        """Authenticate the connection if the PDF is encrypted.
           PyMuPDF handles encryption directly upon opening the file,
           so we modify this method to match that behavior."""
        if self.doc.is_encrypted:
            try:
                # Attempt to authenticate with the provided password
                if not self.doc.authenticate(password):
                    self.logger.error("Incorrect password!")
                    return False
                return True
            except Exception as e:
                self.logger.error(f"Error during authentication: {e}")
                return False
        return True  # Document is not encrypted

    def read_data(self, page_num=0):
        """Read data from a specific page of the PDF."""
        if not self.doc:
            self.logger.error("PDF not opened!")
            return None

        if page_num < len(self.doc):
            page = self.doc.load_page(page_num)
            return page.get_text()
        else:
            self.l(f"Page number {page_num} is out of range!")
            return None

    def print_pdf_contents(self):
        """Print the entire contents of the PDF to the terminal."""
        if not self.doc:
            self.logger.error("PDF not opened!")
            return

        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            self.logger.info(page.get_text())

