import json
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Callable
import codecs
import csv
import math

class Chapitre:
    def enregistre_longueur(self, argument: int | None) -> None:
        if isinstance(argument, str):
            self.longueur= int(argument)
        elif isinstance(argument, int):
            self.longueur = argument
        elif isinstance(argument, list):
            if len(argument) == 1 and isinstance(argument[0], str):
                self.longueur = int(argument[0])
            elif len(argument) == 1 and isinstance(argument[0], int):
                self.longueur = argument[0]
            else:
                messagebox.showerror("Erreur", "Longueur en millimètres attendue. Valeur reçue '" + argument[0] + "' de type " + str(type(argument[0])))  #type: ignore
                raise TypeError("Longueur en millimètres attendue. Valeur reçue '" + argument[0] + "' de type " + str(type(argument[0])))
        else:
            messagebox.showerror("Erreur", "Longueur en millimètres attendue. Valeur reçue '" + str(argument) + "' de type " + str(type(argument))) #type: ignore
            raise TypeError("Longueur en millimètres attendue. Valeur reçue '" + str(argument) + "' de type " + str(type(argument)))

    def meme_que(self, num_chap: int | None = None, num_livret: int | None  = None, modulateur: int = 0) -> str:
        if num_chap is None:
            return self.ref
        if modulateur == 0 and (num_livret == self.liste_a_ranger.livret.numero_livret or num_livret is None):
            return str(num_chap)
        if num_livret == self.liste_a_ranger.livret.numero_livret or num_livret is None:
            return str(int(self.liste_a_ranger.livret.get_num_cible(str(num_chap))) + modulateur)
        else:
            for dictio in self.liste_a_ranger.compte_rendu:
                if dictio["livret"] == str(num_livret) and dictio["ancien"] == str(num_chap):
                    return str(int(dictio["nouveau"]) + modulateur)
            return str(next((int(dictio["nouveau"]) + modulateur for dictio in self.liste_a_ranger.compte_rendu if dictio["livret"] == str(num_livret) and dictio["ancien"] == str(num_chap))))
    
    def enregistre_suites(self, argument: list[int] | None) -> None:
        if isinstance(argument, str):
            self.suites= [argument]
        elif isinstance(argument, bool):
            self.enregistre_numero_fixe(argument) #type: ignore
        elif isinstance(argument, int):
            self.suites = [str(argument)]
        elif isinstance(argument, list) and all(isinstance(a, str) for a in argument):
            self.suites = argument #type: ignore
        elif isinstance(argument, list) and all(isinstance(a, int) for a in argument): #type: ignore
            self.suites = [str(a) for a in argument]
        else:
            messagebox.showerror("Erreur", "Liste de chapitres connectés attendue. Valeur reçue '" + str(argument) + "' de type " + str(type(argument))) #type: ignore
            raise TypeError("Liste de chapitres connectés attendue. Valeur reçue '" + str(argument) + "' de type " + str(type(argument)))

    def enregistre_numero_fixe(self, argument: None | str) -> None:
        if isinstance(argument, type(None)):
            self.numero_fixe = False
            self.numero_cible = lambda _ : ""
        elif isinstance(argument, str): #type: ignore
            self.numero_fixe = True
            self.numero_cible = eval(argument)
        else:
            messagebox.showerror("Erreur", "Indication de numéro fixe attendue. Valeur reçue '" + str(argument) + "' de type " + str(type(argument))) #type: ignore
            raise TypeError("Indication de numéro fixe attendue. Valeur reçue '" + str(argument) + "' de type " + str(type(argument))) #type: ignore
        
    def update_spoil_strict(self) -> None:
        self.spoil_strict = list()
        for chap in self.liste_a_ranger.livret.get_all_chapitres():
            if chap.ref in (cchap for cchap in self.chapitres_lies if cchap not in self.suites):
                self.spoil_strict.extend(chap.suites)
        self.spoil_strict = list(set(self.spoil_strict))
        if self.ref in self.spoil_strict:
            self.spoil_strict.remove(self.ref)

    def __repr__(self) -> str:
        return f"chap{self.ref}"
    
    def __init__(self, ref: str, donnees: list[int|list[int]|str|bool|bool], liste_a_ranger: "ChapitresARanger"): #type: ignore
        self.ref : str = ref
        self.longueur : int
        self.suites : list[str] = []
        self.numero_fixe : bool = False
        self.double_colonne : bool = False
        self.chapitres_lies : set[str] = set()
        self.numero_cible : Callable[[Chapitre], str]
        self.liste_a_ranger : ChapitresARanger = liste_a_ranger
        self.prioritaire : bool = False
        self.spoil_strict: list[str] = list()

        if not isinstance(donnees,list): #type: ignore
            donnees = [donnees]
        if len(donnees) == 1: #type: ignore
            self.enregistre_longueur(donnees[0]) #type: ignore
        elif len(donnees) == 2: #type: ignore
            self.enregistre_longueur(donnees[0]) #type: ignore
            self.enregistre_suites(donnees[1]) #type: ignore
        elif len(donnees) == 3: #type: ignore
            self.enregistre_longueur(donnees[0]) #type: ignore
            self.enregistre_suites(donnees[1]) #type: ignore
            self.enregistre_numero_fixe(donnees[2]) #type: ignore
        elif len(donnees) == 4: #type: ignore
            self.enregistre_longueur(donnees[0]) #type: ignore
            self.enregistre_suites(donnees[1]) #type: ignore
            self.enregistre_numero_fixe(donnees[2]) #type: ignore
            self.double_colonne = donnees[3] #type: ignore
        elif len(donnees) == 5: #type: ignore
            self.enregistre_longueur(donnees[0]) #type: ignore
            self.enregistre_suites(donnees[1]) #type: ignore
            self.enregistre_numero_fixe(donnees[2]) #type: ignore
            self.double_colonne = donnees[3] #type: ignore
            self.prioritaire = donnees[4] #type: ignore
        else:
            messagebox.showerror("Erreur", "Trop d'arguments reçus.") #type: ignore
            raise IndexError("Trop d'arguments reçus.")
        self.chapitres_lies = set(self.suites)


class ChapitresARanger:
    def __init__(self, cr: str) -> None:
        self.liste_chapitres : list[Chapitre]= []
        self.adresse_fichie_source = source_address.get()
        self.numero_premier_chapitre : int
        self.livret : Livret
        self.compte_rendu : list[dict[str,str]] = []
        self.quantite_depart: int

        with open(cr, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                self.compte_rendu.append(row)

        with open(self.adresse_fichie_source) as f:
            json_data = json.load(f)
            for ref, donnees in json_data.items():
                self.liste_chapitres.append(Chapitre(ref, donnees, self))
        # self.numero_premier_chapitre = min([int(a.ref) for a in self.liste_chapitres])
        self.numero_premier_chapitre = int(settings["num_prem_chap"])
        self.quantite_depart = len(self.liste_chapitres)
        if settings["melanger_chap"]:
            random.shuffle(self.liste_chapitres)
        else:
            self.liste_chapitres.sort(key=lambda x: x.longueur, reverse=True)
        self.liste_chapitres.sort(key=lambda x: x.prioritaire, reverse=True)

        for chapitre1 in self.liste_chapitres:
            for chapitre2 in self.liste_chapitres:
                if chapitre1.ref in chapitre2.suites:
                    chapitre1.chapitres_lies.add(chapitre2.ref)

    
    def est_vide(self) -> bool:
        return False if len([chap for chap in self.liste_chapitres if chap.longueur > 0]) else True
    
    def update_spoil_strict(self) -> None:
        for chap in self.liste_chapitres:
            chap.update_spoil_strict()


class Colonne:
    def __init__(self, page : "Page") -> None:
        self.liste_chapitres : list[Chapitre] = []
        self.page = page
        
    def __str__(self) -> str:
        return ", ".join([str(chapitre.ref) for chapitre in sorted(self.liste_chapitres, key=lambda x:x.longueur)]) + f" Espace gaché {self.get_longueur_restante()} mm"

    def get_longueur_restante(self) -> int:
        return int(settings["longueur_max_colonne"] - sum(chapitre.longueur for chapitre in self.liste_chapitres))

    def recevoir(self, chapitre : Chapitre) -> None:
        num_fixe = str(self.page.livret.get_numero_prochain_chapitre())
        chapitre.numero_cible = lambda _: num_fixe
        self.liste_chapitres.append(chapitre)
        if chapitre.numero_fixe:
            self.page.liste_numeros_interdits_par_fixe.extend(list(chapitre.chapitres_lies))
        else:
            self.page.liste_numeros_interdits.extend(list(chapitre.chapitres_lies))
        if settings["interdire_spoil_strict"]:
            for chap in self.page.livret.get_all_chapitres():
                if chap.ref in (cchap for cchap in chapitre.chapitres_lies if cchap not in chapitre.suites):
                    if chapitre.numero_fixe:
                        self.page.liste_numeros_interdits_par_fixe.extend(list(chap.suites))
                    else:
                        self.page.liste_numeros_interdits.extend(list(chap.suites))
        self.page.livret.chapitres_a_ranger.update_spoil_strict()


        if chapitre in self.page.livret.chapitres_a_ranger.liste_chapitres:
            self.page.livret.chapitres_a_ranger.liste_chapitres.remove(chapitre)
        else:
            messagebox.showerror("Erreur", "Le chapitre à retirer n'est pas présent dans les listes") #type: ignore

    def tester_si_prochain_chapitre_est_fixe(self, modulateur: int = 0) -> bool:
        num_prochain_chap = str(self.page.livret.get_numero_prochain_chapitre() + modulateur)
        return num_prochain_chap in (chapitre.numero_cible(chapitre) for chapitre in self.page.livret.chapitres_a_ranger.liste_chapitres if chapitre.numero_fixe)

    def tester(self, liste_chapitres : list[Chapitre], cas_parfait :bool = True) -> bool:
        longueur_a_tester = sum([chapitre.longueur for chapitre in liste_chapitres])
        if (longueur_a_tester > self.get_longueur_restante() or (longueur_a_tester < (self.get_longueur_restante() - settings["gachi_autorise"]) and cas_parfait)):
            return False
        
        for chap in liste_chapitres:
            if chap.longueur < 1:
                return False
            if len(self.page.liste_colonnes) in (2,4) and chap.double_colonne:
                return False
            if (not chap.numero_fixe) and (chap.ref in self.page.liste_numeros_interdits or chap.ref in self.page.liste_numeros_interdits_par_fixe):
                return False
            if chap.numero_fixe and chap.ref in self.page.liste_numeros_interdits:
                return False
            for chap2 in liste_chapitres:
                if chap != chap2 and (chap.ref in chap2.chapitres_lies or chap.ref in chap2.spoil_strict):
                    return False
        return True

    def remplir(self, chapitre_specifique : Chapitre | None = None) -> Chapitre | None:
        compteur_boucle : int = 0
        pg["value"] = int(100 - len(self.page.livret.chapitres_a_ranger.liste_chapitres) / self.page.livret.chapitres_a_ranger.quantite_depart * 100)
        root.update_idletasks()

        # Chapitre double colonne
        if len(self.page.liste_colonnes) in (2,4):
            for chap in ([chapitre for chapitre in self.page.liste_colonnes[-2].liste_chapitres if chapitre.double_colonne]):
                # doublon = chap 
                self.liste_chapitres.append(chap)

        while True:
            root.update()
            pg2["value"] = 0
            chap1_ttk.set("")
            chap2_ttk.set("")
            chap3_ttk.set("")
            chap4_ttk.set("")
            num_ttk.set("Création du chapitre " + str(self.page.livret.get_numero_prochain_chapitre()))
            root.update_idletasks()
            compteur_boucle += 1

            # Chapitre fixe ou pas fixe
            if self.tester_si_prochain_chapitre_est_fixe():
                liste_chapitres_a_tester = [next((chap for chap in self.page.livret.chapitres_a_ranger.liste_chapitres if chap.numero_cible(chap) == str(self.page.livret.get_numero_prochain_chapitre())))]
            else:    
                liste_chapitres_a_tester = [chap for chap in self.page.livret.chapitres_a_ranger.liste_chapitres if (not chap.numero_fixe) and (chap.longueur > 0)]
                if len(self.page.liste_colonnes) in (2,4):
                        liste_chapitres_a_tester = [a for a in liste_chapitres_a_tester if a not in [chap_double for chap_double in self.page.livret.chapitres_a_ranger.liste_chapitres if chap_double.double_colonne]]

            if len(liste_chapitres_a_tester) == 0:
                return

            # Test si impossibilité de placer le numéro fixe à cause de numéros interdits
            if liste_chapitres_a_tester[0].numero_fixe and liste_chapitres_a_tester[0].ref in self.page.liste_numeros_interdits:
                liste_reduite : list[str] = self.page.liste_numeros_interdits
                for chap in [chap for chap in self.page.livret.get_chapitres_places() if (chap.numero_fixe or chap.prioritaire) and liste_chapitres_a_tester[0].ref in chap.suites]:
                    for suite in chap.suites:
                        if suite in self.page.liste_numeros_interdits:
                            liste_reduite.remove(suite)
                if liste_chapitres_a_tester[0].ref in liste_reduite:
                    return liste_chapitres_a_tester[0]

            # Test si au moins 1 chapitre plaçable
            if not any((self.tester([chap], False) for chap in liste_chapitres_a_tester)):
                return
            
            
            # Test si numéro fixe impossible car conflit colonne double/simple
            if self.tester_si_prochain_chapitre_est_fixe() and liste_chapitres_a_tester[0].double_colonne and len(self.page.liste_colonnes) in (2,4):
                return

            if self.page.livret.chapitres_a_ranger.est_vide():
                return
            
            for chapitre in liste_chapitres_a_tester:
                if self.tester([chapitre]):
                    self.recevoir(chapitre)
                    return

            exit = False
            if settings["nombre_chapitres_par_colonne"] >= 4 or (settings["nombre_chapitres_par_colonne"] > 3 and len(self.page.livret.liste_pages) > self.page.livret.bascule):
                if not any((self.tester_si_prochain_chapitre_est_fixe(),
                            self.tester_si_prochain_chapitre_est_fixe(1),
                            self.tester_si_prochain_chapitre_est_fixe(2),
                            self.tester_si_prochain_chapitre_est_fixe(3))):
                    for chapitre in liste_chapitres_a_tester:
                        chap1_ttk.set("Chapitre 1: " + chapitre.ref)
                        pg2["value"] = int(liste_chapitres_a_tester.index(chapitre)/len(liste_chapitres_a_tester)*100)
                        root.update_idletasks()
                        if exit:
                            break
                        if not self.tester([chapitre], False):
                            continue
                        for i, chapitre2 in enumerate(liste_chapitres_a_tester):
                            chap2_ttk.set("Chapitre 2: " + chapitre2.ref)
                            root.update_idletasks()
                            if exit:
                                break
                            if chapitre == chapitre2:
                                continue
                            if not self.tester([chapitre, chapitre2], False):
                                continue
                            for j, chapitre3 in enumerate(liste_chapitres_a_tester[i:]):
                                chap3_ttk.set("Chapitre 3: " + chapitre3.ref)
                                root.update_idletasks()
                                if exit:
                                    break
                                if len(set((chapitre, chapitre2, chapitre3))) != len(list((chapitre, chapitre2, chapitre3))):
                                    continue
                                if not self.tester([chapitre, chapitre2, chapitre3], False):
                                    continue
                                for chapitre4 in liste_chapitres_a_tester[i+j:]:
                                    chap4_ttk.set("Chapitre 4: " + chapitre4.ref)
                                    root.update_idletasks()
                                    if self.tester([chapitre, chapitre2, chapitre3, chapitre4]) and len(set((chapitre, chapitre2, chapitre3, chapitre4))) == len(list((chapitre, chapitre2, chapitre3, chapitre4))):
                                        self.recevoir(chapitre)
                                        if self.tester_si_prochain_chapitre_est_fixe():
                                            exit = True
                                            break
                                        self.recevoir(chapitre2)
                                        if self.tester_si_prochain_chapitre_est_fixe():
                                            exit = True
                                            break
                                        self.recevoir(chapitre3)
                                        if self.tester_si_prochain_chapitre_est_fixe():
                                            exit = True
                                            break
                                        self.recevoir(chapitre4)
                                        return
                if exit:
                    break     

            if settings["nombre_chapitres_par_colonne"] > 2:                   
                if not any((self.tester_si_prochain_chapitre_est_fixe(),
                            self.tester_si_prochain_chapitre_est_fixe(1),
                        self.tester_si_prochain_chapitre_est_fixe(2))):
                    for chapitre in liste_chapitres_a_tester:
                        chap1_ttk.set("Chapitre 1: " + chapitre.ref)
                        pg2["value"] = int(liste_chapitres_a_tester.index(chapitre)/len(liste_chapitres_a_tester)*100)
                        root.update_idletasks()
                        if exit:
                            break
                        if not self.tester([chapitre], False):
                            continue
                        for chapitre2 in liste_chapitres_a_tester:
                            chap2_ttk.set("Chapitre 2: " + chapitre2.ref)
                            root.update_idletasks()
                            if exit:
                                break
                            if chapitre == chapitre2:
                                continue
                            if not self.tester([chapitre, chapitre2], False):
                                continue
                            for chapitre3 in liste_chapitres_a_tester:
                                chap3_ttk.set("Chapitre 3: " + chapitre3.ref)
                                root.update_idletasks()
                                if self.tester([chapitre, chapitre2, chapitre3]) and len(set((chapitre, chapitre2, chapitre3))) == len(list((chapitre, chapitre2, chapitre3))):
                                    self.recevoir(chapitre)
                                    if self.tester_si_prochain_chapitre_est_fixe():
                                        exit = True
                                        break
                                    self.recevoir(chapitre2)
                                    if self.tester_si_prochain_chapitre_est_fixe():
                                        exit = True
                                        break

                                    self.recevoir(chapitre3)
                                    return
                if exit:
                    break

            if not self.tester_si_prochain_chapitre_est_fixe(1):
                for chapitre in liste_chapitres_a_tester:
                    for chapitre2 in ([a for a in self.page.livret.chapitres_a_ranger.liste_chapitres if not a.numero_fixe or ((len(self.page.liste_colonnes) in (2,4)) and a.double_colonne)]):
                        if self.tester([chapitre, chapitre2]) and chapitre != chapitre2:
                            self.recevoir(chapitre)
                            self.recevoir(chapitre2)
                            return

            for chapitre in liste_chapitres_a_tester:
                if self.tester([chapitre], cas_parfait=False):
                    self.recevoir(chapitre)
                    break
            if compteur_boucle > 1000:
                messagebox.showerror("Erreur Boucle infinie", f"Impossible de placer {self.page.livret.get_numero_prochain_chapitre()}. Il reste à placer {[chap.ref for chap in self.page.livret.chapitres_a_ranger.liste_chapitres]} ") #type: ignore
                raise NotImplementedError("Boucle infinie")



class Page:
    def __init__(self, livret : "Livret"):
        self.liste_colonnes: list[Colonne] = []
        self.livret = livret
        self.liste_numeros_interdits: list[str] = []
        self.liste_numeros_interdits_par_fixe: list[str] = []
        self.pages_recommencees : int = 0
        
    def __str__(self):
        retour = ""
        for col in self.liste_colonnes:
            retour += col.__repr__()
            retour += "\n"
        return "\n".join([colonne.__str__() for colonne in self.liste_colonnes])

    def recommencer_page(self, chapitre_a_mettre: Chapitre):
        liste_chapitres_fixes: list[Chapitre] = [chapitre_a_mettre]
        self.liste_numeros_interdits = list()
        for colonne in self.liste_colonnes:
            for chapitre in colonne.liste_chapitres:
                if chapitre.numero_fixe:
                    liste_chapitres_fixes.append(chapitre)
                self.livret.chapitres_a_ranger.liste_chapitres.append(chapitre)
        for chap_fixe in liste_chapitres_fixes:
            self.liste_numeros_interdits_par_fixe.extend([chap for chap in chap_fixe.chapitres_lies if chap not in [chap.ref for chap in liste_chapitres_fixes]])
        self.liste_numeros_interdits_par_fixe = list(set(self.liste_numeros_interdits_par_fixe))
        temp: list[str] = list()
        for ref_chap_fixe in self.liste_numeros_interdits_par_fixe:
            temp.extend(self.livret.get_chapitre(ref_chap_fixe).suites)
        self.liste_numeros_interdits_par_fixe.extend(temp)
            
        
        self.liste_colonnes = []
        self.pages_recommencees += 1
        if self.pages_recommencees > 1000:
            messagebox.showerror("Erreur Boucle infinie", f"Impossible de placer {self.livret.get_numero_prochain_chapitre()}. Il reste à placer {[chap.ref for chap in self.livret.chapitres_a_ranger.liste_chapitres]} ") #type: ignore
            raise NotImplementedError("Boucle infinie")

        
    def remplir(self) -> None:
        if len(self.livret.liste_pages) == 1 and settings["commencer_page_droite"]:
            for _ in range(int(settings["nombre_colonnes_par_page"] / 2)):
                self.liste_colonnes.append(Colonne(self))
        while len(self.liste_colonnes) < settings["nombre_colonnes_par_page"]:
            self.liste_colonnes.append(Colonne(self))
            chapitre_fixe_implacable = self.liste_colonnes[-1].remplir()
            if isinstance(chapitre_fixe_implacable, Chapitre):
                self.recommencer_page(chapitre_fixe_implacable)

    def get_chapitres_places(self) -> list[Chapitre]:
        liste_chapitres:list[Chapitre] = list()
        for colonne in self.liste_colonnes:
            liste_chapitres.extend(colonne.liste_chapitres)
        return liste_chapitres


class Livret:
    def __init__(self, chapitres_a_ranger : ChapitresARanger, numero_livret: int) -> None:
        self.numero_livret = numero_livret
        self.liste_pages : list[Page] = []
        self.chapitres_a_ranger = chapitres_a_ranger
        self.chapitres_a_ranger.livret = self
        self.quantite_pages_moyenne : int = math.ceil(len(self.chapitres_a_ranger.liste_chapitres) / settings["nombre_chapitres_par_colonne"])
        self.bascule : int = self.quantite_pages_moyenne - int(self.quantite_pages_moyenne * (settings["nombre_chapitres_par_colonne"] % 1))


    def get_numero_prochain_chapitre(self) -> int:
        liste_chap : set[Chapitre] = set()
        for page in self.liste_pages:
            for colonne in page.liste_colonnes:
                for chapitre in colonne.liste_chapitres:
                    liste_chap.add(chapitre)
        return len(liste_chap) + self.chapitres_a_ranger.numero_premier_chapitre
    
    def get_num_cible(self, ref: str) -> str:
        for chapitre in self.get_chapitres_places():
            if chapitre.ref == ref:
                return chapitre.numero_cible(chapitre)
        return "9999"
    
    def get_chapitres_places(self) -> list[Chapitre]: 
        all_chap: list[Chapitre] = list()
        for page in self.liste_pages:
            for colonne in page.liste_colonnes:
                for chap in colonne.liste_chapitres:
                    all_chap.append(chap)
        return all_chap
    
    def get_all_chapitres(self) -> list[Chapitre]:
        all_chap = self.get_chapitres_places()
        all_chap.extend(self.chapitres_a_ranger.liste_chapitres)
        return all_chap
    
    def get_chapitre(self, ref: str) -> Chapitre:
        return next((chap for chap in self.get_all_chapitres() if chap.ref == ref))

    def remplir(self):
        while not self.chapitres_a_ranger.est_vide():
            self.liste_pages.append(Page(self))
            self.liste_pages[-1].remplir()
            if all([len(colonne.liste_chapitres) == 0 for colonne in self.liste_pages[-1].liste_colonnes]):
                messagebox.showerror("Erreur Boucle infinie", f"Impossible de placer {self.get_numero_prochain_chapitre()}. Il reste à placer {[chap.ref for chap in self.chapitres_a_ranger.liste_chapitres]} ") #type: ignore
                raise NotImplementedError("Boucle infinie")




    def sauver(self):
        adresse_livret_range, _ = os.path.splitext(self.chapitres_a_ranger.adresse_fichie_source)
        contenu_livret_range = """
<html>
    <head>
    <meta charset="utf-8"> 
        <style>
            .colonne {
                width: 120px;
                background-color: whitesmoke;
                margin: 10px;
                min-height: 30 px;
                float: left;
            }
            .chapitre {

                width: 100px;
                background-color: rgb(187, 233, 255);
                vertical-align: middle;
                margin: 10px;
            }
            .fixe {
                background-color: #ffeea1;
            }
            .new_number {

            }
            .old_number {
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        """
        for numero_page, page in enumerate(self.liste_pages):
            contenu_livret_range += "<div>"
            contenu_livret_range += f"<div style='clear: both'>Double page {numero_page*2}-{numero_page*2 + 1}"+ "</div>"
            for colonne in page.liste_colonnes:
                contenu_livret_range += """
        <div class="colonne">"""
                for chapitre in colonne.liste_chapitres:
                    contenu_livret_range += f'<div class="{"chapitre fixe" if chapitre.numero_fixe else "chapitre"}" style="height: {chapitre.longueur/290*600}px"><span class="old_number">{chapitre.ref}</span> → <span class="new_number">{chapitre.numero_cible(chapitre)}</span><br><span>Allez à {", ".join((self.get_num_cible(ref) for ref in chapitre.suites))}</span></div>\n'
                contenu_livret_range += "</div>"
            contenu_livret_range += "</div>"
        contenu_livret_range += """
    </body>
</html>
        """
        with codecs.open(adresse_livret_range + "_organise.html", "w+", "utf-8") as f:
            f.write(contenu_livret_range)

        with open(adresse_livret_range + "_organise_compte-rendu.csv", "w", newline = '') as csvfile:
            fieldnames = ['livret', 'ancien', 'nouveau']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")

            writer.writeheader()

            for row in self.chapitres_a_ranger.compte_rendu:
                writer.writerow({'livret': row["livret"], 'ancien': row["ancien"], 'nouveau': row["nouveau"]})
            for numero_page, page in enumerate(self.liste_pages):
                for colonne in page.liste_colonnes:
                    for chapitre in colonne.liste_chapitres:
                        writer.writerow({'livret': self.numero_livret, 'ancien': chapitre.ref, 'nouveau': chapitre.numero_cible(chapitre)})


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Organise mon livret')
    root.resizable(False, False)
    
    com_page_droite = tk.BooleanVar(value=True)
    long_max_col = tk.IntVar()
    long_max_col.set(263)
    cr_address = tk.StringVar()
    source_address = tk.StringVar()
    numero_livret = tk.IntVar()
    gach_aut = tk.IntVar()
    gach_aut.set(3)
    nb_col_page = tk.IntVar()
    nb_col_page.set(4)
    nb_chap_col = tk.DoubleVar()
    nb_chap_col.set(3.0)
    num_prem_chap = tk.IntVar()
    num_prem_chap.set(0)
    melanger_chap = tk.BooleanVar()
    interdire_spoil_strict = tk.BooleanVar(value=True)
    settings = {
        "commencer_page_droite": False,
        "interdire_spoil_strict": True,
        "longueur_max_colonne": 263,
        "gachi_autorise": 3,
        "nombre_colonnes_par_page":  4,
        'melanger_chap': False,
        "nombre_chapitres_par_colonne": 3.0,
        "num_prem_chap": 0
    }
    def mmain():
        settings["commencer_page_droite"] = com_page_droite.get()
        settings["longueur_max_colonne"] = long_max_col.get()
        settings["gachi_autorise"] = gach_aut.get()
        settings["nombre_colonnes_par_page"] = nb_col_page.get()
        settings["nombre_chapitres_par_colonne"] = nb_chap_col.get()
        settings["melanger_chap"] = melanger_chap.get()
        settings["interdire_spoil_strict"] = interdire_spoil_strict.get()
        settings["num_prem_chap"] = num_prem_chap.get()

        chapitres_a_ranger = ChapitresARanger(cr_address.get().strip('"'))
        livret = Livret(chapitres_a_ranger, numero_livret.get())

        lf_livret.grid_remove()
        lf_mise_en_page.grid_remove()
        lf_obsolete.grid_remove()
        convert_button.grid_remove()

        ttk.Label(root, text="Avancement principal").pack(fill="x", expand=True, padx=10, pady=(10, 0))
        pg.pack(padx=10, pady=10, fill='x', expand=True)
        ttk.Label(root, text="Avancement secondaire").pack(fill="x", expand=True, padx=10, pady=(10, 0))
        pg2.pack(padx=10, pady=10, fill='x', expand=True)
        num_ttk.set("")
        ttk.Label(root, textvariable=num_ttk).pack(fill="x", expand=True, padx=10, pady=10)
        chap1_ttk.set("")
        ttk.Label(root, textvariable=chap1_ttk).pack(fill="x", expand=True, padx=10)
        chap2_ttk.set("")
        ttk.Label(root, textvariable=chap2_ttk).pack(fill="x", expand=True, padx=10)
        chap3_ttk.set("")
        ttk.Label(root, textvariable=chap3_ttk).pack(fill="x", expand=True, padx=10)
        chap4_ttk.set("")
        ttk.Label(root, textvariable=chap4_ttk).pack(fill="x", expand=True, padx=10, pady=(0,10))

        livret.chapitres_a_ranger.update_spoil_strict()
        livret.remplir()
        livret.sauver()
        for page in livret.liste_pages:
            chapitres_de_la_page:list[Chapitre] = list()
            for colonne in page.liste_colonnes:
                for chapitre in colonne.liste_chapitres:
                    chapitres_de_la_page.append(chapitre)
            chapitres_de_la_page = list(set(chapitres_de_la_page))
            for i, chapitre1 in enumerate(chapitres_de_la_page):
                for chapitre2 in chapitres_de_la_page[i:]:
                    if chapitre1.ref in chapitre2.chapitres_lies or chapitre1.ref in chapitre2.spoil_strict:
                        messagebox.showerror("Erreur", f"Spoil entre les chapitres {chapitre1.ref} et {chapitre2.ref}") #type: ignore
                        print(f"Problème {chapitre1.ref} et {chapitre2.ref}")
        root.destroy()

    def button_cr():
        cr_address.set(filedialog.askopenfilename(initialdir = os.getcwd(), title = "Sélectionnez un fichier", filetypes = (("Text files", "*.txt *.csv *.json"), ("all files", "*.*"))))
    def button_source():
        source_address.set(filedialog.askopenfilename(initialdir = os.getcwd(), title = "Sélectionnez un fichier", filetypes = (("Text files", "*.txt *.csv *.json"), ("all files", "*.*"))))

    PAD = {"padx": 20, "pady": 20, "ipady": 10}
    INDV = {"sticky": tk.EW, "padx": 10}

    lf_livret = ttk.LabelFrame(root, text="Livret")
    for row in range(5):
        lf_livret.rowconfigure(index=row, weight=1)
    ttk.Label(lf_livret, text="Numero du livret").grid(row=0, column=0, **INDV) #type: ignore
    ttk.Entry(lf_livret, textvariable = numero_livret).grid(row=0, column=1, **INDV) #type: ignore
    ttk.Label(lf_livret, text="Numéro premier chapitre").grid(row=1, column=0, **INDV) #type: ignore
    ttk.Entry(lf_livret, textvariable = num_prem_chap).grid(row=1, column=1, **INDV) #type: ignore
    ttk.Label(lf_livret, text="Chapitres par colonne").grid(row=2, column=0, **INDV) #type: ignore
    tk.Scale(lf_livret, variable = nb_chap_col, from_=3.0, to=4.0, orient="horizontal", resolution=0.1).grid(row=2, column=1, **INDV) #type: ignore
    ttk.Label(lf_livret, text="Source").grid(row=3, column=0, **INDV) #type: ignore
    ttk.Entry(lf_livret, textvariable = source_address).grid(row=3, column=1, **INDV) #type: ignore
    ttk.Button(lf_livret, text="Choisir…", command=button_source).grid(row=3, column=2, **INDV) #type: ignore
    ttk.Label(lf_livret, text="Compte Rendu").grid(row=4, column=0, **INDV) #type: ignore
    ttk.Entry(lf_livret, textvariable = cr_address).grid(row=4, column=1, **INDV) #type: ignore
    ttk.Button(lf_livret, text="Choisir…", command=button_cr).grid(row=4, column=2, **INDV) #type: ignore
    lf_livret.grid(row=0, column=0, sticky=tk.N, padx=(20,0), pady=(20,0))

    lf_mise_en_page = ttk.LabelFrame(root, text="Mise en page")
    for row in range(4):
        lf_mise_en_page.rowconfigure(index=row, weight=1)
    ttk.Checkbutton(lf_mise_en_page,
                text='Commencer par la page de droite',
                variable=com_page_droite,
                onvalue= True,
                offvalue= False).grid(row=0, column=0, columnspan=2, **INDV) #type: ignore
    ttk.Label(lf_mise_en_page, text="Nombre de colonnes par double page").grid(row=1, column=0, **INDV) #type: ignore
    ttk.Entry(lf_mise_en_page, textvariable = nb_col_page).grid(row=1, column=1, **INDV) #type: ignore
    ttk.Label(lf_mise_en_page, text="Longueur maximum des colonnes (mm)").grid(row=2, column=0, **INDV) #type: ignore
    ttk.Entry(lf_mise_en_page, textvariable = long_max_col).grid(row=2, column=1, **INDV) #type: ignore
    ttk.Label(lf_mise_en_page, text="Gachi autorise (mm)").grid(row=3, column=0, **INDV) #type: ignore
    ttk.Entry(lf_mise_en_page, textvariable = gach_aut).grid(row=3, column=1, **INDV) #type: ignore
    lf_mise_en_page.grid(row=0, column=1, sticky=tk.N, **PAD) #type: ignore

    lf_obsolete = ttk.LabelFrame(root, text="Obsolète")
    for row in range(2):
        lf_obsolete.rowconfigure(index=row, weight=1)
    ttk.Checkbutton(lf_obsolete,
                text='Mise en page avec ordre aléatoire',
                variable=melanger_chap,
                onvalue= True,
                offvalue= False).grid(row=0, column=0, **INDV) #type: ignore
    ttk.Checkbutton(lf_obsolete,
                text='Interdire spoil niveau strict',
                variable=interdire_spoil_strict,
                onvalue= True,
                offvalue= False).grid(row=1, column=0, **INDV) #type: ignore
    lf_obsolete.grid(row=1, column=0, sticky=tk.EW, padx=(20,0), pady=20, ipady=10)
    
    # convert button
    convert_button = ttk.Button(root, text='Go !', width=30)
    convert_button.grid(row=1, column=1, sticky=tk.SE, padx=20, pady=20)
    convert_button.configure(command=mmain)

    pg = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=100)
    pg2 = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=100)
    num_ttk = tk.StringVar()
    chap1_ttk = tk.StringVar()
    chap2_ttk = tk.StringVar()
    chap3_ttk = tk.StringVar()
    chap4_ttk = tk.StringVar()




    
    root.mainloop()
