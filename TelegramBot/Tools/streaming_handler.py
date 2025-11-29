from telegram import Update, Message
import time
import asyncio
import re
from typing import Callable, Any


class TelegramStreamingHandler:
    def __init__(self, update: Update, update_interval: float = 3.0, char_update_threshold: int = 100):
        self.update = update
        self.streaming_message: Message = None
        self.last_update_time = 0
        self.pending_text = None
        self.update_interval = update_interval
        self.flood_control_until = 0
        self.last_char_count = 0
        self.char_update_threshold = char_update_threshold
        self.max_length = 4096
    
    async def stream_chunk(self, _chunk: str, accumulated: str):
        current_time = time.time()
        self.pending_text = accumulated
        
        if current_time < self.flood_control_until:
            return
        
        display_text = accumulated[:self.max_length] if len(accumulated) > self.max_length else accumulated
        if len(accumulated) > self.max_length:
            display_text += "..."
        
        if self.streaming_message is None:
            self.streaming_message = await self.update.message.reply_text(display_text)
            self.last_update_time = current_time
            self.last_char_count = len(accumulated)
        else:
            time_since_last_update = current_time - self.last_update_time
            chars_since_last_update = len(accumulated) - self.last_char_count
            
            should_update = (
                time_since_last_update >= self.update_interval or
                chars_since_last_update >= self.char_update_threshold
            )
            
            if should_update:
                try:
                    await self.streaming_message.edit_text(display_text)
                    self.last_update_time = current_time
                    self.last_char_count = len(accumulated)
                    self.pending_text = None
                except Exception as e:
                    error_str = str(e)
                    
                    if "Flood control" in error_str or "Retry in" in error_str:
                        try:
                            retry_match = re.search(r'Retry in (\d+) seconds', error_str)
                            if retry_match:
                                retry_seconds = int(retry_match.group(1))
                                self.flood_control_until = current_time + retry_seconds + 2
                                print(f"Flood control: pausing updates for {retry_seconds + 2} seconds")
                        except Exception:
                            self.flood_control_until = current_time + 60
    
    async def finalize(self, final_text: str):
        max_length = 4096
        display_text = final_text[:max_length] if len(final_text) > max_length else final_text
        if len(final_text) > max_length:
            display_text += "..."
        
        if self.streaming_message:
            current_time = time.time()
            if current_time < self.flood_control_until:
                wait_time = self.flood_control_until - current_time
                print(f"Waiting {wait_time:.1f} seconds for flood control to clear before final update")
                await asyncio.sleep(wait_time + 1)
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await self.streaming_message.edit_text(display_text)
                    break
                except Exception as e:
                    error_str = str(e)
                    if attempt < max_retries - 1 and ("Flood control" in error_str or "Retry in" in error_str):
                        try:
                            retry_match = re.search(r'Retry in (\d+) seconds', error_str)
                            if retry_match:
                                retry_seconds = int(retry_match.group(1))
                                print(f"Final update flood control: waiting {retry_seconds} seconds")
                                await asyncio.sleep(retry_seconds + 1)
                                continue
                        except Exception:
                            await asyncio.sleep(5)
                            continue
                    else:
                        print(f"Error in final edit (attempt {attempt + 1}): {error_str}")
                        if attempt == max_retries - 1:
                            await self.update.message.reply_text(display_text)
        else:
            await self.update.message.reply_text(display_text)

