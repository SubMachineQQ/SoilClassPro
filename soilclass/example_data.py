from .i18n import t
from .models import SoilSample

EXAMPLE_SIEVE = [
    (75.0, 100.0),
    (19.0, 98.0),
    (9.5, 92.0),
    (4.75, 83.0),
    (2.00, 65.0),
    (0.850, 54.0),
    (0.425, 45.0),
    (0.250, 38.0),
    (0.106, 31.0),
    (0.075, 28.0),
    (0.020, 18.0),
    (0.005, 10.0),
    (0.001, 4.0),
]


def example_sample() -> SoilSample:
    return SoilSample(
        name="BH-1 / 3.5 m",
        sieve_data=list(EXAMPLE_SIEVE),
        liquid_limit=38.0,
        plastic_limit=19.0,
        organic=False,
        project=t("example_project"),
        location=t("example_location"),
        operator=t("example_operator"),
        date="2026-07-06",
    )
