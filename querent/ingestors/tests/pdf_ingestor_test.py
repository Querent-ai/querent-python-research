import unittest
import PyPDF2
from querent.connectors import pdf_connector

import os


class TestPDFConnector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a sample PDF for testing
        cls.test_pdf_path = "querent/connectors/CAPSTONEComplete.pdf"
        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(
            PyPDF2.PageObject.create_blank_page(width=72, height=72))
        with open(cls.test_pdf_path, 'wb') as f:
            pdf_writer.write(f)

    def test_open_pdf(self):
        connector = pdf_connector.PDFConnector(self.test_pdf_path)
        connector.open_pdf()
        self.assertIsNotNone(connector.pdf_file)
        self.assertIsNotNone(connector.pdf_reader)

    def test_read_data(self):
        connector = pdf_connector.PDFConnector(self.test_pdf_path)
        connector.open_pdf()
        data = connector.read_data(0)
        self.assertEqual(data, "")  # Since our test PDF is blank

    def test_authenticate(self):
        connector = pdf_connector.PDFConnector(self.test_pdf_path)
        connector.open_pdf()
        # Our test PDF isn't encrypted, so this should return True
        self.assertTrue(connector.authenticate("any_password"))

    def test_print_pdf_contents(self):
        connector = pdf_connector.PDFConnector(self.test_pdf_path)
        connector.open_pdf()
        print("\nContents of the test PDF:")
        connector.print_pdf_contents()
