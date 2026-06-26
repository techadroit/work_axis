from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from backend.app.llm.checkpoointer.base_checkpointer import BaseCheckpointer
from core.utils.file_util import get_install_root, get_data_path


class AppSqliteCheckpointer(BaseCheckpointer):

    def __init__(self):
        self.db_path = get_data_path() / "checkpoints" / "app_checkpoints.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn_str = str(self.db_path.resolve())

    def create_checkpoint(self, *args, **kwargs):
        return AsyncSqliteSaver.from_conn_string(self.conn_str)
