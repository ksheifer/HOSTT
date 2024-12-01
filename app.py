import csv
from flask import Flask, render_template, request

app = Flask(__name__)

# Функция для загрузки данных из CSV
def load_dictionary():
    dictionary = []
    try:
        with open('/Users/karinasheifer/Documents/Languages/Turkic/NorthSiberian/DLG/tyldit.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter='\t')
            for row in csv_reader:
                row = {key.strip(): (value.strip() if value else '') for key, value in row.items()}
                dictionary.append(row)
    except Exception as e:
        print(f"Ошибка при загрузке словаря: {e}")
    return dictionary

# Функция для нормализации текста
def normalize_text(text):
    return text.replace('е', 'ё').replace('Е', 'Ё').replace('ё', 'е').replace('Ё', 'е') \
               .replace('ҕ', '5').replace('ҕ', '5') \
               .replace('һ', 'ь').replace('һ', 'ь') \
               .replace('5', 'ҕ').replace('ь', 'һ')

@app.route("/", methods=["GET", "POST"])
def index():
    dictionary = load_dictionary()  # Загружаем данные из CSV
    results = []  # Список для хранения результатов

    # Получаем общий поисковый запрос
    search_query = request.form.get("search_query", "")

    # Статистика по словам
    total_words = len(dictionary)  # Общее количество слов в словаре
    identical_words = 0  # Слова, где SIM == 100
    different_words = 0  # Слова, где SIM == 0
    partially_different_words = 0  # Слова, где SIM != 0 и SIM != 100

    # Перебираем все записи в словаре и считаем статистику
    for entry in dictionary:
        sim_value = entry.get('SIM')
        if sim_value:
            sim_value = int(sim_value)  # Преобразуем в число для сравнения
            if sim_value == 100:
                identical_words += 1
            elif sim_value == 0:
                different_words += 1
            else:
                partially_different_words += 1

    # Рассчитываем проценты (целые числа)
    identical_percent = int((identical_words / total_words) * 100) if total_words else 0
    different_percent = int((different_words / total_words) * 100) if total_words else 0
    partially_different_percent = int((partially_different_words / total_words) * 100) if total_words else 0

    # Очистка результатов перед новым поиском
    if not search_query:
        results = []  # Если нет запроса, очищаем старые результаты

    # Поиск по всем языкам
    if search_query:
        # Очищаем старые результаты перед добавлением новых
        results.clear()  # Очистка списка перед новым поиском
        for entry in dictionary:
            # Проверяем совпадение с любым языком
            if (normalize_text(search_query.lower()) in normalize_text(entry.get('НЬУУЧЧАЛЫЫ', '').lower())) or \
               (normalize_text(search_query.lower()) in normalize_text(entry.get('ҺАКАЛЫЫ', '').lower())) or \
               (normalize_text(search_query.lower()) in normalize_text(entry.get('САХАЛЫЫ', '').lower())):
                results.append(entry)

    # Отправляем данные в шаблон
    return render_template(
        'index.html',
        results=results,
        search_query=search_query,
        total_words=total_words,
        identical_words=f"{identical_percent}%",  # Процентное значение
        different_words=f"{different_percent}%",  # Процентное значение
        partially_different_words=f"{partially_different_percent}%"  # Процентное значение
    )

if __name__ == "__main__":
    app.run(debug=True)
