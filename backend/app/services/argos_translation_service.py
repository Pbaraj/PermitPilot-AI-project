from argostranslate import package, translate


LANGUAGE_NAME_TO_CODE = {
    "english": "en",
    "german": "de",
    "deutsch": "de",
    "french": "fr",
    "spanish": "es",
    "italian": "it",
    "portuguese": "pt",
    "hindi": "hi",
    "arabic": "ar",
    "turkish": "tr",
    "chinese": "zh",
}


def normalize_language_code(language: str) -> str:
    if not language:
        return "unknown"

    language = language.strip().lower()

    if len(language) == 2:
        return language

    return LANGUAGE_NAME_TO_CODE.get(language, language)


def install_translation_package_if_needed(from_code: str, to_code: str) -> bool:
    try:
        installed_languages = translate.get_installed_languages()

        from_language = next(
            (lang for lang in installed_languages if lang.code == from_code),
            None,
        )
        to_language = next(
            (lang for lang in installed_languages if lang.code == to_code),
            None,
        )

        if from_language and to_language:
            try:
                from_language.get_translation(to_language)
                return True
            except Exception:
                pass

        package.update_package_index()
        available_packages = package.get_available_packages()

        matching_package = next(
            (
                pkg for pkg in available_packages
                if pkg.from_code == from_code and pkg.to_code == to_code
            ),
            None,
        )

        if matching_package is None:
            return False

        downloaded_path = matching_package.download()
        package.install_from_path(downloaded_path)

        return True

    except Exception:
        return False


def translate_text_with_argos(
    text: str,
    source_language: str,
    target_language: str = "en",
) -> tuple[str, str]:
    if not text.strip():
        return text, "Empty text. Translation skipped."

    from_code = normalize_language_code(source_language)
    to_code = normalize_language_code(target_language)

    if from_code == to_code:
        return text, "Source and target language are the same. Translation skipped."

    if from_code == "unknown":
        return text, "Source language unknown. Original text was used."

    package_available = install_translation_package_if_needed(from_code, to_code)

    if not package_available:
        return (
            text,
            f"No Argos translation package available for {from_code} → {to_code}. Original text was used.",
        )

    try:
        installed_languages = translate.get_installed_languages()

        from_language = next(
            (lang for lang in installed_languages if lang.code == from_code),
            None,
        )
        to_language = next(
            (lang for lang in installed_languages if lang.code == to_code),
            None,
        )

        if not from_language or not to_language:
            return text, f"Translation language pair {from_code} → {to_code} not installed."

        translation = from_language.get_translation(to_language)
        translated_text = translation.translate(text)

        return translated_text, f"Translated using Argos Translate: {from_code} → {to_code}."

    except Exception as error:
        return text, f"Translation failed: {error}. Original text was used."