import csv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Настройка базы данных SQLite
DATABASE_URL = "sqlite:///dictionary.db"
engine = create_engine(DATABASE_URL, echo=True)

# Создание базового класса для декларативных моделей
Base = declarative_base()

# Модель таблицы
class Dictionary(Base):
    __tablename__ = 'dictionary'
    id = Column(Integer, primary_key=True, autoincrement=True)
    haka = Column(String, nullable=False)  # ҺАКАЛЫЫ
    sakha = Column(String, nullable=False)  # САХАЛЫЫ
    nuuchcha = Column(String, nullable=False)  # НЬУУЧЧАЛЫЫ
    sim = Column(Integer, nullable=True)  # SIM
    haka_ex = Column(String, nullable=True)  # ҺАКАЛЫЫ_ex
    sakha_ex = Column(String, nullable=True)  # САХАЛЫЫ_ex
    nuuchcha_ex = Column(String, nullable=True)  # НЬУУЧЧАЛЫЫ_ex
    group = Column(String, nullable=True)  # GROUP


# Создание таблицы
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()


# Функция для импорта данных из CSV
def import_csv_to_sqlalchemy(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')  # Убедитесь, что разделитель правильно указан
        for row in reader:
            # Обработка значения SIM
            sim_value = row.get('SIM', '')  # Получаем значение из столбца SIM
            sim = int(sim_value) if sim_value.isdigit() else None  # Преобразуем в число, если это возможно

            # Создание записи
            entry = Dictionary(
                haka=row.get('ҺАКАЛЫЫ', ''),
                sakha=row.get('САХАЛЫЫ', ''),
                nuuchcha=row.get('НЬУУЧЧАЛЫЫ', ''),
                sim=sim,
                haka_ex=row.get('ҺАКАЛЫЫ_ex', ''),
                sakha_ex=row.get('САХАЛЫЫ_ex', ''),
                nuuchcha_ex=row.get('НЬУУЧЧАЛЫЫ_ex', ''),
                group=row.get('GROUP', '')
            )
            # Добавление записи в сессию
            session.add(entry)
    # Сохранение изменений в базе данных
    session.commit()


# Укажите путь к вашему CSV-файлу
csv_file_path = "/Users/karinasheifer/PycharmProjects/online_dict/data/tyldit.csv"
import_csv_to_sqlalchemy(csv_file_path)