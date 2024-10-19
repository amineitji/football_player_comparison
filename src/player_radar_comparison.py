import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import numpy as np
from math import pi
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec

class PlayerComparisonRadarChart:
    def __init__(self, player_files, competitions_to_keep, start_season, exclude_columns, 
                 categories, category_labels, color1="#000000", color2="#3b3700"):
        self.player_files = player_files
        self.competitions_to_keep = competitions_to_keep
        self.start_season = start_season
        self.exclude_columns = exclude_columns
        self.categories = categories
        self.category_labels = category_labels
        self.color1 = color1
        self.color2 = color2
        self.data = self.load_and_process_data()
        
    def load_and_process_data(self):
        # Charger et concaténer les données des fichiers des joueurs
        data_frames = []
        for player_name, file_path in self.player_files.items():
            player_stats = pd.read_csv(file_path)
            player_stats['Joueur'] = player_name
            data_frames.append(player_stats)
        
        data = pd.concat(data_frames)

        # Filtrer les compétitions
        data = data[data['Comp'].isin(self.competitions_to_keep)]

        # Filtrer les saisons
        data = data[data['Saison'] >= self.start_season]

        # Exclure les colonnes non pertinentes
        data_cleaned = data.drop(columns=self.exclude_columns)

        # Remplacer les valeurs NaN dans les colonnes numériques
        numeric_columns = data_cleaned.select_dtypes(include=[np.number]).columns
        data_cleaned[numeric_columns] = data_cleaned[numeric_columns].fillna(data_cleaned[numeric_columns].mean())

        # Grouper par saison, âge, équipe et joueur
        data_grouped = data.groupby(['Saison', 'Âge', 'Équipe', 'Joueur']).sum().reset_index()

        return data_grouped

    def normalize_data(self, data):
        # Normaliser chaque groupe de données avec StandardScaler
        scaler = StandardScaler()
        return pd.DataFrame(scaler.fit_transform(data), columns=data.columns)

    def compute_mean_components(self, data_grouped):
        # Séparer les données en catégories (ici on suppose que `categories` est un dict de colonnes)
        components_mean = {}
        for comp_name, columns in self.categories.items():
            data_comp = data_grouped[columns]
            scaled_data = self.normalize_data(data_comp)
            components_mean[comp_name] = scaled_data.mean(axis=1)

        # Combiner les moyennes dans un DataFrame
        composantes_data = pd.DataFrame({
            'Saison': data_grouped['Saison'],
            'Équipe': data_grouped['Équipe'],
            'Joueur': data_grouped['Joueur']
        })

        for comp_name, mean_values in components_mean.items():
            composantes_data[comp_name] = mean_values

        return composantes_data

    def create_gradient_background(self, fig):
        """Crée un fond en dégradé vertical couvrant toute la figure."""
        gradient = np.linspace(0, 1, 256).reshape(-1, 1)
        gradient = np.hstack((gradient, gradient))
        cmap = mcolors.LinearSegmentedColormap.from_list("", [self.color1, self.color2])
        ax = fig.add_axes([0, 0, 1, 1], zorder=-1)
        ax.axis('off')
        ax.imshow(gradient, aspect='auto', cmap=cmap, extent=[0, 1, 0, 1])

    def customize_axes(self, ax):
        """Personnalise les axes avec du blanc et du gras."""
        ax.spines['polar'].set_color('white')  # Contour des axes en blanc
        ax.spines['polar'].set_linewidth(2)  # Contours plus épais

    def create_radar_chart(self, data, saison):
        N = len(self.categories)

        # Angles pour chaque catégorie
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]  # Boucler pour fermer le cercle

        # Initialiser la figure avec un GridSpec pour un meilleur contrôle
        fig = plt.figure(figsize=(14, 14), facecolor='none')
        gs = GridSpec(1, 1)

        # Créer le fond en dégradé
        self.create_gradient_background(fig)

        # Créer le radar chart
        ax = fig.add_subplot(gs[0], polar=True, facecolor='none')

        # Tracer pour chaque joueur
        for i, row in data.iterrows():
            values = row[self.categories.keys()].values.flatten().tolist()
            values += values[:1]  # Boucler pour fermer le cercle

            # Tracer en fonction du joueur
            if row['Joueur'] == list(self.player_files.keys())[0]:
                ax.plot(angles, values, linewidth=4, linestyle='solid', label=row['Joueur'], color='red', zorder=4)
                ax.fill(angles, values, color='red', alpha=0.3)
            else:
                ax.plot(angles, values, linewidth=4, linestyle='solid', label=row['Joueur'], color='blue', zorder=4)
                ax.fill(angles, values, color='blue', alpha=0.3)

        # Dessiner les labels personnalisés pour chaque catégorie
        plt.xticks(angles[:-1], self.category_labels, color='white', fontsize=18, fontweight='bold')

        ax.set_yticklabels([f'{v:.2f}' for v in ax.get_yticks()], color='white', fontsize=16)

        # Personnaliser les axes
        self.customize_axes(ax)

        # Ajouter le titre
        ax.set_title(f'Comparaison des joueurs - Saison {saison}', size=25, color='white', fontweight='bold', y=1.2)
        
        ax.text(0, 0, "La graduation d'un radar chart reflète des mesures normalisées\nsur plusieurs axes, où chaque cercle concentrique représente\nune isovaleur, et les valeurs augmentent du centre vers les bords,\nsouvent standardisées par z-score.", 
        fontsize=8, color='white', ha='center', transform=ax.transAxes, fontweight='bold')


        # Ajouter l'étiquette Twitter
        ax.text(1.15, 0.94, "@TarbouchData", fontsize=18, color='white', ha='center', transform=ax.transAxes, alpha=0.8,fontweight='bold')


        # Ajouter une légende
        legend = ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=20)
        plt.setp(legend.get_texts(), color='black')

        # Afficher le graphique
        plt.tight_layout(pad=2)
        plt.savefig('viz_data/comparaison_joueurs_saison_' + str(saison) + '.png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())

        plt.show()

    def plot_comparison_for_all_seasons(self):
        # Calculer les moyennes des composantes pour chaque saison
        composantes_data = self.compute_mean_components(self.data)

        # Créer une boucle pour chaque saison
        seasons = composantes_data['Saison'].unique()
        for saison in seasons:
            # Filtrer les données pour chaque saison
            data_for_season = composantes_data[(composantes_data['Saison'] == saison) & 
                                               (composantes_data['Joueur'].isin(self.player_files.keys()))]
            
            # Créer le radar chart
            self.create_radar_chart(data_for_season, saison)

    def plot_comparison_between_seasons(self, player_season_1, player_season_2):
        """
        Compare un joueur d'une saison spécifique contre un autre joueur d'une autre saison.

        :param player_season_1: Tuple (nom_joueur, saison) ex: ('Vitinha', '2022-2023')
        :param player_season_2: Tuple (nom_joueur, saison) ex: ('Verratti', '2021-2022')
        """
        # Calculer les moyennes des composantes pour chaque saison
        composantes_data = self.compute_mean_components(self.data)

        # Filtrer les données pour le premier joueur et sa saison
        data_player_1 = composantes_data[(composantes_data['Joueur'] == player_season_1[0]) &
                                         (composantes_data['Saison'] == player_season_1[1])]

        # Filtrer les données pour le deuxième joueur et sa saison
        data_player_2 = composantes_data[(composantes_data['Joueur'] == player_season_2[0]) &
                                         (composantes_data['Saison'] == player_season_2[1])]

        # Vérifier si les deux ensembles de données ne sont pas vides
        if data_player_1.empty or data_player_2.empty:
            print(f"Impossible de trouver les données pour les saisons ou joueurs spécifiés : {player_season_1} ou {player_season_2}")
            return

        # Fusionner les données pour les deux joueurs
        data_comparison = pd.concat([data_player_1, data_player_2])

        # Créer le radar chart pour la comparaison entre les saisons des deux joueurs
        self.create_radar_chart(data_comparison, f"{player_season_1[1]} vs {player_season_2[1]}")

