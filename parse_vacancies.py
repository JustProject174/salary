import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Используем неинтерактивный бэкенд
import matplotlib.pyplot as plt


# Функция для парсинга вакансий с hh.ru с использованием API
def parse_vacancies_api(job_title, pages=5):
    vacancies = []
    url = "https://api.hh.ru/vacancies"

    for page in range(pages):
        # Параметры для запроса
        params = {
            "text": job_title,
            "area": 113,  # Исключаем Москву (1 - Москва, 2 - другие регионы)
            "page": page,
            "per_page": 20  # Количество вакансий на одной странице
        }

        # Отправляем GET-запрос
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Ошибка при запросе на страницу {page + 1}: {response.status_code}")
            continue

        data = response.json()

        # Ищем все вакансии на странице
        for vacancy in data['items']:
            title = vacancy.get('name', 'Нет названия')
            salary = vacancy.get('salary', None)
            if salary:
                salary = parse_salary(salary)

            # Проверяем, что вакансия не из Москвы
            if vacancy['area']['id'] != "1":  # Идентификатор Москвы в API - "1"
                vacancies.append({
                    "title": title,
                    "salary": salary,
                    "city": vacancy['area']['name'],
                    "industry": vacancy.get('specialization', {}).get('name', 'Не указана')
                })

    print(f"Найдено вакансий: {len(vacancies)}")
    return vacancies

# Функция для парсинга зарплаты
def parse_salary(salary_data):
    # Проверяем, есть ли зарплата в указанном диапазоне
    if salary_data['from'] and salary_data['to']:
        return (salary_data['from'] + salary_data['to']) // 2
    elif salary_data['from']:
        return salary_data['from']
    elif salary_data['to']:
        return salary_data['to']
    else:
        return None

# Функция для расчета перцентилей (P25, P50, P75)
def calculate_percentiles(vacancies):
    salaries = [vacancy['salary'] for vacancy in vacancies if vacancy['salary'] is not None]
    df = pd.DataFrame(salaries, columns=['salary'])
    p25 = df['salary'].quantile(0.25)
    p50 = df['salary'].quantile(0.50)
    p75 = df['salary'].quantile(0.75)
    return p25, p50, p75

# Функция для группировки вакансий по схожим зарплатам
def group_similar_salaries(vacancies, tolerance=5000):
    salary_groups = []

    # Сортируем вакансии по зарплатам
    vacancies_sorted = sorted(vacancies, key=lambda x: x['salary'] if x['salary'] is not None else 0)

    # Группируем по зарплатам с учетом допустимой погрешности
    group = []
    last_salary = None

    for vacancy in vacancies_sorted:
        salary = vacancy['salary']
        if salary is not None:
            if last_salary is None or abs(salary - last_salary) <= tolerance:
                group.append(vacancy)
            else:
                salary_groups.append(group)
                group = [vacancy]
        last_salary = salary

    if group:
        salary_groups.append(group)  # Добавляем последнюю группу

    return salary_groups

# Функция для сохранения данных в Excel
def save_to_excel(vacancies, filename="vacancies_data.xlsx"):
    df = pd.DataFrame(vacancies)
    df.to_excel(filename, index=False)
    print(f"Данные сохранены в файл: {filename}")

# Функция для построения графика
def plot_scatter(vacancies, grouped_salaries):
    # Подготовка данных для отображения на графике
    grouped_data = []
    for group in grouped_salaries:
        cities = [vacancy['city'] for vacancy in group]
        avg_salary = np.mean([vacancy['salary'] for vacancy in group if vacancy['salary'] is not None])
        grouped_data.append([avg_salary, cities])

    # Подготовка данных для графика
    avg_salaries = [data[0] for data in grouped_data]
    cities = [", ".join(data[1]) for data in grouped_data]  # Объединение городов в строку для каждой группы

    # Построение графика
    df = pd.DataFrame(list(zip(avg_salaries, cities)), columns=['Salary', 'Cities'])

    plt.figure(figsize=(10, 6))
    plt.scatter(df['Salary'], df['Cities'], marker='o')
    plt.title("Зарплаты по городам")
    plt.xlabel("Зарплата (руб.)")
    plt.ylabel("Города")
    plt.tight_layout()
    plt.show()

# Основной процесс
def main():
    job_title = input("Введите должность: ")
    vacancies = parse_vacancies_api(job_title, pages=5)  # Увеличено количество страниц

    if vacancies:
        # Группировка вакансий по зарплатам
        grouped_salaries = group_similar_salaries(vacancies)

        # Построение графика
        plot_scatter(vacancies, grouped_salaries)

        # Сохранение данных в файл Excel
        save_to_excel(vacancies)

    else:
        print(f"Не удалось найти вакансии для должности '{job_title}', исключая Москву.")

if __name__ == "__main__":
    main()
