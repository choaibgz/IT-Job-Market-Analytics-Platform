import subprocess
import sys
import os

def run_step(cmd_list, description):
    print("\n" + "=" * 60)
    print(f"  RUNNING: {description}")
    print("=" * 60)
    # Using sys.executable to run with same python interpreter
    cmd = [sys.executable] + cmd_list
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    print(result.stdout)
    if result.returncode != 0:
        print(f"[Error] Step failed with return code {result.returncode}")
        print("Stderr:")
        print(result.stderr)
        return False
    print(f"[OK] {description} completed successfully.")
    return True

def main():
    steps = [
        (['-m', 'src.preprocessing.clean_data'], "Prétraitement & NLP (clean_data.py)"),
        (['-m', 'src.models.train'], "Entraînement des modèles & Clustering (train.py)"),
        (['generate_eda_plots.py'], "Génération des graphiques EDA (generate_eda_plots.py)"),
        (['generate_notebooks.py'], "Génération des 4 Notebooks Jupyter (generate_notebooks.py)")
    ]
    
    for cmd, desc in steps:
        success = run_step(cmd, desc)
        if not success:
            print("\n[FAILED] Pipeline execution interrupted due to errors.")
            sys.exit(1)
            
    print("\n" + "=" * 60)
    print("  [SUCCESS] All pipeline steps completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
