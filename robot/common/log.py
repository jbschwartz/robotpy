import logging

logger = logging.getLogger('Print Logger')
logger.setLevel(logging.DEBUG)

print_handler = logging.StreamHandler()

if __debug__:
  print_handler.setLevel(logging.DEBUG)
else:
  print_handler.setLevel(logging.ERROR)

print_format = logging.Formatter('[%(levelname)s] %(message)s')
print_handler.setFormatter(print_format)

logger.addHandler(print_handler)