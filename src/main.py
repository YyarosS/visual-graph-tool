import argparse
import sys
import os
import requests
import gzip
import io

from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
    
def fetch_and_parse_packages(repo_url):
    if repo_url.endswith('.gz'):
        response = requests.get(repo_url)
        response.raise_for_status()
        content = gzip.decompress(response.content).decode('utf-8')
    else:
        response = requests.get(repo_url)
        response.raise_for_status()
        content = response.text

    # Разделяем по двойным новым строкам
    packages_raw = content.split('\n\n')
    packages = []
    for pkg_raw in packages_raw:
        if pkg_raw.strip() == '':
            continue
        pkg_info = {}
        for line in pkg_raw.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                pkg_info[key] = value
        packages.append(pkg_info)
    return packages

def find_package_dependencies(packages, package_name):
    for pkg in packages:
        if pkg.get('Package') == package_name:
            depends = pkg.get('Depends', '')
            if depends:
                # Убираем версии и условия
                deps = [d.split('(')[0].strip() 
                        for d in depends.split(',')]
                return [d for d in deps if d]  # Убираем пустые строки
            else:
                return []
    return []

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

    # # Валидация URL или пути
    # if arguments.mode in ["remote"]:
    #     if not is_valid_url(arguments.repo_url):
    #         parser.error(f"Некорректный URL: {arguments.repo_url}")
    # elif arguments.mode in ["local"]:
    #     if not os.path.exists(arguments.repo_url):
    #         parser.error(f"Файл или директория не найдена: {arguments.repo_url}")
    # elif arguments.mode in ["mock"]:
    #     # В mock режиме URL может быть любым, даже фиктивным
    #     pass

    # print(f"package_name={arguments.package_name}")
    # print(f"repo_url={arguments.repo_url}")
    # print(f"mode={arguments.mode}")
    # print(f"output={arguments.output}")

    if arguments.mode == "remote":
        try:
            packages = fetch_and_parse_packages(arguments.repo_url)
        except Exception as e:
            parser.error(f"Не удалось загрузить или распарсить репозиторий: {e}")
    elif arguments.mode == "local":
        try:
            with open(arguments.repo_url, 'rb') as f:
                content = f.read()
            if arguments.repo_url.endswith('.gz'):
                content = gzip.decompress(content)
            packages = []
            raw = content.decode('utf-8')
            for pkg_raw in raw.split('\n\n'):
                if pkg_raw.strip() == '':
                    continue
                pkg_info = {}
                for line in pkg_raw.splitlines():
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        pkg_info[key] = value
                packages.append(pkg_info)
        except Exception as e:
            parser.error(f"Ошибка при чтении локального файла: {e}")
    else:
        packages = []

    dependencies = find_package_dependencies(packages, arguments.package_name)

    if dependencies:
        print("Зависимости для пакета '{}':".format(arguments.package_name))
        for dep in dependencies:
            print("- {}".format(dep))
    else:
        print("Зависимости для пакета '{}' не найдены.".format(arguments.package_name))
    return 0

if __name__ == "__main__":
    sys.exit(main())