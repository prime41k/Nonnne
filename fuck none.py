# nonnne.py
""" 
nonnne - для тех кто ненавидит None

Usage:
    from nonnne import Maybe, maybe, safe_call
    
    user = Maybe(get_user())
    name = user.name.unwrap("Незнакомец")
"""

from typing import Any, Optional, TypeVar, Generic, Callable

T = TypeVar('T')


class Maybe(Generic[T]):
    """
    Безопасная обёртка для значений, которые могут быть None.
    Паттерн Option/Maybe из функциональных языков.
    """
    
    def __init__(self, value: Optional[T]):
        self._value = value
    
    def __getattr__(self, name: str) -> 'Maybe':
        """Безопасный доступ к атрибутам: user.name -> Maybe(name)"""
        if self._value is None:
            return Maybe(None)
        try:
            return Maybe(getattr(self._value, name))
        except AttributeError:
            return Maybe(None)
    
    def __getitem__(self, key: Any) -> 'Maybe':
        """Безопасная индексация: data['key'] -> Maybe(value)"""
        if self._value is None:
            return Maybe(None)
        try:
            return Maybe(self._value[key])
        except (KeyError, IndexError, TypeError):
            return Maybe(None)
    
    def __call__(self, *args: Any, **kwargs: Any) -> 'Maybe':
        """Безопасный вызов: func() -> Maybe(result)"""
        if self._value is None:
            return Maybe(None)
        try:
            return Maybe(self._value(*args, **kwargs))
        except (TypeError, ValueError, RuntimeError):
            return Maybe(None)
    
    def __bool__(self) -> bool:
        """Позволяет if maybe: """
        return self._value is not None
    
    def __str__(self) -> str:
        return str(self._value) if self._value is not None else ""
    
    def __repr__(self) -> str:
        return f"Maybe({repr(self._value)})"
    
    def __eq__(self, other: Any) -> bool:
        """
        Строгое сравнение только с Maybe.
        
        >>> Maybe(5) == Maybe(5)
        True
        >>> Maybe(5) == 5
        False
        """
        if isinstance(other, Maybe):
            return self._value == other._value
        return False
    
    def __hash__(self) -> int:
        """Хеш для использования в словарях и множествах"""
        return hash(self._value) if self._value is not None else hash(None)
    
    # === Основные методы ===
    
    def unwrap(self, default: Any = None) -> Any:
        """
        Получить значение или default, если None.
        
        >>> Maybe(None).unwrap("default")
        'default'
        >>> Maybe(5).unwrap("default")
        5
        """
        return self._value if self._value is not None else default
    
    def unwrap_or_else(self, func: Callable[[], Any]) -> Any:
        """
        Получить значение или результат функции, если None.
        
        >>> Maybe(None).unwrap_or_else(lambda: "computed")
        'computed'
        """
        return self._value if self._value is not None else func()
    
    def map(self, func: Callable[[T], Any]) -> 'Maybe':
        """
        Применить функцию к значению, если оно есть.
        
        >>> Maybe(5).map(lambda x: x * 2)
        Maybe(10)
        >>> Maybe(None).map(lambda x: x * 2)
        Maybe(None)
        """
        if self._value is None:
            return Maybe(None)
        try:
            return Maybe(func(self._value))
        except Exception:
            return Maybe(None)
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Maybe':
        """
        Оставить значение, если оно удовлетворяет условию.
        
        >>> Maybe(5).filter(lambda x: x > 3)
        Maybe(5)
        >>> Maybe(5).filter(lambda x: x > 10)
        Maybe(None)
        """
        if self._value is None:
            return Maybe(None)
        try:
            if predicate(self._value):
                return self
            return Maybe(None)
        except Exception:
            return Maybe(None)
    
    def is_none(self) -> bool:
        """Проверить, является ли значение None"""
        return self._value is None
    
    def is_some(self) -> bool:
        """Проверить, есть ли значение"""
        return self._value is not None
    
    def to_list(self) -> list:
        """Преобразовать в список: Some(x) -> [x], None -> []"""
        return [self._value] if self._value is not None else []


# === Вспомогательные функции ===

def maybe(value: Any) -> Maybe:
    """
    Обернуть значение в Maybe.
    
    >>> maybe(5)
    Maybe(5)
    >>> maybe(None)
    Maybe(None)
    """
    return Maybe(value)


def safe_call(func: Callable, *args: Any, **kwargs: Any) -> Maybe:
    """
    Безопасный вызов функции, которая может упасть или вернуть None.
    
    >>> safe_call(lambda: 1/0)
    Maybe(None)
    >>> safe_call(lambda x: x * 2, 5)
    Maybe(10)
    """
    try:
        return Maybe(func(*args, **kwargs))
    except Exception:
        return Maybe(None)


def first(iterable: Any, predicate: Optional[Callable] = None) -> Maybe:
    """
    Безопасно получить первый элемент коллекции.
    
    >>> first([1, 2, 3])
    Maybe(1)
    >>> first([])
    Maybe(None)
    >>> first([1, 2, 3], lambda x: x > 2)
    Maybe(3)
    """
    try:
        if predicate:
            for item in iterable:
                if predicate(item):
                    return Maybe(item)
            return Maybe(None)
        return Maybe(next(iter(iterable)))
    except (StopIteration, TypeError):
        return Maybe(None)


def last(iterable: Any) -> Maybe:
    """
    Безопасно получить последний элемент коллекции.
    Работает с любыми итерируемыми объектами.
    """
    try:
        # Для списков и кортежей - быстро
        if hasattr(iterable, '__getitem__') and hasattr(iterable, '__len__'):
            if len(iterable) == 0:
                return Maybe(None)
            return Maybe(iterable[-1])
        
        # Для остальных итерируемых - перебираем
        last_item = None
        found = False
        for item in iterable:
            last_item = item
            found = True
        
        return Maybe(last_item) if found else Maybe(None)
    except (TypeError, IndexError, KeyError):
        return Maybe(None)


def get_path(data: Any, *keys: Any) -> Maybe:
    """
    Безопасно получить значение по цепочке ключей.
    
    >>> data = {'user': {'name': 'Alice'}}
    >>> get_path(data, 'user', 'name')
    Maybe('Alice')
    >>> get_path(data, 'user', 'age')
    Maybe(None)
    """
    current = data
    for key in keys:
        if current is None:
            return Maybe(None)
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            return Maybe(None)
    return Maybe(current)


# === Экспорт ===

__all__ = [
    'Maybe',
    'maybe',
    'safe_call',
    'first',
    'last',
    'get_path',
]