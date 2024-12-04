import csv
from flask import Flask, render_template, request

app = Flask(__name__)

# Автообновление шаблонов
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Функция для загрузки данных из CSV
def load_dictionary():
    dictionary = []
    try:
        with open('/Users/karinasheifer/Documents/Languages/Turkic/NorthSiberian/DLG/tyldit.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter='\t')
            for row in csv_reader:
                # Заменяем \n на <br> в значениях
                row = {key.strip(): (value.strip().replace('\n', '<br>') if value else '') for key, value in row.items()}
                dictionary.append(row)
    except Exception as e:
        print(f"Ошибка при загрузке словаря: {e}")
    return dictionary

# Функция для нормализации текста
def normalize_text(text):
    return (text.replace('е', 'ё')
               .replace('ҕ', '5')
               .replace('һ', 'ь')
               .replace('5', 'ҕ')
               .replace('ң', 'ҥ'))

# Функция для токенизации строки: удаляет пунктуацию и пробелы, возвращает список токенов
def tokenize_text(text):
    return re.findall(r'\b\w+\b', text.lower())  # Находит слова и приводит их к нижнему регистру

# Функция для сравнения токенов из запроса и токенов в данных
def tokens_match(query_tokens, entry_tokens):
    # Проверяем, все ли токены из запроса присутствуют в токенах записи
    return all(token in entry_tokens for token in query_tokens)

@app.route("/", methods=["GET", "POST"])
def index():
    dictionary = load_dictionary()  # Загружаем данные из CSV
    results = []  # Список для хранения результатов
    error_message = None  # Сообщение об ошибке

    # Получаем общий поисковый запрос
    search_query = request.form.get("search_query", "")

    # Статистика по словам
    total_words = len(dictionary)  # Общее количество слов в словаре
    identical_words = 0  # Слова, где SIM == 100
    different_words = 0  # Слова, где SIM == 0
    partially_different_words = 0  # Слова, где SIM != 0 и SIM != 100

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

    identical_percent = int((identical_words / total_words) * 100) if total_words else 0
    different_percent = int((different_words / total_words) * 100) if total_words else 0
    partially_different_percent = int((partially_different_words / total_words) * 100) if total_words else 0

    # Поиск по запросу
    if search_query:
        normalized_query = normalize_text(search_query.lower())
        query_tokens = tokenize_text(normalized_query)  # Токенизация запроса
        print(f"Query tokens: {query_tokens}")  # Печать токенов запроса

        exact_matches = []
        prefix_matches = []

        for entry in dictionary:
            # Токенизация полей записи
            nyuchchaly_tokens = tokenize_text(normalize_text(entry.get('НЬУУЧЧАЛЫЫ', '')))
            hakaly_tokens = tokenize_text(normalize_text(entry.get('ҺАКАЛЫЫ', '')))
            sakhaly_tokens = tokenize_text(normalize_text(entry.get('САХАЛЫЫ', '')))

            print(f"Entry tokens: {nyuchchaly_tokens}, {hakaly_tokens}, {sakhaly_tokens}")  # Печать токенов записи

            # Проверяем точное совпадение токенов
            if (tokens_match(query_tokens, nyuchchaly_tokens) or
                tokens_match(query_tokens, hakaly_tokens) or
                tokens_match(query_tokens, sakhaly_tokens)):
                exact_matches.append(entry)
            else:
                # Проверяем совпадение по префиксу
                for field_tokens in [nyuchchaly_tokens, hakaly_tokens, sakhaly_tokens]:
                    # Определяем длину префикса на основе длины символов в каждом токене
                    prefix_length = 3 if all(len(token) <= 6 for token in field_tokens) else 4
                    print(f"Field tokens for prefix match check: {field_tokens}, prefix length: {prefix_length}")

                    # Проверяем совпадение по префиксу для токенов
                    for query_token, field_token in zip(query_tokens, field_tokens):
                        if not field_token.startswith(query_token[:prefix_length]):
                            break
                    else:
                        # Если цикл не прервался, значит, префиксное совпадение найдено
                        print(f"Prefix match found for entry: {entry}")
                        prefix_matches.append(entry)
                        break

        results = exact_matches + prefix_matches

        if not results:
            error_message = "Оо дьэ... тугу эмэ атыны көрдөөн көр"

    return render_template(
        'index.html',
        results=results,
        search_query=search_query,
        error_message=error_message,
        total_words=total_words,
        identical_words=f"{identical_percent}%",
        different_words=f"{different_percent}%",
        partially_different_words=f"{partially_different_percent}%"
    )

if __name__ == "__main__":
    app.run(debug=True)
