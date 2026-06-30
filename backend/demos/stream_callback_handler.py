from src.app.server.base.base_stream_handler import BaseStreamHandler
from src.app.utils.logger_util import log_response


class StreamCallbackHandler(BaseStreamHandler):

    async def handle_stream(self, stream):
        log_response(stream)
