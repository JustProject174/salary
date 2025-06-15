import pandas as pd
import numpy as np

# Функция для извлечения числовых значений зарплаты
import pandas as pd
import numpy as np

def extract_salary(salary_str):
    salary_str = salary_str.replace(" ", "").lower()
    if "не указана" in salary_str:
        return None
    elif "от" in salary_str and "до" in salary_str:
        parts = salary_str.split("до")
        salary_from = int(parts[0].replace("от", "").strip())
        salary_to = int(parts[1].strip())
        return (salary_from + salary_to) // 2
    elif "от" in salary_str:
        return int(salary_str.replace("от", "").strip())
    elif "до" in salary_str:
        return int(salary_str.replace("до", "").strip())
    elif "руб" in salary_str:
        return int(salary_str.replace("руб", "").strip())
    return None
# Функция для расчета средней зарплаты
def calculate_average_salary(vacancies):
    total_salary = sum(vacancy['salary'] for vacancy in vacancies if vacancy['salary'] is not None)
    average_salary = total_salary / len(vacancies) if vacancies else 0
    return average_salary

def calculate_percentiles(vacancies):
    city_percentiles = {}
    
    for city, salaries in vacancies.items():
        # Фильтруем пустые значения
        salaries = [s for s in salaries if s is not None]
        
        if salaries:
            p25 = np.percentile(salaries, 25)
            p50 = np.percentile(salaries, 50)  # Медиана
            p75 = np.percentile(salaries, 75)
            
            city_percentiles[city] = {
                'P25': p25,
                'P50': p50,
                'P75': p75
            }
    
    return city_percentiles

# Пример использования
if __name__ == "__main__":
    median_salary = calculate_median_salary()
    print(f"Медианная зарплата для введенной должности: {median_salary} руб.")
