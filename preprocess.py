"""Text cleaning shared by train_model.py and app.py.

Keeping ONE copy matters: if training and serving clean text differently
(e.g. "don't" -> "dont" vs "don t"), the model sees words it never learned.
"""
import re

# Source "fingerprints" that let a model cheat. In the ISOT dataset almost every
# real article starts with "CITY (Reuters) -" and many fake ones carry tags like
# "21st Century Wire". A model that learns these scores ~99% on the test split
# but has learned the publisher, not the truth.
_DATELINE = re.compile(r"^[^()]{0,80}\(\s*reuters\s*\)\s*[-\u2013\u2014]*\s*", re.I)
_ARTIFACTS = re.compile(
    r"\(\s*reuters\s*\)|\breuters\b|21st century wire|featured image|"
    r"getty images|image via|photo by|video via|pic\.twitter\.com\S*",
    re.I,
)
_URL = re.compile(r"http\S+|www\S+", re.I)
_TIME_WORDS = re.compile(
    r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
    r"january|february|march|april|june|july|august|september|october|"
    r"november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\b"
)
# Publisher / platform names and web boilerplate: they identify the SOURCE, not the truth
_SOURCE_WORDS = re.compile(
    r"\b(?:breitbart|twitter|flickr|youtube|facebook|instagram|reddit|infowars|"
    r"buzzfeed|politico|cnn|bbc|npr|afp|ap|rt|"
    r"new\s+york\s+times?|washington\s+post|daily\s+wire|daily\s+caller|"
    r"pic|com|getty|imgur|"
    r"video|watch|read|follow|share|breaking)\b"
)
def strip_source_artifacts(text: str) -> str:
    text = str(text)
    text = _DATELINE.sub("", text, count=1)
    return _ARTIFACTS.sub(" ", text)


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = _URL.sub(" ", text)
    text = text.replace("'", " ").replace("\u2019", " ")
    text = re.sub(r"[^a-z\s]", " ", text)
    text = _TIME_WORDS.sub(" ", text)
    text = _SOURCE_WORDS.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def prepare_text(text: str) -> str:
    """Full pipeline used everywhere: strip source tags, then clean."""
    return clean_text(strip_source_artifacts(text))
