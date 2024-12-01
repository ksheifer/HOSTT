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
        search_query=search_query
    )

if __name__ == "__main__":
    app.run(debug=True)
