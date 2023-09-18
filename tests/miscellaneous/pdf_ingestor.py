import pypdf


class PDFConnector:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pdf_file = None
        self.pdf_reader = None

    def open_pdf(self):
        """Open the PDF file."""
        self.pdf_file = open(self.file_path, 'rb')
        self.pdf_reader = pypdf.pdf_reader(self.pdf_file)

    def authenticate(self, password):
        """Authenticate the connection if the PDF is encrypted."""
        if self.pdf_reader.is_encrypted:
            try:
                self.pdf_reader.decrypt(password)
                return True
            except:
                print("Incorrect password!")
                return False
        return True

    def read_data(self, page_num=0):
        """Read data from a specific page of the PDF."""
        if not self.pdf_reader:
            print("PDF not opened!")
            return None
        print(len(self.pdf_reader.pages))
        if page_num < len(self.pdf_reader.pages):
            page = self.pdf_reader.pages[page_num]
            print("Page      ", page)
            return page.extract_text()
        else:
            print(f"Page number {page_num} is out of range!")
            return None

    def print_pdf_contents(self):
        """Print the entire contents of the PDF to the terminal."""
        if not self.pdf_reader:
            print("PDF not opened!")
            return
        for page_num in range(len(self.pdf_reader.pages)):
            page = self.pdf_reader.pages[page_num]
            print(page.extract_text())
