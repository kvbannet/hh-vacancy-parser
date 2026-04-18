import requests
import json
import logging

BASE_URL = "https://api.hh.kz/vacancies"

DEFAULT_PARAMS = {
    "text": "python",
    "area": 40,  # Казахстан
    "per_page": 20
}

MIN_SALARY = 300000
MAX_PAGES = 3  # сколько страниц парсим

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def fetch_vacancies(params, page):
    try:
        params["page"] = page
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Ошибка запроса (page {page}): {e}")
        return None


def extract_salary(salary):
    if not salary:
        return None

    salary_from = salary.get("from")
    salary_to = salary.get("to")

    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    return salary_from or salary_to


def parse_vacancies(data):
    vacancies = []

    for item in data.get("items", []):
        salary = extract_salary(item.get("salary"))

        if salary is None or salary < MIN_SALARY:
            continue

        vacancies.append({
            "title": item.get("name", "Нет названия"),
            "company": item.get("employer", {}).get("name", "Не указано"),
            "salary": salary,
            "link": item.get("alternate_url", "Нет ссылки")
        })

    return vacancies


def save_to_json(vacancies, filename="vacancies.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(vacancies, f, ensure_ascii=False, indent=4)
        logging.info(f"Сохранено {len(vacancies)} вакансий в {filename}")
    except IOError as e:
        logging.error(f"Ошибка сохранения файла: {e}")


def main():
    all_vacancies = []

    for page in range(MAX_PAGES):
        data = fetch_vacancies(DEFAULT_PARAMS.copy(), page)

        if not data:
            continue

        vacancies = parse_vacancies(data)
        all_vacancies.extend(vacancies)

    if not all_vacancies:
        logging.warning("Вакансии не найдены")
        return

    for v in all_vacancies:
        print("\n--------------------")
        print("💼", v["title"])
        print("🏢", v["company"])
        print("💰", v["salary"])
        print("🔗", v["link"])

    save_to_json(all_vacancies)


if __name__ == "__main__":
    main()