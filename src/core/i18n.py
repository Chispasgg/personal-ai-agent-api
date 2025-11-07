"""
Internationalization support for multiple languages.
Simple language detection and template selection.
"""
# from typing import  Optional
# from langdetect import detect, LangDetectException
from googletrans import Translator
from config.settings import settings


async def get_language_data(text: str) -> str:
    """
    Detect language from text using langdetect.
    Falls back to default language if detection fails.

    Args:
        text: Input text to analyze

    Returns:
        Detected language code
    """
    result_data = {
            'texto_original': text,
            'idioma_detectado': settings.default_language,
            'texto_traducido': text,
            'confianza': 0
        }
    if not text or len(text.strip()) < 3:
        return result_data  # type: ignore

    try:
        # Crear instancia del traductor
        traductor = Translator()

        # Detectar el idioma
        deteccion = await traductor.detect(text)
        idioma_detectado = deteccion.lang
        confianza = deteccion.confidence

        # Validate against supported languages
        if idioma_detectado in settings.supported_languages_list:
            # Traducir al inglés
            traduccion = await traductor.translate(text, dest='en', src=idioma_detectado)
            result_data = {
                'texto_original': text,
                'idioma_detectado': idioma_detectado,
                'texto_traducido': traduccion.text,
                'confianza': confianza
                }

            return result_data  # type: ignore

        return result_data  # type: ignore

    except Exception as e:
        print(f"Language detection failed: {e}")
        return result_data  # type: ignore

# old version
# def detect_language(text: str) -> str:
#     """
#     Detect language from text using langdetect.
#     Falls back to default language if detection fails.
#
#     Args:
#         text: Input text to analyze
#
#     Returns:
#         Detected language code
#     """
#     if not text or len(text.strip()) < 3:
#         return settings.default_language  # type: ignore
#
#     try:
#         result = detect(text)
#
#         # Validate against supported languages
#         if result in settings.supported_languages_list:
#             return result  # type: ignore
#
#         return settings.default_language  # type: ignore
#
#     except LangDetectException as e:
#         print(f"Language detection failed: {e}")
#         return settings.default_language  # type: ignore
#
# old version
# def get_language(text: str, hint: Optional[str]=None) -> str:
#     """
#     Get language for text, considering optional hint.
#
#     Args:
#         text: Input text
#         hint: Optional language hint from previous interactions
#
#     Returns:
#         Language code to use
#     """
#     # If hint is provided and valid, use it
#     if hint and hint in settings.supported_languages_list:
#         return hint  # type: ignore
#
#     # Otherwise detect from text
#     return detect_language(text)


# def translate_to_english(text:str):
#     """
#     Traduce un texto al inglés detectando automáticamente el idioma de origen.

#     Args:
#         texto (str): El texto a traducir (debe tener más de 4 caracteres)

#     Returns:
#         dict: Diccionario con la información de la traducción:
#             - texto_original: El texto original
#             - idioma_detectado: El idioma detectado
#             - texto_traducido: El texto traducido al inglés
#             - confianza: Confianza de la detección del idioma

#     Raises:
#         ValueError: Si el texto tiene 4 caracteres o menos
#     """
#     # Validar que el texto tenga más de 4 caracteres
#     if len(text) <= 4:
#         raise ValueError("El texto debe tener más de 4 caracteres")

#     # Crear instancia del traductor
#     traductor = Translator()

#     # Detectar el idioma
#     deteccion = traductor.detect(text)
#     idioma_detectado = deteccion.lang
#     confianza = deteccion.confidence

#     # Si ya está en inglés, no traducir
#     if idioma_detectado == 'en':
#         return {
#             'texto_original': text,
#             'idioma_detectado': idioma_detectado,
#             'texto_traducido': text,
#             'confianza': confianza,
#             'mensaje': 'El texto ya está en inglés'
#         }

#     # Traducir al inglés
#     traduccion = traductor.translate(text, dest='en', src=idioma_detectado)

#     return {
#         'texto_original': text,
#         'idioma_detectado': idioma_detectado,
#         'texto_traducido': traduccion.text,
#         'confianza': confianza
#     }
