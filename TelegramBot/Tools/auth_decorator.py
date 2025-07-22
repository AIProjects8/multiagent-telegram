from functools import wraps
from config import Config

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id: int = update.effective_user.id
        if user_id not in Config.from_env().allowed_user_ids:
            print(f"Access denied for {user_id}.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped