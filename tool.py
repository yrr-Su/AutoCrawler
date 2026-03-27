
from typing import Any, TypeVar, cast

from bs4.element import Tag

T = TypeVar('T', Tag, list[Tag])

def ensure_element_found(
        element: Any,
        describe: str,
        msg: str,
        ) -> T:
    """確保元素被找到，如果元素是 None, 則引發 ValueError。

    :param element_value: 查找操作的結果。
    :param element_description: 正在查找的元素的描述 (例如 "span with class 'foo'")。
    :param context_message: 操作的上下文 (例如 "in pre_parse AVG")。
    :return: 元素 (保證不是 None)。
    :raises ValueError: 如果元素是 None or of the wrong type/structure.
    """

    if isinstance(element, list):
        if isinstance(element[0], Tag):
            return cast(T, element)

    else:
        if isinstance(element, Tag):
            return cast(T, element)

    raise ValueError(
        f"In {msg}: "
        f"Required element '{describe}'"
        " not found or is of incorrect type/structure."
        f"Expected list[Tag] ot Tag, but got {type(element)}."
        )
