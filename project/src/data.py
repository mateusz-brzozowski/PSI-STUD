from datetime import datetime


class Data:
    data_stream_id: int
    time: datetime
    content: bytes

    def __init__(self,
                 data_stream_id: int,
                 time: datetime,
                 content: bytes) -> None:
        self.data_stream_id = data_stream_id
        self.time = time
        self.content = content
