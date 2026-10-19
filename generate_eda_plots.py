import os
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    cleaned_path = "data/processed/cleaned_jobs.csv"
    raw_path = "data/raw/jobs_raw_latest.csv"
    
    if os.path.exists(cleaned_path):
        print(f"Loading cleaned data from {cleaned_path}")
        df = pd.read_csv(cleaned_path)
    elif os.path.exists(raw_path):
        print(f"Loading raw data from {raw_path}")
        df = pd.read_csv(raw_path)
        df['source'] = df['source'].fillna('Inconnu')
        df['ville'] = df['ville'].fillna('Non spécifié')
    else:
        print("Error: No data found. Please run the scraper first.")
        return

    # Create output directory for figures
    fig_dir = "reports/figures"
    os.makedirs(fig_dir, exist_ok=True)
    sns.set_theme(style="whitegrid")

    # 1. Repartition of IT offers by Source
    print("Generating source distribution plot...")
    plt.figure(figsize=(8, 5))
    source_counts = df['source'].value_counts()
    
    colors = sns.color_palette("muted", len(source_counts))
    sns.barplot(x=source_counts.index, y=source_counts.values, hue=source_counts.index, palette=colors, legend=False)
    
    plt.title("Répartition des offres d'emploi IT par Source (Scraping)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Plateforme de Recrutement", fontsize=12, labelpad=10)
    plt.ylabel("Nombre d'offres", fontsize=12, labelpad=10)
    
    for i, v in enumerate(source_counts.values):
        plt.text(i, v + (max(source_counts.values) * 0.01), str(v), ha='center', va='bottom', fontsize=11, fontweight='bold')
        
    plt.tight_layout()
    source_plot_path = os.path.join(fig_dir, "repartition_sources.png")
    plt.savefig(source_plot_path, dpi=300)
    plt.close()
    print(f"Saved source plot to {source_plot_path}")

    # 2. Repartition of IT offers by City
    print("Generating city distribution plot...")
    plt.figure(figsize=(10, 6))
    
    df['ville_clean'] = df['ville'].fillna('Non spécifié').str.strip().str.capitalize()
    df['ville_clean'] = df['ville_clean'].replace({
        'Casablanca et région': 'Casablanca',
        'Rabat et région': 'Rabat',
        'Tanger et région': 'Tanger',
        'Marrakech et région': 'Marrakech',
        'Tout le maroc': 'Maroc',
        'Multivilles': 'Maroc'
    })
    
    city_counts = df['ville_clean'].value_counts().head(10)
    
    sns.barplot(x=city_counts.values, y=city_counts.index, hue=city_counts.index, palette="viridis", legend=False)
    
    plt.title("Top 10 des Villes par Répartition des Offres IT au Maroc", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Nombre d'offres", fontsize=12, labelpad=10)
    plt.ylabel("Ville", fontsize=12, labelpad=10)
    
    for i, v in enumerate(city_counts.values):
        plt.text(v + (max(city_counts.values) * 0.005), i, f" {v}", va='center', ha='left', fontsize=10, fontweight='bold')
        
    plt.tight_layout()
    city_plot_path = os.path.join(fig_dir, "repartition_villes.png")
    plt.savefig(city_plot_path, dpi=300)
    plt.close()
    print(f"Saved city plot to {city_plot_path}")

    # 3. Top sought-after technical skills
    print("Generating technical skills plot...")
    
    tech_cols = [col for col in df.columns if col.startswith('tech_')]
    
    if tech_cols:
        tech_counts = df[tech_cols].sum().sort_values(ascending=False).head(15)
        tech_names = [col.replace('tech_', '').replace('_', ' ').title() for col in tech_counts.index]
        tech_names = [name.replace('Cpp', 'C++').replace('Csharp', 'C#').replace('Net', '.NET').replace('Spring Boot', 'Spring Boot') for name in tech_names]
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x=tech_counts.values, y=tech_names, hue=tech_names, palette="rocket", legend=False)
        
        plt.title("Top 15 des Compétences Techniques les plus Recherchées", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Nombre d'occurrences", fontsize=12, labelpad=10)
        plt.ylabel("Technologie / Compétence", fontsize=12, labelpad=10)
        
        for i, v in enumerate(tech_counts.values):
            plt.text(v + (max(tech_counts.values) * 0.005), i, f" {int(v)}", va='center', ha='left', fontsize=10, fontweight='bold')
            
        plt.tight_layout()
        tech_plot_path = os.path.join(fig_dir, "competences_les_plus_recherchees.png")
        plt.savefig(tech_plot_path, dpi=300)
        plt.close()
        print(f"Saved technical skills plot to {tech_plot_path}")
        
        print("\n--- COMPÉTENCES CLÉS ---")
        for name, count in zip(tech_names, tech_counts.values):
            percentage = (count / len(df)) * 100
            print(f"- {name}: {int(count)} offres ({percentage:.1f}%)")
    else:
        print("No tech columns found in cleaned data. Creating placeholder chart from keywords list.")
        tech_keywords = ['python', 'java', 'javascript', 'typescript', 'php', 'c++', 'c#', 'sql', 'react', 'angular', 'docker', 'kubernetes', 'aws', 'azure', 'git']
        desc_text = df['description'].fillna('').str.lower() + " " + df['titre_poste'].fillna('').str.lower()
        counts = {}
        for kw in tech_keywords:
            pattern = rf'\b{re.escape(kw)}\b'
            if kw == 'c++':
                pattern = r'c\+\+'
            elif kw == 'c#':
                pattern = r'c\#'
            counts[kw.upper()] = desc_text.str.contains(pattern, regex=True).sum()
            
        counts_series = pd.Series(counts).sort_values(ascending=False)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x=counts_series.values, y=counts_series.index, hue=counts_series.index, palette="rocket", legend=False)
        plt.title("Top Compétences Techniques (Extraction Directe)", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Nombre d'offres", fontsize=12, labelpad=10)
        
        for i, v in enumerate(counts_series.values):
            plt.text(v + (max(counts_series.values) * 0.005), i, f" {int(v)}", va='center', ha='left', fontsize=10, fontweight='bold')
            
        plt.tight_layout()
        tech_plot_path = os.path.join(fig_dir, "competences_les_plus_recherchees.png")
        plt.savefig(tech_plot_path, dpi=300)
        plt.close()
        print(f"Saved fallback technical skills plot to {tech_plot_path}")
        
        print("\n--- COMPÉTENCES CLÉS ---")
        for name, count in zip(counts_series.index, counts_series.values):
            percentage = (count / len(df)) * 100
            print(f"- {name}: {int(count)} offres ({percentage:.1f}%)")

if __name__ == "__main__":
    main()
