from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0


def detect_language(text: str) -> str:
    cleaned_text = text.strip()

    if len(cleaned_text) < 20:
        return "unknown"

    try:
        return detect(cleaned_text)
    except Exception:
        return "unknown"


def unique_languages(languages: list[str]) -> list[str]:
    result = []

    for language in languages:
        if language not in result:
            result.append(language)

    return result