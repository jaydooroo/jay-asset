from .repository import PriceRepository


_repository: PriceRepository | None = None


def get_price_repository() -> PriceRepository:
    """
    Return the price repository used by strategies.

    Strategies always read stored daily closes from DynamoDB. The daily ingest
    job (market/ingest.py) fills that table from Tiingo, so user requests never
    call a market-data API directly.
    """
    global _repository
    if _repository is None:
        from .dynamodb_repository import DynamoDBPriceRepository

        _repository = DynamoDBPriceRepository()
    return _repository


def set_price_repository(repository: PriceRepository | None) -> None:
    """Override the active price repository (mainly for tests)."""
    global _repository
    _repository = repository
