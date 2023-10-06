class IngestedMessages:
    """
    A class to represent the ingested messages.
    """

    def __init__(self, messages):
        """
        Constructor for the IngestedMessages class.

        Parameters
        ----------
        messages : list
            A list of messages.
        """

        self.messages = messages

    def __str__(self):
        """
        Returns a string representation of the IngestedMessages object.

        Returns
        -------
        str
            A string representation of the IngestedMessages object.
        """

        return str(self.messages)

    def __repr__(self):
        """
        Returns a string representation of the IngestedMessages object.

        Returns
        -------
        str
            A string representation of the IngestedMessages object.
        """

        return str(self.messages)
