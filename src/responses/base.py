from abc import ABC, abstractmethod


class BaseResponse(ABC):

    def __await__(self):
        return self._send_response().__await__()

    @abstractmethod
    async def _send_response(self):
        pass
