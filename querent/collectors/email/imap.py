import imaplib

from querent.config.collector.collector_config import EmailCollectorConfig


class ImapEmail:
    def imap_open(self, config: EmailCollectorConfig) -> imaplib.IMAP4_SSL:
        """
        Function to open an IMAP connection to the email server.

        Args:
            config (EmailCollectorConfig): The email collector config.
        Returns:
            imaplib.IMAP4_SSL: The IMAP connection.
        """
        conn = imaplib.IMAP4_SSL(
            config.imap_server,
            config.imap_port,
            config.imap_keyfile,
            config.imap_certfile,
        )
        conn.login(config.imap_username, config.imap_password)
        conn.select(config.imap_folder)
        return conn

    def adjust_imap_folder(self, imap_folder, email_sender) -> str:
        """
        Function to adjust the IMAP folder based on the email address of the sender.

        Args:
            imap_folder (str): The folder to open.
            email_sender (str): The email address of the sender.

        Returns:
            str: The adjusted IMAP folder.
        """
        if "@gmail" in email_sender.lower():
            if "sent" in imap_folder.lower():
                return '"[Gmail]/Sent Mail"'
            if "draft" in imap_folder.lower():
                return '"[Gmail]/Drafts"'
        return imap_folder
