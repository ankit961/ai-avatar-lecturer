"""
Translation module for converting text between languages.
Supports Hindi to English and English to Hindi translation using MarianMT models.
"""

import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

import torch
from transformers import MarianMTModel, MarianTokenizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Translator:
    """Text translator using MarianMT models."""
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize translator.
        
        Args:
            device: Device to run inference on ('cpu', 'cuda', or None for auto)
        """
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Initializing translator on device '{self.device}'")
        
        # Model configurations
        self.models = {}
        self.tokenizers = {}
        
        # Available translation pairs for Indian languages
        self.model_configs = {
            # Hindi
            "hi_to_en": "Helsinki-NLP/opus-mt-hi-en",
            "en_to_hi": "Helsinki-NLP/opus-mt-en-hi",
            
            # Note: Tamil and Telugu models don't exist in Helsinki-NLP
            # These languages will use the multilingual fallback models (en_to_indic, indic_to_en)
            
            # Marathi
            "mr_to_en": "Helsinki-NLP/opus-mt-mr-en",
            "en_to_mr": "Helsinki-NLP/opus-mt-en-mr",
            
            # Bengali
            "bn_to_en": "Helsinki-NLP/opus-mt-bn-en",
            "en_to_bn": "Helsinki-NLP/opus-mt-en-bn",
            
            # Note: Individual language models for gu, kn, ml, pa, ur don't exist
            # These languages will use the multilingual fallback models (en_to_indic, indic_to_en)
            
            # Urdu (has working models)
            "ur_to_en": "Helsinki-NLP/opus-mt-ur-en",
            "en_to_ur": "Helsinki-NLP/opus-mt-en-ur",
            
            # Multi-language to English (supports many Indian languages)
            "auto_to_en": "Helsinki-NLP/opus-mt-mul-en",
            
            # Indic languages multilingual model
            "indic_to_en": "Helsinki-NLP/opus-mt-inc-en",
            "en_to_indic": "Helsinki-NLP/opus-mt-en-inc"
        }
        
        # Language mapping for Whisper compatibility
        self.language_names = {
            "hi": "Hindi",
            "ta": "Tamil", 
            "te": "Telugu",
            "mr": "Marathi",
            "bn": "Bengali",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi",
            "ur": "Urdu",
            "en": "English",
            "auto": "Auto-detect"
        }
    
    def _load_model(self, model_key: str) -> None:
        """Load a specific translation model."""
        if model_key in self.models:
            return  # Already loaded
        
        model_name = self.model_configs[model_key]
        logger.info(f"Loading translation model: {model_name}")
        
        try:
            # Load tokenizer and model
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            
            # Move to device
            model = model.to(self.device)
            
            # Store
            self.tokenizers[model_key] = tokenizer
            self.models[model_key] = model
            
            logger.info(f"Successfully loaded {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    def translate_text(
        self, 
        text: str, 
        source_lang: str = "hi", 
        target_lang: str = "en",
        max_length: int = 512
    ) -> Dict[str, any]:
        """
        Translate text between languages.
        
        Args:
            text: Input text to translate
            source_lang: Source language code ('hi', 'en', 'auto')
            target_lang: Target language code ('hi', 'en')
            max_length: Maximum length for generated translation
            
        Returns:
            Dictionary containing translation results
        """
        if not text.strip():
            return {
                "source_text": text,
                "translated_text": "",
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        
        # Determine model key with fallback support
        if source_lang == "auto":
            model_key = "auto_to_en" if target_lang == "en" else "hi_to_en"
        else:
            model_key = f"{source_lang}_to_{target_lang}"
        
        # Try fallback for unsupported pairs
        if model_key not in self.model_configs:
            # For English to Indic languages, try the multilingual Indic model
            if source_lang == "en" and target_lang in ["ta", "te", "gu", "kn", "ml", "pa"]:
                model_key = "en_to_indic"
                logger.warning(f"Using fallback model en_to_indic for {source_lang}->{target_lang}")
            # For Indic to English, try the multilingual Indic model
            elif source_lang in ["ta", "te", "gu", "kn", "ml", "pa"] and target_lang == "en":
                model_key = "indic_to_en"
                logger.warning(f"Using fallback model indic_to_en for {source_lang}->{target_lang}")
            else:
                raise ValueError(f"Translation from {source_lang} to {target_lang} not supported. Available models: {list(self.model_configs.keys())}")
        
        # Load model if needed
        self._load_model(model_key)
        
        try:
            tokenizer = self.tokenizers[model_key]
            model = self.models[model_key]
            
            # Tokenize input
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                translated_tokens = model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=4,
                    do_sample=False,
                    early_stopping=True
                )
            
            # Decode translation
            translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
            
            result = {
                "source_text": text,
                "translated_text": translated_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "model_used": model_key
            }
            
            logger.info(f"Translation completed: {source_lang} -> {target_lang}")
            logger.debug(f"Original: {text[:100]}...")
            logger.debug(f"Translated: {translated_text[:100]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise
    
    def batch_translate(
        self, 
        texts: List[str], 
        source_lang: str = "hi", 
        target_lang: str = "en"
    ) -> List[Dict[str, any]]:
        """
        Translate multiple texts.
        
        Args:
            texts: List of input texts
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of translation results
        """
        results = []
        
        for text in texts:
            try:
                result = self.translate_text(text, source_lang, target_lang)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to translate text: {e}")
                results.append({
                    "source_text": text,
                    "translated_text": "",
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "error": str(e)
                })
        
        return results
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection based on character analysis.
        
        Args:
            text: Input text
            
        Returns:
            Detected language code ('hi' or 'en')
        """
        # Simple heuristic: check for Devanagari characters
        devanagari_chars = 0
        latin_chars = 0
        
        for char in text:
            if '\u0900' <= char <= '\u097F':  # Devanagari Unicode range
                devanagari_chars += 1
            elif char.isalpha() and ord(char) < 128:  # Basic Latin
                latin_chars += 1
        
        # Determine language based on character counts
        if devanagari_chars > latin_chars:
            return "hi"
        else:
            return "en"
    
    def auto_translate_to_english(self, text: str) -> Dict[str, any]:
        """
        Automatically detect language and translate to English if needed.
        
        Args:
            text: Input text
            
        Returns:
            Translation result
        """
        detected_lang = self.detect_language(text)
        
        if detected_lang == "en":
            # Already in English
            return {
                "source_text": text,
                "translated_text": text,
                "source_lang": "en",
                "target_lang": "en",
                "translation_needed": False
            }
        else:
            # Translate to English
            result = self.translate_text(text, source_lang=detected_lang, target_lang="en")
            result["translation_needed"] = True
            return result

    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return self.language_names.copy()
    
    def get_indian_languages(self) -> Dict[str, str]:
        """
        Get list of supported Indian languages.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        indian_langs = {k: v for k, v in self.language_names.items() 
                       if k not in ["en", "auto"]}
        return indian_langs
    
    def is_language_supported(self, lang_code: str, target_lang: str = "en") -> bool:
        """
        Check if a language pair is supported.
        
        Args:
            lang_code: Source language code
            target_lang: Target language code
            
        Returns:
            True if translation is supported
        """
        if lang_code == "auto":
            return target_lang == "en"
        
        model_key = f"{lang_code}_to_{target_lang}"
        return model_key in self.model_configs
    
    def smart_translate(self, text: str, target_lang: str = "en") -> Dict[str, any]:
        """
        Smart translation that tries multiple models for Indian languages.
        
        Args:
            text: Text to translate
            target_lang: Target language (default: English)
            
        Returns:
            Translation result with fallback strategy
        """
        # First try auto-detection with multilingual model
        try:
            result = self.translate_text(text, source_lang="auto", target_lang=target_lang)
            result["translation_method"] = "auto_multilingual"
            return result
        except Exception as e:
            logger.warning(f"Auto translation failed: {e}")
        
        # Fallback to Indic multilingual model
        try:
            self._load_model("indic_to_en")
            tokenizer = self.tokenizers["indic_to_en"]
            model = self.models["indic_to_en"]
            
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                translated_tokens = model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    do_sample=False,
                    early_stopping=True
                )
            
            translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
            
            result = {
                "source_text": text,
                "translated_text": translated_text,
                "source_lang": "indic",
                "target_lang": target_lang,
                "model_used": "indic_to_en",
                "translation_method": "indic_multilingual"
            }
            
            logger.info("Translation completed using Indic multilingual model")
            return result
            
        except Exception as e:
            logger.error(f"Indic translation also failed: {e}")
            
            # Ultimate fallback - return original text
            return {
                "source_text": text,
                "translated_text": text,
                "source_lang": "unknown",
                "target_lang": target_lang,
                "model_used": "none",
                "translation_method": "fallback_no_translation",
                "error": str(e)
            }


def translate_hindi_to_english(text: str, device: Optional[str] = None) -> str:
    """
    Convenience function to translate Hindi text to English.
    
    Args:
        text: Hindi text to translate
        device: Device to run on
        
    Returns:
        English translation
    """
    translator = Translator(device=device)
    result = translator.translate_text(text, source_lang="hi", target_lang="en")
    return result["translated_text"]


def translate_english_to_hindi(text: str, device: Optional[str] = None) -> str:
    """
    Convenience function to translate English text to Hindi.
    
    Args:
        text: English text to translate
        device: Device to run on
        
    Returns:
        Hindi translation
    """
    translator = Translator(device=device)
    result = translator.translate_text(text, source_lang="en", target_lang="hi")
    return result["translated_text"]


if __name__ == "__main__":
    # Test the translator
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python translate.py <text> [source_lang] [target_lang]")
        sys.exit(1)
    
    text = sys.argv[1]
    source_lang = sys.argv[2] if len(sys.argv) > 2 else "auto"
    target_lang = sys.argv[3] if len(sys.argv) > 3 else "en"
    
    try:
        translator = Translator()
        
        if source_lang == "auto":
            result = translator.auto_translate_to_english(text)
        else:
            result = translator.translate_text(text, source_lang, target_lang)
        
        print(f"Source ({result['source_lang']}): {result['source_text']}")
        print(f"Translation ({result['target_lang']}): {result['translated_text']}")
        
    except Exception as e:
        print(f"Error: {e}")
