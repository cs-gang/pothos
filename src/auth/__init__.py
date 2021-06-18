"""Functions and classes to help authenticate users with Firebase."""
import time


class IDGenerator:
    """
    Snowflake generator.
    Used for making both user IDs before saving them in firebase and our database.

    Usage:
        ```
        sf = IDGenerator()
        user_id = next(sf)
        ```
    """

    def __init__(self):
        self.wid = 0
        self.inc = 0

    def __next__(self) -> int:
        t = round(time() * 1000) - 1609459200000
        self.inc += 1
        return (t << 14) | (self.wid << 6) | (self.inc % 2 ** 6)


class User:
    """
    Represents a user of Pothos.
    """

    pass
