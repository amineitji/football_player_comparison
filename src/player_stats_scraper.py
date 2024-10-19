import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class PlayerStatsScraper:
    def __init__(self, output_dir="data/"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def scrape_and_save(self, url, player_name):
        # Envoyer une requête à la page web
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Liste des IDs des tableaux à scraper
            table_ids = [
                'stats_passing_expanded', 
                'stats_standard_expanded', 
                'stats_shooting_expanded',  
                'stats_gca_expanded', 
                'stats_defense_expanded',
                'stats_possession_expanded'
            ]
            
            # Scraper et sauvegarder uniquement les tableaux avec les IDs spécifiés
            for table_id in table_ids:
                table = soup.find('table', {'id': table_id})
                if table:
                    # Lire le tableau avec pandas
                    df = pd.read_html(str(table))[0]
                    
                    # Définir le nom du fichier CSV
                    csv_filename = os.path.join(self.output_dir, f"{player_name}_{table_id}.csv")
                    
                    # Sauvegarder le dataframe dans un fichier CSV
                    df.to_csv(csv_filename, index=False)
                    print(f"Tableau {table_id} pour {player_name} sauvegardé dans {csv_filename}")
                else:
                    print(f"Tableau avec l'ID {table_id} non trouvé pour {player_name}")
        else:
            print(f"Échec de la requête pour {url}. Code de statut : {response.status_code}")

    def clean_and_transform_csv(self, file_path):
        # Lire le fichier CSV en ignorant la première ligne
        df = pd.read_csv(file_path, skiprows=1)
        
        # Définir une expression régulière pour détecter les lignes qui commencent par une année au format 'yyyy-yyyy'
        date_pattern = re.compile(r'^\d{4}-\d{4}$')
        
        # Filtrer les lignes qui commencent par une date
        df_cleaned = df[df.iloc[:, 0].astype(str).apply(lambda x: bool(date_pattern.match(x)))]
        
        # Remplacer les valeurs vides (NaN) et les chaînes vides par None
        df_cleaned = df_cleaned.replace("", None).where(pd.notnull(df_cleaned), None)

        # Supprimer la colonne "Matchs" si elle existe
        if "Matchs" in df_cleaned.columns:
            df_cleaned = df_cleaned.drop(columns=["Matchs"])
        
        # Réécrire le fichier modifié
        df_cleaned.to_csv(file_path, index=False)
        print(f"Fichier nettoyé et transformé : {file_path}")

    def process_csvs(self, player_name):
        # Parcourir tous les fichiers CSV du joueur et nettoyer les fichiers
        for file_name in os.listdir(self.output_dir):
            if file_name.startswith(player_name) and file_name.endswith(".csv"):
                file_path = os.path.join(self.output_dir, file_name)
                self.clean_and_transform_csv(file_path)

    def modify_csv_columns(self, file_suffix, columns_to_remove):
        # Parcours de tous les fichiers CSV dans le répertoire qui se terminent par le suffixe
        for filename in os.listdir(self.output_dir):
            if filename.endswith(file_suffix):
                file_path = os.path.join(self.output_dir, filename)

                # Chargement du fichier CSV dans un DataFrame
                df = pd.read_csv(file_path)

                # Suppression des colonnes spécifiques
                df = df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors='ignore')

                # Remplacement des valeurs manquantes par -1
                df.fillna(-1, inplace=True)

                # Sauvegarde du fichier CSV mis à jour
                df.to_csv(file_path, index=False)

                print(f"Colonnes modifiées et calcul appliqué pour {filename}")

    def process_all_csv_modifications(self):
        # Modifier les colonnes selon le fichier
        self.modify_csv_columns("_standard_expanded.csv", ['xG', 'npxG', 'npxG/Sh', 'G-xG', 'np:G-xG', '90', 'Pays'])
        self.modify_csv_columns("_shooting_expanded.csv", ['xG', 'npxG', 'npxG/Sh', 'G-xG', 'np:G-xG', '90', 'Pays'])
        self.modify_csv_columns("_passing_expanded.csv", ['Cmp.1', 'Att.1', 'Cmp%.1', 'Cmp.2', 'Att.2', 'Cmp%.2', 'Cmp.3', 'Att.3', 'Cmp%.3', 'Pays', '90'])
        self.modify_csv_columns("_possession_expanded.csv", ['Pays', '90', 'CSR', 'Manqué', 'Perte', 'Rec', 'PrgR'])
        self.modify_csv_columns("_defense_expanded.csv", ['Pays', '90', 'Manqués', 'Err'])
        self.modify_csv_columns("_gca_expanded.csv", ['Pays', '90', 'AMT90', 'AMB90', 'PassLive.1', 'PassDead.1', 'TO.1', 'Tirs.1', 'Ftp.1', 'Déf.1'])

    def merge_player_stats_and_delete_files(self, player_name):
        """
        Fusionne les fichiers CSV du joueur, puis supprime les fichiers originaux après la fusion.
        """
        file_paths = [os.path.join(self.output_dir, file_name) for file_name in os.listdir(self.output_dir) if file_name.startswith(player_name)]

        if not file_paths:
            print(f"Aucun fichier trouvé pour {player_name}")
            return

        # Charger tous les CSV
        dfs = [pd.read_csv(file) for file in file_paths]

        # Colonnes communes pour la jointure
        common_columns = ['Saison', 'Âge', 'Équipe', 'Comp']

        # Fusionner tous les DataFrames
        df_merged = dfs[0]
        for df in dfs[1:]:
            df_merged = df_merged.merge(df, on=common_columns, how='outer')

        # Fusionner les colonnes identiques en vérifiant si elles ont des valeurs identiques
        df_final = df_merged.loc[:, ~df_merged.columns.duplicated()]

        for col in df_merged.columns[df_merged.columns.duplicated(keep=False)]:
            duplicated_columns = df_merged.loc[:, df_merged.columns == col]
            if (duplicated_columns.nunique(axis=1) == 1).all():
                df_final[col] = duplicated_columns.iloc[:, 0]
            else:
                df_final = pd.concat([df_final, duplicated_columns], axis=1)

        # Sauvegarder le fichier fusionné
        output_file = os.path.join(self.output_dir, f"{player_name}_merged_stats.csv")
        df_final.to_csv(output_file, index=False)

        # Supprimer les fichiers CSV originaux
        for file in file_paths:
            os.remove(file)

        print(f"Tous les fichiers CSV ont été supprimés après la fusion pour {player_name}.")
        return output_file

    def run(self, player_urls):
        """
        Exécute l'ensemble du processus pour chaque joueur à partir des URLs fournies.
        :param player_urls: Liste de tuples contenant (url, player_name)
        """
        for url, player_name in player_urls:
            print(f"Scraping et traitement pour {player_name}")
            self.scrape_and_save(url, player_name)
            self.process_csvs(player_name)
        
        self.process_all_csv_modifications()

        for _, player_name in player_urls:
            merged_file = self.merge_player_stats_and_delete_files(player_name)
            print(f"Fichier fusionné pour {player_name} : {merged_file}")