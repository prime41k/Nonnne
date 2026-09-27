"""
nonnne — убивает None раз и навсегда.

Пример:
    from nonnne import Maybe
    
    user = Maybe(get_user())
    name = user.profile.name.unwrap("Аноним")
"""

from typing import Any, Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class Maybe(Generic[T]):
    """
    Безопасная обёртка для значений, которые могут быть None.
    Вдохновлено Option из Rust и Maybe из Haskell.
    """

    __slots__ = ("_value",)

    def __init__(self, value: Optional[T]) -> None:
        self._value = value

    # --- Магия доступа ---

    def __getattr__(self, name: str) -> "Maybe":
        if self._value is None:
            return Maybe(None)
        try:
            return Maybe(getattr(self._value, name))
        except AttributeError:
            return Maybe(None)

    def __getitem__(self, key: Any) -> "Maybe":
        if self._value is None:
            return Maybe(None)
        try:
            return Maybe(self._value[key])
        except (KeyError, IndexError, TypeError):
            return Maybe(None)

    def __call__(self, *args: Any, **kwargs: Any) -> "Maybe":
        if self._value is None:
            return Maybe(None)
        try:
            return Maybe(self._value(*args, **kwargs))
        except Exception:
            return Maybe(None)

    # --- Сравнение и представление ---

    def __bool__(self) -> bool:
        return self._value is not None

    def __str__(self) -> str:
        return str(self._value) if self._value is not None else ""

    def __repr__(self) -> str:
        return f"Maybe({self._value!r})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Maybe):
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        return hash(self._value) if self._value is not None else hash(None)

    # --- Основные методы ---

    def unwrap(self, default: Any = None) -> Any:
        """Вернуть значение или дефолт."""
        return self._value if self._value is not None else default

    def unwrap_or_else(self, func: Callable[[], Any]) -> Any:
        """Вернуть значение или результат функции, если None."""
        return self._value if self._value is not None else func()

    def map(self, func: Callable[[T], Any]) -> "Maybe":
        """Применить функцию к значению, если оно есть."""
        if self._value is None:
            return Maybe(None)
        try:
            return Maybe(func(self._value))
        except Exception:
            return Maybe(None)

    def filter(self, predicate: Callable[[T], bool]) -> "Maybe":
        """Оставить значение, только если оно проходит проверку."""
        if self._value is None:
            return Maybe(None)
        try:
            return self if predicate(self._value) else Maybe(None)
        except Exception:
            return Maybe(None)

    def is_none(self) -> bool:
        return self._value is None

    def is_some(self) -> bool:
        return self._value is not None

    def to_list(self) -> list:
        """Some(x) -> [x], None -> []"""
        return [self._value] if self._value is not None else []


# --- Утилиты ---

def maybe(value: Any) -> Maybe:
    """Быстрая обёртка значения."""
    return Maybe(value)


def safe_call(func: Callable, *args: Any, **kwargs: Any) -> Maybe:
    """Вызвать функцию без риска падения."""
    try:
        return Maybe(func(*args, **kwargs))
    except Exception:
        return Maybe(None)


def first(iterable: Any, predicate: Optional[Callable] = None) -> Maybe:
    """Первый элемент, удовлетворяющий условию."""
    try:
        items = iter(iterable)
        if predicate:
            for item in items:
                if predicate(item):
                    return Maybe(item)
            return Maybe(None)
        return Maybe(next(items))
    except (StopIteration, TypeError):
        return Maybe(None)


def last(iterable: Any) -> Maybe:
    """Последний элемент коллекции."""
    try:
        if hasattr(iterable, "__len__") and hasattr(iterable, "__getitem__"):
            return Maybe(iterable[-1]) if len(iterable) > 0 else Maybe(None)
        
        last_item = None
        found = False
        for item in iterable:
            last_item = item
            found = True
        return Maybe(last_item) if found else Maybe(None)
    except (TypeError, IndexError, KeyError):
        return Maybe(None)


def get_path(data: Any, *keys: Any) -> Maybe:
    """Безопасный доступ по цепочке ключей: data['a']['b']['c']."""
    current = data
    for key in keys:
        if current is None:
            return Maybe(None)
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            return Maybe(None)
    return Maybe(current)


__all__ = ["Maybe", "maybe", "safe_call", "first", "last", "get_path"]
