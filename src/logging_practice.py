import logging
import yfinance as yf

# log_records = []
# class ListHandler(logging.Handler):
#     def emit(self, record):
#         log_records.append(record.getMessage())

logger = logging.getLogger('yfinance')
print(logger.level)
# logger.setLevel(logging.NOTSET)

# stream_handler = logging.StreamHandler()
# # stream_handler.addFilter(lambda rec: 'delisted' in rec.getMessage().lower())
# logger.addHandler(stream_handler)

# list_handler = ListHandler()
# list_handler.addFilter(lambda rec: 'delisted' in rec.getMessage().lower())
# logger.addHandler(list_handler)

yf.Ticker('AABL').history()

# delisted_msgs = [msg for msg in log_records if 'delisted' in msg.lower()]

# if log_records:
#     print('LOG RECORDS', log_records)

logging.shutdown()
