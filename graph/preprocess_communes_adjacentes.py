import pandas as pd
import sys

# 1er argument : fichier brut en entrée 
# (entier ou extrait de : https://www.data.gouv.fr/fr/datasets/liste-des-adjacences-des-communes-francaises/)
# 
# 2e argument : fichier en sortie, à 2 colonne (un code insee, un code insee voisin)
file_communes_voisines_ini = sys.argv[1]
file_communes_voisines_new = sys.argv[2]

voisins_brut = pd.read_csv(file_communes_voisines_ini,
                           sep = ',',
                           header = 0)

print(voisins_brut)


print("--- découpage de la liste des codes communes voisines\n")

print("--- état avant :")
print(voisins_brut['insee'],voisins_brut['insee_voisins'])

voisins_brut['insee_voisins']=voisins_brut['insee_voisins'].apply(lambda aa: aa.split('|'))

print("--- état après :")
print(voisins_brut['insee'],voisins_brut['insee_voisins'])

print("--- fin découpage de la liste des codes communes voisines\n")



print("--- création du fichier de sortie simplifié \"code insee , code insee voisin\"\n")
with open(file_communes_voisines_new,'w') as fileout:

    # entête du fichier : le nom des 2 colonnes
    print('insee_origine,insee_destination')

    # parcours de l'ensemble des lignes du dataframe
    for row in voisins_brut.itertuples():
        # pour chacun des codes insee dans la liste en colonne 4
        for c in row[4]:
            # chaque paire de codes insee est écrit sur 5 caractères, avec des 0 devant si besoin
            print('{},{}'.format(str(row[1]).zfill(5),str(c).zfill(5)),file=fileout)


print("--- fin de création du fichier de sortie simplifié")



