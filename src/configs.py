import argparse
import logging

from constants import (
    BASE_DIR,
    DT_FORMAT,
    FILE_FORMAT,
    LOG_FORMAT,
    LOGS_DIR,
    PRETTY_FORMAT
)

from logging.handlers import RotatingFileHandler


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(PRETTY_FORMAT, FILE_FORMAT),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    log_dir = BASE_DIR / LOGS_DIR
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=1024 * 1024, backupCount=5
    )

    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
