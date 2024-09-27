import requests
from bs4 import BeautifulSoup


def run(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        return print("Не удалось получить данные")
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    for row in soup.find_all('tr', valign='top'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            name = cells[0].get_text(strip=True)
            value_cell = cells[1]

            match name:
                case 'Organism':
                    print(f"Вид: {value_cell.get_text(strip=True)}")
                case 'Treatment protocol':
                    print(f"Обработка в эксперименте: {value_cell.get_text(strip=True)}")
                case 'Library strategy':
                    print(f"Тип эксперимента: {value_cell.get_text(strip=True)}")
                case 'Genotype':
                    print(f"Генотип: {value_cell.get_text(strip=True)}")
                case 'SRA':
                    if link := value_cell.find('a'):
                        print(f"Ссылка на сырые данные: {link.get('href')}")
                case s if s.startswith('Series'):
                    if link := value_cell.find('a'):
                        print(f"Ссылка на базу данных: https://www.ncbi.nlm.nih.gov{link.get('href')}")


if __name__ == '__main__':
    run('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM357351')
