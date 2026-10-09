"""Exécute les cellules fournies sans les modifier, depuis la racine du dépôt."""
import argparse
from pathlib import Path
import nbformat
from nbclient import NotebookClient

parser = argparse.ArgumentParser()
parser.add_argument('--bonus', action='store_true', help='Exécuter uniquement le notebook des six bonus')
args = parser.parse_args()
racine = Path(__file__).resolve().parent
relatif = ('analyses/m2_tp1/bonus/TP_M2_1_Bonus_eq02.ipynb' if args.bonus
           else 'analyses/m2_tp1/TP_M2_1_Signal_PPG_eq02.ipynb')
chemin = racine / relatif
notebook = nbformat.read(chemin, as_version=4)
def progression(cell_index, **kwargs):
    if notebook.cells[cell_index].cell_type == 'code':
        print(f'Cellule {cell_index + 1}/{len(notebook.cells)}', flush=True)
client = NotebookClient(notebook, timeout=1800 if args.bonus else 300,
                        kernel_name='python3', resources={'metadata': {'path': str(racine)}},
                        on_cell_start=progression)
client.execute()
nbformat.write(notebook, chemin)
print(f'Notebook exécuté et enregistré : {chemin}')
