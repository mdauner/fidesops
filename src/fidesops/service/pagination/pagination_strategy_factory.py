import logging
from enum import Enum
from typing import List, Dict, Any
from fidesops.service.pagination.pagination_strategy import PaginationStrategy
from fidesops.service.pagination.pagination_strategy_cursor import (
    CursorPaginationStrategy,
)
from fidesops.service.pagination.pagination_strategy_link import LinkPaginationStrategy
from fidesops.service.pagination.pagination_strategy_offset import (
    OffsetPaginationStrategy,
)

from pydantic import ValidationError

from fidesops.common_exceptions import (
    NoSuchStrategyException,
    ValidationError as FidesopsValidationError,
)
from fidesops.schemas.saas.strategy_configuration import StrategyConfiguration

logger = logging.getLogger(__name__)


class SupportedPaginationStrategies(Enum):
    """
    The supported methods by which Fidesops can post-process Saas connector data.
    """

    offset = OffsetPaginationStrategy
    link = LinkPaginationStrategy
    cursor = CursorPaginationStrategy


def get_strategy(
    strategy_name: str,
    configuration: Dict[str, Any],
) -> PaginationStrategy:
    """
    Returns the strategy given the name and configuration.
    Raises NoSuchStrategyException if the strategy does not exist
    """
    if strategy_name not in SupportedPaginationStrategies.__members__:
        valid_strategies = ", ".join([s.name for s in SupportedPaginationStrategies])
        raise NoSuchStrategyException(
            f"Strategy '{strategy_name}' does not exist. Valid strategies are [{valid_strategies}]"
        )
    strategy = SupportedPaginationStrategies[strategy_name].value
    try:
        strategy_config: StrategyConfiguration = strategy.get_configuration_model()(
            **configuration
        )
        return strategy(configuration=strategy_config)
    except ValidationError as e:
        raise FidesopsValidationError(message=str(e))


def get_strategies() -> List[PaginationStrategy]:
    """Returns all supported pagination strategies"""
    return [e.value for e in SupportedPaginationStrategies]
