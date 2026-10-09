"""Fonctions des bonus uniquement. Le code du TP principal reste inchangé."""
from pathlib import Path
import hashlib
import pickle
import struct
import urllib.request
import zlib
import numpy as np
import pandas as pd
from scipy import signal


def fc_fenetres(t_pics, instants, largeur=8.0):
    """Même convention d'intervalles que la boîte à outils du TP."""
    ibi = np.diff(t_pics)
    fin = t_pics[1:]
    fc = np.full(len(instants), np.nan)
    cv = np.full(len(instants), np.nan)
    for k, tc in enumerate(instants):
        dans = (fin >= tc - largeur / 2) & (fin < tc + largeur / 2)
        if dans.sum() >= 3:
            fc[k] = 60 / np.median(ibi[dans])
            cv[k] = np.std(ibi[dans]) / np.mean(ibi[dans])
    return fc, cv


def erreur(estimee, reference, masque=None):
    valide = np.isfinite(estimee) & np.isfinite(reference)
    if masque is not None:
        valide &= masque
    return float(np.mean(np.abs(estimee[valide] - reference[valide]))) if valide.any() else np.nan


def chaine(x, fs, instants, filtrer=True, causal=False):
    sos = signal.butter(4, [0.5, 5.0], fs=fs, btype='bandpass', output='sos')
    y = (signal.sosfilt(sos, x) if causal else signal.sosfiltfilt(sos, x)) if filtrer else x - np.mean(x)
    pics, _ = signal.find_peaks(y, distance=int(fs * 60 / 180), prominence=0.5 * np.std(y))
    fc, cv = fc_fenetres(pics / fs, instants)
    return y, pics, fc, cv


def qualite(fc, cv, seuil=0.15):
    return (cv < seuil) & (fc >= 40) & (fc <= 180)


def fc_fft(x, fs, instants):
    """FFT de 8 s, Hann, maximum entre 0,7 et 3 Hz, sans interpolation."""
    n = int(8 * fs)
    freq = np.fft.rfftfreq(n, 1 / fs)
    bande = (freq >= 0.7) & (freq <= 3)
    result = np.full(len(instants), np.nan)
    for k, tc in enumerate(instants):
        debut = round((tc - 4) * fs)
        if debut < 0 or debut + n > len(x):
            continue
        segment = x[debut:debut + n]
        puissance = np.abs(np.fft.rfft((segment - segment.mean()) * np.hanning(n))) ** 2
        result[k] = 60 * freq[bande][np.argmax(puissance[bande])]
    return result


def score_forme(x, pics, fs, instants):
    """Corrélation de chaque battement avec la forme moyenne de sa fenêtre.

    Extraits fixes de -0,20 à +0,30 s autour des pics, centrés et normalisés.
    Le score de la fenêtre est la corrélation minimale (critère conservateur).
    """
    avant, apres = round(0.20 * fs), round(0.30 * fs)
    bons = pics[(pics >= avant) & (pics + apres < len(x))]
    segments = np.array([x[p - avant:p + apres + 1] for p in bons])
    segments = segments - segments.mean(axis=1, keepdims=True)
    normes = np.linalg.norm(segments, axis=1, keepdims=True)
    segments = segments / np.maximum(normes, 1e-12)
    scores = np.full(len(instants), np.nan)
    for k, tc in enumerate(instants):
        dans = (bons / fs >= tc - 4) & (bons / fs < tc + 4)
        if dans.sum() < 3:
            continue
        moyenne = segments[dans].mean(axis=0)
        moyenne /= max(np.linalg.norm(moyenne), 1e-12)
        scores[k] = np.min(segments[dans] @ moyenne)
    return scores


def charger_bidmc(numero, racine, dossier_bonus):
    """Données officielles uniquement, sans repli synthétique, avec SHA-256."""
    dossier = Path(dossier_bonus) / 'data' / 'bidmc'
    dossier.mkdir(parents=True, exist_ok=True)
    manifest = dossier / 'SHA256SUMS.txt'
    if not manifest.exists():
        with urllib.request.urlopen('https://physionet.org/files/bidmc/1.0.0/SHA256SUMS.txt', timeout=90) as r:
            manifest.write_bytes(r.read())
    hashes = {line.split()[-1].split('/')[-1]: line.split()[0] for line in manifest.read_text().splitlines()}
    frames = []
    for suffixe in ['Signals', 'Numerics']:
        nom = f'bidmc_{numero:02d}_{suffixe}.csv'
        fichier = dossier / nom
        if not fichier.exists() and (Path(racine) / 'data' / nom).exists():
            fichier = Path(racine) / 'data' / nom
        if not fichier.exists():
            url = 'https://physionet.org/files/bidmc/1.0.0/bidmc_csv/' + nom
            with urllib.request.urlopen(url, timeout=180) as r:
                contenu = r.read()
            assert hashlib.sha256(contenu).hexdigest() == hashes[nom], nom
            fichier.write_bytes(contenu)
        assert hashlib.sha256(fichier.read_bytes()).hexdigest() == hashes[nom], nom
        df = pd.read_csv(fichier)
        df.columns = df.columns.str.strip()
        frames.append(df)
    return frames


def preparer_dalia(dossier_bonus):
    """Extrait le sujet S1 et la documentation du ZIP officiel, vérification CRC.

    Le serveur ne gère pas toujours HTTP Range. Lecture séquentielle jusqu'à S1,
    sans conserver les autres sujets (environ 1,3 Go transférés sur ce serveur).
    """
    dossier = Path(dossier_bonus) / 'data' / 'ppg_dalia'
    dossier.mkdir(parents=True, exist_ok=True)
    cible = dossier / 'S1.pkl'
    if not cible.exists():
        def lire(r, taille):
            morceaux = []
            while taille:
                b = r.read(min(taille, 1024 * 1024))
                if not b:
                    raise EOFError('Archive UCI incomplète')
                morceaux.append(b)
                taille -= len(b)
            return b''.join(morceaux)
        url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00495/data.zip'
        with urllib.request.urlopen(url, timeout=180) as r:
            while True:
                valeurs = struct.unpack('<4s5H3I2H', lire(r, 30))
                sig, _, flags, methode, _, _, crc, comp, taille, nomlen, extralen = valeurs
                if sig != b'PK\x03\x04' or flags & 8:
                    raise ValueError('Structure ZIP non prise en charge')
                nom = lire(r, nomlen).decode()
                lire(r, extralen)
                garder = nom.endswith('/S1.pkl') or nom.endswith('.pdf')
                print(nom, f'({comp / 1e6:.1f} Mo)', flush=True)
                morceaux = []
                restant = comp
                while restant:
                    bloc = lire(r, min(restant, 1024 * 1024))
                    restant -= len(bloc)
                    if garder:
                        morceaux.append(bloc)
                if garder:
                    contenu = b''.join(morceaux)
                    if methode == 8:
                        contenu = zlib.decompress(contenu, -15)
                    elif methode != 0:
                        raise ValueError('Compression ZIP non prise en charge')
                    assert len(contenu) == taille and zlib.crc32(contenu) == crc
                    (dossier / Path(nom).name).write_bytes(contenu)
                if nom.endswith('/S1.pkl'):
                    break

    class LectureRestreinte(pickle.Unpickler):
        def find_class(self, module, name):
            autorises = {('numpy.core.multiarray', '_reconstruct'),
                         ('numpy.core.multiarray', 'scalar'), ('numpy', 'ndarray'),
                         ('numpy', 'dtype'), ('_codecs', 'encode')}
            if (module, name) not in autorises:
                raise pickle.UnpicklingError(f'Classe inattendue : {module}.{name}')
            return super().find_class(module, name)
    with cible.open('rb') as f:
        d = LectureRestreinte(f, encoding='latin1').load()
    assert d['subject'] == 'S1'
    return (d['signal']['wrist']['BVP'].ravel(), d['signal']['wrist']['ACC'],
            np.asarray(d['label']), d['activity'].ravel())
