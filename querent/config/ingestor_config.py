from enum import Enum
from typing import Optional


class IngestorBackend(str, Enum):
    PDF = "pdf"
    TEXT = "txt"
    DOCX = "docx"
    DOC = "doc"
    PPT = "ppt"
    PPTX = "pptx"
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
