from enum import Enum, unique

@unique
class Ingestor(Enum):
    PDF = "pdf"
    TEXT = "txt"
    DOCX = "docx"
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    YAML = "yaml"
    MARKDOWN = "markdown"
    IMG = "image"
    PNG = "png"
    JPG = "jpg"
    GIF = "gif"
    WEBRTC = "webrtc"
    MP3 = "mp3"
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    WAV = "wav"
    Unsupported = "unsupported"

    # Define alternate names using aliases
    def _generate_next_value_(name, start, count, last_values):
        aliases = {
            "TEXT": ("txt", "text"),
            "DOCX": ("docx", "doc"),
            "CSV": ("csv", "comma-separated-values", "comma-separated")
        }
        return aliases.get(name, name)
