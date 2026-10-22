from ..i18n import translate_domain_text
from .base import ClassificationResult, Classifier
from .uscs import USCSClassifier
from .bs5930 import BS5930Classifier
from .rscs import RSCSClassifier
from .iso14688 import ISO14688Classifier
from .aashto import AASHTOClassifier

ALL_CLASSIFIERS = [
    USCSClassifier,
    BS5930Classifier,
    ISO14688Classifier,
    RSCSClassifier,
    AASHTOClassifier,
]


def _translate_result(result: ClassificationResult) -> ClassificationResult:
    result.name = translate_domain_text(result.name)
    result.notes = [translate_domain_text(n) for n in result.notes]
    result.extras = {translate_domain_text(k): v
                     for k, v in result.extras.items()}
    return result


SHORT_SYSTEM_NAMES = {
    "USCS (ASTM D2487)": "USCS",
    "British Standard (BS 5930)": "BS 5930",
    "TS EN ISO 14688": "TS EN ISO 14688",
    "RSCS (Park & Santamarina 2017)": "RSCS",
    "AASHTO (M 145)": "AASHTO",
}


def short_system_name(system: str) -> str:
    return SHORT_SYSTEM_NAMES.get(system, system.split(" ")[0])


def classify_selected(sample, classifier_classes):
    return [_translate_result(cls().classify(sample))
           for cls in classifier_classes]


def classify_all(sample):
    return classify_selected(sample, ALL_CLASSIFIERS)


__all__ = [
    "Classifier", "ClassificationResult",
    "USCSClassifier", "BS5930Classifier", "ISO14688Classifier",
    "RSCSClassifier", "AASHTOClassifier",
    "ALL_CLASSIFIERS", "classify_all", "classify_selected",
]
