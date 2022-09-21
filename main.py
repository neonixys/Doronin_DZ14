# Импорт библиотеки flask
from flask import Flask

# Импорт модуля sqlite3
import sqlite3

# Импорт json
import json

app = Flask(__name__)


def get_data_sql(sql):
    """Создание подключения к БД с помощью метода sqlite3.connect"""
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        result = connection.execute(sql).fetchall()
    return result


@app.route('/movie/<title>', methods=['GET'])
def get_by_title(title):
    """ Представление страницы с выборкой фильма по названию в формате JSON"""
    result = {}
    for item in get_data_sql(sql=f"""
        SELECT title, country, release_year, listed_in as genre, description
        FROM netflix
        WHERE title LIKE '%{title.title()}%'
        ORDER BY release_year desc
        """):
        result = dict(item)

    return app.response_class(
        json.dumps(result, ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )


@app.route('/movie/<int:year_one>/to/<int:year_two>', methods=['GET'])
def get_by_period(year_one, year_two):
    """ Представление страницы с выборкой фильма по диапазону лет выпуска в формате JSON"""
    sql = f"""
        select * from netflix
        WHERE release_year between '{year_one}' AND '{year_two}'
        LIMIT 100
        """

    result = []
    for item in get_data_sql(sql):
        result.append(dict(item))

    return app.response_class(
        json.dumps(result[:100], ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )


@app.route('/rating/<rating>', methods=['GET'])
def get_rating(rating):
    """ Представление страницы поиска по рейтингу."""
    rating_dict = {
        "children": ("G", "G"),
        "family": ('G', 'PG', 'PG-13'),
        "adult": ('R', 'NC-17')
    }

    sql = f"""
        select * from netflix
        WHERE rating in {rating_dict.get(rating, ('PG', 'NC-17'))}
        """

    result = []
    for item in get_data_sql(sql):
        result.append(dict(item))

    return app.response_class(
        json.dumps(result, ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )


@app.route('/genre/<genre>', methods=['GET'])
def get_genre(genre):
    """ Представление страницы с выборкой 10 самых свежих фильмов в формате json по жанру"""
    sql = f"""
            select title, description from netflix
            WHERE listed_in LIKE '%{str(genre).title()}%'
            ORDER by release_year DESC
            LIMIT 10
        """

    result = []
    for item in get_data_sql(sql):
        result.append(dict(item))

    return app.response_class(
        json.dumps(result, ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )


def get_names(name1='Rose McIver', name2='Ben Lamb'):
    """ Функция получает в качестве аргумента имена двух актеров,
           и возвращает список тех, кто играет с ними в паре больше 2 раз"""
    global result
    sql = f"""
            select "cast" from netflix
            WHERE "cast" LIKE '%{name1}%'
            AND "cast" LIKE '%{name2}%'
        """
    names_dict = {}
    for item in get_data_sql(sql):
        result = dict(item)

        names = set(result.get('cast').split(", ")) - {name1, name2}

        for name in names:
            names_dict[name.strip()] = names_dict.get(name.strip(), 0) + 1

    print(names_dict)

    for key, value in names_dict.items():
        if value > 2:
            print(key)

    return app.response_class(
        json.dumps(result, ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )
#print(get_names())

def get_film(types='Movie', year=2020, genre='Horror'):
    """Функция передает тип картины (фильм или сериал),
        год выпуска и ее жанр и получать на выходе список
        названий картин с их описаниями в JSON."""
    sql = f"""
            select * from netflix
            WHERE type = '{types.title()}' 
            AND release_year = '{year}'
            AND listed_in LIKE  '%{genre.title()}%'
        """

    result = []
    for item in get_data_sql(sql):
        result.append(dict(item))

    return json.dumps(result, ensure_ascii=False, indent=4)

#print(get_film())

if __name__ == '__main__':
    app.run(port=5000, debug=True)
