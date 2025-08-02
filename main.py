import logging

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    print("Starting telegram bot. Version 0.0.1")
    from TelegramBot.start import start
    
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('telegram.ext').setLevel(logging.WARNING)
    logging.getLogger('telegram.request').setLevel(logging.WARNING)
    logging.getLogger('telegram.ext._application').setLevel(logging.WARNING)
    
    start()