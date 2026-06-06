from .repository import PriceRepository
from .config import price_source


_repository: PriceRepository | None = None


def get_price_repository() -> PriceRepository:
    """
    Return the configured price repository.

    For now this wraps the existing external market-data downloader. Keeping
    strategies behind this small interface lets us later swap in DynamoDB,
    Postgres/RDS, or S3 without rewriting strategy logic.
    """
    global _repository
    if _repository is None:
        source = price_source()
        if source == "dynamodb":
            from .dynamodb_repository import DynamoDBPriceRepository

            _repository = DynamoDBPriceRepository()
        else:
            from .external_provider import ExternalPriceRepository

            _repository = ExternalPriceRepository()
    return _repository


def set_price_repository(repository: PriceRepository | None) -> None:
    """
    Override the active price repository.

    This is mainly useful for tests and for future wiring where AWS Lambda can
    choose a DynamoDB-backed implementation while local development can keep
    using the external provider.
    """
    global _repository
    _repository = repository
