import logging, os

os.system("color")

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

def colorize(color):
  def colorize_decorator(func):
    def colorize_wrapper(message, *args, **kwargs):
      return func(f'{color}{message}' + '\033[0m', *args, **kwargs)

    return colorize_wrapper
  return colorize_decorator

grey   = colorize('\033[90m')
red    = colorize('\033[31m')
yellow = colorize('\033[33m')

logger.debug   = grey(logger.debug)
logger.error = red(logger.error)
logger.warning = yellow(logger.warning)