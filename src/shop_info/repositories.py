from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

from common.repositories import BaseRepository
from database.schemas import ShopInformation

__all__ = ('ShopInfoRepository',)


class ShopInfoRepository(BaseRepository):

    def get_value_or_none(self, key: str) -> str | None:
        statement = (
            select(ShopInformation.value)
            .where(ShopInformation.key == key)
        )
        with self._session_factory() as session:
            result = session.execute(statement).first()
        if result:
            return result[0]

    def upsert(self, *, key: str, value: str) -> None:
        statement = (
            insert(ShopInformation)
            .values(key=key, value=value)
            .on_conflict_do_update(
                index_elements=('key',),
                set_={
                    ShopInformation.value: value,
                }
            )
        )
        with self._session_factory() as session:
            with session.begin():
                session.execute(statement)
