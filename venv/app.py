import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Чтение и очистка данных
df = pd.read_csv('games.csv')

# Удаление данных с пропусками и фильтрация по годам
df = df.dropna()
df = df[(df['Year_of_Release'] >= 2000) & (df['Year_of_Release'] <= 2022)]

# Преобразование рейтинга в числовой вид
rating_mapping = {
    'E': 3,     # Everyone
    'E10+': 10, # Everyone 10+
    'T': 13,    # Teen
    'M': 17,    # Mature
    'AO': 18,   # Adults Only
    'K-A': 6    # Kids to Adults (старый рейтинг, аналог E)
}
df['Numeric_Rating'] = df['Rating'].map(rating_mapping)

# Создание Dash-приложения
app = dash.Dash(__name__)

# Layout дашборда
app.layout = html.Div(children=[
    html.H1("Анализ игровой индустрии"),
    html.P("Этот дашборд позволяет анализировать количество и оценки игр на разных платформах и жанрах за выбранные годы."),
    
    # Фильтры
    html.Div([
        dcc.Dropdown(
            id='platform-filter',
            options=[{'label': platform, 'value': platform} for platform in df['Platform'].unique()],
            multi=True,
            value=df['Platform'].unique(),
            placeholder="Выберите платформу"
        ),
        dcc.Dropdown(
            id='genre-filter',
            options=[{'label': genre, 'value': genre} for genre in df['Genre'].unique()],
            multi=True,
            value=df['Genre'].unique(),
            placeholder="Выберите жанр"
        ),
        dcc.RangeSlider(
            id='year-slider',
            min=df['Year_of_Release'].min(),
            max=df['Year_of_Release'].max(),
            value=[2000, 2022],
            marks={str(year): str(year) for year in range(2000, 2023, 2)},
            step=1
        ),
    ], style={'display': 'flex', 'gap': '20px'}),
    
    # Графики
    html.Div([
        html.Div([
            html.H4("Общее количество игр"),
            html.Div(id='total-games')
        ]),
        html.Div([
            html.H4("Общая средняя оценка игроков"),
            html.Div(id='avg-user-score')
        ]),
        html.Div([
            html.H4("Общая средняя оценка критиков"),
            html.Div(id='avg-critic-score')
        ]),
    ], style={'display': 'flex', 'gap': '50px'}),
    
    dcc.Graph(id='games-by-year-platform'),
    dcc.Graph(id='scores-scatter'),
    dcc.Graph(id='avg-rating-by-genre'),
])

# Callback для обновления графиков и метрик
@app.callback(
    [Output('total-games', 'children'),
     Output('avg-user-score', 'children'),
     Output('avg-critic-score', 'children'),
     Output('games-by-year-platform', 'figure'),
     Output('scores-scatter', 'figure'),
     Output('avg-rating-by-genre', 'figure')],
    [Input('platform-filter', 'value'),
     Input('genre-filter', 'value'),
     Input('year-slider', 'value')]
)
def update_dashboard(selected_platforms, selected_genres, selected_years):
    filtered_df = df[(df['Platform'].isin(selected_platforms)) &
                     (df['Genre'].isin(selected_genres)) &
                     (df['Year_of_Release'] >= selected_years[0]) &
                     (df['Year_of_Release'] <= selected_years[1])]

    # Метрики
    total_games = len(filtered_df)
    avg_user_score = filtered_df['User_Score'].mean()
    avg_critic_score = filtered_df['Critic_Score'].mean()

    # Stacked Area Plot (игры по годам и платформам)
    games_by_year_platform = px.area(
        filtered_df,
        x='Year_of_Release',
        y='Name',
        color='Platform',
        title="Количество игр по годам и платформам"
    )

    # Scatter plot (оценки игроков и критиков по жанрам)
    scores_scatter = px.scatter(
        filtered_df,
        x='User_Score',
        y='Critic_Score',
        color='Genre',
        title="Оценки игроков и критиков по жанрам"
    )

    # Bar/Line chart (средний возрастной рейтинг по жанрам)
    avg_rating_by_genre = filtered_df.groupby('Genre').agg({'Numeric_Rating': 'mean'}).reset_index()
    avg_rating_chart = px.bar(
        avg_rating_by_genre,
        x='Genre',
        y='Numeric_Rating',
        title="Средний возрастной рейтинг по жанрам"
    )

    return (
        f"{total_games} игр",
        f"Средняя оценка игроков: {avg_user_score:.2f}",
        f"Средняя оценка критиков: {avg_critic_score:.2f}",
        games_by_year_platform,
        scores_scatter,
        avg_rating_chart
    )

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
