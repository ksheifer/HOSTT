import os
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text, inspect, or_
from sqlalchemy.orm import sessionmaker
from app.models import Dictionary
import re

# Определим базовую директорию проекта
basedir = os.path.abspath(os.path.dirname(__file__))

# Правильная и переносимая инициализация Flask-приложения
app = Flask(
    __name__,
    template_folder=os.path.join(basedir, '..', 'templates'),
    static_folder=os.path.join(basedir, '..', 'static')
)

# Подключение базы данных
DATABASE_URL = f"sqlite:///{os.path.join(basedir, 'dictionary.db')}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()



# Функция для загрузки данных из базы данных
def load_dictionary():
    dictionary_data = []

    # Попытка загрузить данные из базы данных
    try:
        dictionary = session.query(Dictionary).all()
        for entry in dictionary:
            dictionary_data.append({
                'id': entry.id,
                'ҺАКАЛЫЫ': entry.haka.replace('\n', '<br>') if entry.haka else '',
                'САХАЛЫЫ': entry.sakha.replace('\n', '<br>') if entry.sakha else '',
                'НЬУУЧЧАЛЫЫ': entry.nuuchcha.replace('\n', '<br>') if entry.nuuchcha else '',
                'SIM': entry.sim,
                'ҺАКАЛЫЫ_ex': entry.haka_ex.replace('\n', '<br>') if entry.haka_ex else '',
                'САХАЛЫЫ_ex': entry.sakha_ex.replace('\n', '<br>') if entry.sakha_ex else '',
                'НЬУУЧЧАЛЫЫ_ex': entry.nuuchcha_ex.replace('\n', '<br>') if entry.nuuchcha_ex else '',
                'GROUP': entry.group,
                'morph': entry.morph if hasattr(entry, 'morph') else ''  # Safely add the morph field if available
            })
        return dictionary_data
    except Exception as e:
        print(f"Ошибка при загрузке данных из базы данных: {e}")

    return dictionary_data


def normalize_text(text):
    return (text.replace('е', 'ё')
            .replace('ҕ', '5')
            .replace('ь', 'һ')
            .replace('5', 'ҕ')
            .replace('ғ', 'ҕ')
            .replace('ң', 'ҥ')
            .replace('нг', 'ҥ')
            .replace('н,', 'ӈ'))


# Функция для токенизации строки: удаляет пунктуацию и пробелы, возвращает список токенов
def tokenize_text(text):
    return re.findall(r'\b\w+\b', text.lower())  # Находит слова и приводит их к нижнему регистру


# Функция для сравнения токенов из запроса и токенов в данных
def tokens_match(query_tokens, entry_tokens):
    return all(token in entry_tokens for token in query_tokens)


# Функция для поиска по префиксу (4 символа) в строках
def prefix_match(query_token, field):
    return field.startswith(query_token[:4])  # Проверка на префикс длиной 4 символа


# Функция для получения всех слов из одной группы
def get_words_in_group(group, dictionary):
    group_numbers = set(group.split(','))
    words_in_group = []
    for entry in dictionary:
        entry_groups = set(group.strip() for group in entry['GROUP'].split(','))
        if group_numbers & entry_groups:  # Пересечение групп
            words_in_group.append(entry)
    return words_in_group


# Функция для статистики
def calculate_statistics(dictionary):
    total_words = len(dictionary)
    if total_words == 0:
        return {
            "total_words": 0,
            "identical_percent": 0,
            "different_percent": 0,
            "partially_different_percent": 0
        }

    identical_words = 0
    different_words = 0
    partially_different_words = 0

    for entry in dictionary:
        sim_value = entry.get('SIM')
        if sim_value is not None:
            try:
                sim_value = int(sim_value)
            except ValueError:
                continue
            if sim_value == 100:
                identical_words += 1
            elif sim_value == 0:
                different_words += 1
            elif 0 < sim_value < 100:
                partially_different_words += 1

    identical_percent = round((identical_words / total_words) * 100)
    different_percent = round((different_words / total_words) * 100)
    partially_different_percent = 100 - identical_percent - different_percent

    return {
        "total_words": total_words,
        "identical_percent": identical_percent,
        "different_percent": different_percent,
        "partially_different_percent": partially_different_percent
    }


# Функция для вычисления позиции первого совпадения
def get_first_match_position(query_tokens, text):
    positions = []
    for token in query_tokens:
        match = re.search(re.escape(token), text)
        if match:
            positions.append(match.start())
    return min(positions) if positions else float('inf')  # Если нет совпадений, возвращаем "бесконечность"


@app.route("/", methods=["GET", "POST"])
def index():
    dictionary = load_dictionary()  # Загружаем данные из базы данных
    results = []  # Основные результаты поиска
    grouped_results = []  # Результаты для отдельной таблицы
    error_message = None  # Сообщение об ошибке

    search_query = request.args.get("search_word", "")

    stats = calculate_statistics(dictionary)

    if search_query:
        normalized_query = normalize_text(search_query.lower())
        query_tokens = tokenize_text(normalized_query)

        exact_matches = []
        prefix_matches = []

        for entry in dictionary:
            nyuchchaly_tokens = tokenize_text(normalize_text(entry.get('НЬУУЧЧАЛЫЫ', '')))
            hakaly_tokens = tokenize_text(normalize_text(entry.get('ҺАКАЛЫЫ', '')))
            sakhaly_tokens = tokenize_text(normalize_text(entry.get('САХАЛЫЫ', '')))
            nyuchchaly_ex_tokens = tokenize_text(normalize_text(entry.get('НЬУУЧЧАЛЫЫ_ex', '')))
            hakaly_ex_tokens = tokenize_text(normalize_text(entry.get('ҺАКАЛЫЫ_ex', '')))
            sakhaly_ex_tokens = tokenize_text(normalize_text(entry.get('САХАЛЫЫ_ex', '')))

            if (tokens_match(query_tokens, nyuchchaly_tokens) or
                    tokens_match(query_tokens, hakaly_tokens) or
                    tokens_match(query_tokens, sakhaly_tokens) or
                    tokens_match(query_tokens, nyuchchaly_ex_tokens) or
                    tokens_match(query_tokens, hakaly_ex_tokens) or
                    tokens_match(query_tokens, sakhaly_ex_tokens)):
                exact_matches.append(entry)

        if exact_matches:
            def match_priority(entry):
                fields = [
                    entry.get('ҺАКАЛЫЫ', ''), entry.get('САХАЛЫЫ', ''), entry.get('НЬУУЧЧАЛЫЫ', ''),
                    entry.get('ҺАКАЛЫЫ_ex', ''), entry.get('САХАЛЫЫ_ex', ''), entry.get('НЬУУЧЧАЛЫЫ_ex', '')
                ]
                for i, field in enumerate(fields):
                    if tokens_match(query_tokens, tokenize_text(normalize_text(field))):
                        return i  # Чем меньше индекс, тем выше приоритет

                return len(fields)  # На случай, если нет совпадений

            exact_matches.sort(key=match_priority)

            matched_groups = set()
            seen_ids = set()

            for match in exact_matches:
                matched_groups.update(match['GROUP'].split(','))
                if match['id'] not in seen_ids:
                    results.append(match)
                    seen_ids.add(match['id'])

            for group in matched_groups:
                words_in_group = get_words_in_group(group, dictionary)
                for word in words_in_group:
                    if word['id'] not in seen_ids:
                        grouped_results.append(word)
                        seen_ids.add(word['id'])

        else:
            seen_ids = set()
            for entry in dictionary:
                nyuchchaly = entry.get('НЬУУЧЧАЛЫЫ', '')
                hakaly = entry.get('ҺАКАЛЫЫ', '')
                sakhaly = entry.get('САХАЛЫЫ', '')
                nyuchchaly_ex = entry.get('НЬУУЧЧАЛЫЫ_ex', '')
                hakaly_ex = entry.get('ҺАКАЛЫЫ_ex', '')
                sakhaly_ex = entry.get('САХАЛЫЫ_ex', '')

                if any(prefix_match(query_token, field) for query_token in query_tokens for field in
                       [hakaly, sakhaly, nyuchchaly, hakaly_ex, sakhaly_ex, nyuchchaly_ex]):
                    if entry['id'] not in seen_ids:
                        prefix_matches.append(entry)
                        seen_ids.add(entry['id'])

            prefix_matches = sorted(prefix_matches, key=lambda entry: get_first_match_position(query_tokens,
                                                                                               entry.get('ҺАКАЛЫЫ', '') +
                                                                                               entry.get('САХАЛЫЫ', '') +
                                                                                               entry.get('НЬУУЧЧАЛЫЫ', '')))

            matched_groups = set()

            for match in prefix_matches:
                matched_groups.update(match['GROUP'].split(','))

            for group in matched_groups:
                words_in_group = get_words_in_group(group, dictionary)
                for word in words_in_group:
                    if word['id'] not in seen_ids:
                        grouped_results.append(word)
                        seen_ids.add(word['id'])

            results.extend(prefix_matches)

    return render_template(
        'index.html',
        results=results,
        grouped_results=grouped_results,
        search_query=search_query,
        error_message=error_message,
        total_words=stats["total_words"],
        identical_words=f"{stats['identical_percent']}%",
        different_words=f"{stats['different_percent']}%",
        partially_different_words=f"{stats['partially_different_percent']}%"
    )



@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/statistics')
def statistics():
    # Load the dictionary data
    dictionary = load_dictionary()

    # Calculate statistics
    stats = calculate_statistics(dictionary)

    # Render the statistics page with calculated values
    return render_template(
        'statistics.html',
        total_words=stats["total_words"],
        identical_words=f"{stats['identical_percent']}%",
        different_words=f"{stats['different_percent']}%",
        partially_different_words=f"{stats['partially_different_percent']}%"
    )


@app.route('/phonetics')
def phonetics():
    return render_template('phonetics.html')


@app.route('/morphology')
def morphology():
    return render_template('morphology.html')


@app.route('/lexicon')
def lexicon():
    return render_template('lexicon.html')


@app.route('/semantics')
def semantics():
    return render_template('semantics.html')


from flask import render_template
from sqlalchemy import or_


@app.route('/etymology')
def etymology():
    # Получаем данные из базы данных для разных категорий
    evn_words = get_unique_words(get_evn_words())
    rus_words = get_unique_words(get_rus_words())
    ngan_words = get_unique_words(get_ngan_words())
    mong_words = get_unique_words(get_mong_words())
    other_words = get_unique_words(get_other_words())

    # Передаем все результаты в шаблон
    return render_template(
        'etymology.html',
        evn_words=evn_words,
        rus_words=rus_words,
        ngan_words=ngan_words,
        mong_words=mong_words,
        other_words=other_words
    )


def get_unique_words(word_list):
    """Удаляет дубликаты из списка слов по уникальному ключу"""
    seen = set()
    unique_data = []

    for item in word_list:
        key = (item['ҺАКАЛЫЫ'], item['САХАЛЫЫ'], item['НЬУУЧЧАЛЫЫ'])  # Уникальный ключ
        if key not in seen:
            seen.add(key)
            unique_data.append(item)

    return unique_data


def get_evn_words():
    results_haka = session.query(Dictionary).filter(Dictionary.haka.like("%эвенк%")).all()
    results_sakha = session.query(Dictionary).filter(Dictionary.sakha.like("%эвенк%")).all()
    return process_results(results_haka + results_sakha)


def get_rus_words():
    results_haka = session.query(Dictionary).filter(Dictionary.haka.like("%рус%")).all()
    results_sakha = session.query(Dictionary).filter(Dictionary.sakha.like("%рус%")).all()
    return process_results(results_haka + results_sakha)


def get_ngan_words():
    results = session.query(Dictionary).filter(Dictionary.haka.like("%нган%")).all()
    return process_results(results)


def get_mong_words():
    results_haka = session.query(Dictionary).filter(Dictionary.haka.like("%Монг%")).all()
    results_sakha = session.query(Dictionary).filter(Dictionary.sakha.like("%Монг%")).all()
    return process_results(results_haka + results_sakha)


def get_other_words():
    results_other = session.query(Dictionary).filter(
        or_(
            Dictionary.haka.like("%норв%"),
            Dictionary.sakha.like("%норв%"),
            Dictionary.haka.like("%кит%"),
            Dictionary.sakha.like("%кит%")
        )
    ).all()
    return process_results(results_other)


def process_results(results):
    """Форматирует результаты в единый список"""
    data = []
    for item in results:
        data.append({
            'ҺАКАЛЫЫ': item.haka,
            'САХАЛЫЫ': item.sakha,
            'SIM': item.sim,
            'НЬУУЧЧАЛЫЫ': item.nuuchcha,
            'ҺАКАЛЫЫ_ex': item.haka_ex,
            'САХАЛЫЫ_ex': item.sakha_ex,
            'НЬУУЧЧАЛЫЫ_ex': item.nuuchcha_ex,
        })
    return data


if __name__ == "__main__":
    app.run(debug=True)
