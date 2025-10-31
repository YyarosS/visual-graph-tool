import argparse
import sys
import os

from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей для менеджера пакетов (Этап 1)"
    )

    parser.add_argument(
        "--package-name", "-n",
        type=str,
        required=True,
        help="Имя анализируемого пакета (например, mylib)"
    )

    parser.add_argument(
        "--repo-url", "-u",
        type=str,
        required=True,
        help="URL репозитория или путь к локальному файлу"
    )

    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["local", "remote", "mock"],
        required=True,
        help="Режим работы с репозиторием: local, remote, mock"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        choices=["ascii-tree", "json", "dot"],
        default="ascii-tree",
        help="Формат вывода зависимостей (по умолчанию: ascii-tree)"
    )

    arguments = parser.parse_args()

    # Валидация URL или пути
    if arguments.mode in ["remote"]:
        if not is_valid_url(arguments.repo_url):
            parser.error(f"Некорректный URL: {arguments.repo_url}")
    elif arguments.mode in ["local"]:
        if not os.path.exists(arguments.repo_url):
            parser.error(f"Файл или директория не найдена: {arguments.repo_url}")
    elif arguments.mode in ["mock"]:
        # В mock режиме URL может быть любым, даже фиктивным
        pass

    # Вывод параметров в формате ключ=значение
    print(f"package_name={arguments.package_name}")
    print(f"repo_url={arguments.repo_url}")
    print(f"mode={arguments.mode}")
    print(f"output={arguments.output}")

    return 0

if __name__ == "__main__":
    sys.exit(main())