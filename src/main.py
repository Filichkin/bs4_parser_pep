import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    DOWNLOAD_DIR,
    MAIN_DOC_URL,
    MAIN_PEP_URL,
    EXPECTED_STATUS
)
from exceptions import VersionsListNotFoundException
from outputs import control_output
from utils import find_tag, get_response, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)

    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 > a'
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    warnings = []

    for a_tag in tqdm(sections_by_python, desc='Парсинг новостей'):
        version_link = urljoin(whats_new_url, a_tag['href'])
        try:
            soup = get_soup(session, version_link)
            title = find_tag(soup, 'h1').text.strip()
            dl_tag = soup.find('dl')
            dl_tag_text = dl_tag.text.replace('\n', ' ')
            results.append((version_link, title, dl_tag_text))
        except ConnectionError as error:
            warnings.append(
                {
                    'link': version_link,
                    'error': error
                    }
                )
    for warning in warnings:
        logging.warning(warning)

    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise VersionsListNotFoundException()
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)

    pdf_a4_link = soup.select_one(
        'table.docutils a[href$="pdf-a4.zip"]'
        )['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOAD_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    numerical_url = urljoin(MAIN_PEP_URL, 'numerical')
    soup = get_soup(session, numerical_url)

    num_index = find_tag(
        soup,
        'section',
        {'id': 'numerical-index'}
    )
    tbody = find_tag(num_index, 'tbody')
    peps_rows = tbody.find_all('tr')
    count_pep = len(peps_rows)
    rows_in_table = {'Status': 'Count'}

    warnings = []
    for pep_row in tqdm(peps_rows, desc='Парсинг PEP:'):
        status_in_table = find_tag(pep_row, 'abbr').text[1:]
        url_tag = find_tag(
            pep_row,
            'a',
            {'class': 'pep reference internal'}
        )
        pep_url = urljoin(MAIN_PEP_URL, url_tag['href'])
        response = get_response(session, pep_url)
        soup = BeautifulSoup(response.text, features='lxml')
        status_tag = soup.find(text='Status').parent
        status = status_tag.next_sibling.next_sibling.text
        expected_status = EXPECTED_STATUS[status_in_table]
        if status not in expected_status:
            warnings.append(
                {
                    'url': pep_url,
                    'real_status': status,
                    'expected_statuses': expected_status
                    }
                )
            continue
        rows_in_table.setdefault(status, 0)
        rows_in_table[status] += 1

    if warnings:
        error_messages = [
            f"Несовпадающие статусы:\n"
            f"URL: {warning['url']}\n"
            f"Статус на странице: {warning['real_status']}\n"
            f"Ожидаемые статусы: {warning['expected_statuses']}"
            for warning in warnings
            ]
        logging.warning('\n\n'.join(error_messages))
    rows_in_table['Total'] = count_pep
    results = list(rows_in_table.items())
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
