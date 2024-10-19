from player_stats_scraper import PlayerStatsScraper
from player_radar_comparison import PlayerComparisonRadarChart

# Étape 1 : Scraper les statistiques des joueurs
player_urls = [
    ("https://fbref.com/fr/joueurs/3b029691/all_comps/Statistiques-Vitinha-Stats---Toutes-les-competitions", "Vitinha"),
    ("https://fbref.com/fr/joueurs/1467af0d/all_comps/Statistiques-Marco-Verratti-Stats---Toutes-les-competitions", "Verratti")
]


# Créer une instance du scraper
scraper = PlayerStatsScraper(output_dir="data/")

# Scraper, traiter et fusionner les statistiques
scraper.run(player_urls)

# Étape 2 : Comparer les joueurs avec des radars
player_files = {
    'Vitinha': 'data/Vitinha_merged_stats.csv',
    'Verratti': 'data/Verratti_merged_stats.csv'
}

categories = {
    'Finition': ['Buts_x', 'B-PénM', 'PénM_x', 'PénT_x', 'PrgR', 'Buts_y', 'Tirs_x', 'TC', 'TC%', 
                        'Tir/90', 'TC/90', 'B/Tir', 'B/TC', 'Dist', 'CF', 'PénM_y', 'PénT_y', 'Tirs_y'],
    'Création':  ['PrgC_x', 'Touches', 'SurfRépDéf', 'ZDéf_x', 'MilTer_x', 'ZOff_x', 'SurfRépOff',
                        'Action de jeu', 'Balle au pied', 'TotDist_x', 'DistBut_x', 'PrgC_y', '1/3_x', 'AMT', 'AMB'],
    'Playmaker': ['PD_x', 'PrgP_x', 'Cmp', 'Att_y', 'Cmp%', 'TotDist_y', 'DistBut_y', 'PD_y', 'xAG_x', 'xA',
                         'A-xAG', 'PC', '1/3_y', 'PPA', 'CntSR', 'PrgP_y', 'PassLive', 'PassDead'],
    'Dribble': ['Att_x', 'Succ', 'Succ%', 'Tkld', 'Tkld%', 'TO', 'Ftp'],
    'Défense': ['Déf', 'Tcl', 'TclR', 'ZDéf_y', 'MilTer_y', 'ZOff_y', 'Tcl.1', 'Att', 'Tcl%', 
                       'Balles contrées', 'Tirs', 'Passe', 'Int', 'Tcl+Int', 'Dég'],
            }

category_labels = ['Qualité de finition', 'Création balle au pied', 'Création à la passe', 'Qualité de Dribbles', 'Efforts défensifs']

# Créer une instance de la classe radar
comparison = PlayerComparisonRadarChart(
    player_files=player_files,
    competitions_to_keep=['1. Champions Lg', '1. Ligue 1'],
    start_season='2017-2018',
    exclude_columns=['Saison', 'Âge', 'Équipe', 'Comp', 'Titulaire', 'Min', 'Joueur'],
    categories=categories,
    category_labels=category_labels
)

# Générer les radars pour chaque saison
comparison.plot_comparison_for_all_seasons()

# Comparer Vitinha saison 23-24 contre Verratti saison 22-23
#comparison.plot_comparison_between_seasons(('Vitinha', '2022-2023'), ('Verratti', '2022-2023'))

