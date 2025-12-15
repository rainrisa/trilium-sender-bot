from trilium_py.client import ETAPI
from datetime import datetime
from pathlib import Path
import threading
import asyncio


class Trilium:
    def __init__(self, etapi: ETAPI, note_id: str):
        self.ea = etapi
        self.note_id = note_id
        self._lock = threading.Lock()

    def _blocking_append(self, text: str, image_paths: list[str]):
        """
        The synchronous, blocking part of the append logic.
        This is designed to be run in a separate thread.
        NOTE: This function assumes the self._lock is ALREADY acquired.
        """
        image_blocks = []

        for path in image_paths:
            res = self.ea.create_attachment(
                ownerId=self.note_id,
                file_path=path,
            )

            attachment_id = res["attachmentId"]
            file_name = Path(path).name

            image_blocks.append(
                f"""
<figure class="image">
  <img src="api/attachments/{attachment_id}/image/{file_name}">
</figure>
""".strip()
            )

        block_parts = []

        if text.strip():
            text = text.replace("\n", "<br>")
            block_parts.append(f"<p>{text}</p>")

        block_parts.extend(image_blocks)

        if not block_parts:
            print("[Trilium] No content to append. Operation skipped.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        block_html = f"""
<hr>
<p>&nbsp;</p>
<div>
  <p><b>Telegram</b> · {timestamp}</p>
  {"".join(block_parts)}
</div>
<p>&nbsp;</p>
""".strip()

        old_html = self.ea.get_note_content(self.note_id)
        self.ea.update_note_content(self.note_id, old_html + block_html)

    async def append(self, text: str = "", image_paths: list[str] | None = None):
        """
        Append text and/or images to a Trilium HTML note (async-safe).

        :param text: plain text (can be empty)
        :param image_paths: list of local image paths (can be empty)
        """
        image_paths = image_paths or []

        await asyncio.to_thread(self._lock.acquire)
        try:
            await asyncio.to_thread(self._blocking_append, text, image_paths)
        finally:
            self._lock.release()
