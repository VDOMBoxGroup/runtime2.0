"""Ecrire le corps d'une reponse sur la socket, par blocs bornes.

`shutil.copyfileobj` lit `shutil.COPY_BUFSIZE` d'un coup, et cette constante
vaut **un mebioctet sous Windows** contre 64 Kio ailleurs. Un fichier de 984 Ko
partait donc en une seule lecture et une seule ecriture de 984 200 octets.

Mesure sur ce serveur, la meme a chaque fois : 978 944 octets arrivaient chez le
client - exactement 239 x 4096 - puis plus rien, et la connexion tombait 19 s
plus tard. Quatre essais sur cinq, toujours au meme octet, avec ou sans
HTTP/1.1 : le protocole n'y est pour rien. Le chemin WebDAV du meme serveur, qui
ecrit par blocs de 64 Kio, sert deux mebioctets sans broncher.

Ce qui rendait le defaut couteux n'est pas la coupure mais le **silence** : le
serveur annoncait 984 200 octets, en livrait moins, et personne ne le disait
nulle part. Le client concluait a une panne reseau, le journal du serveur ne
portait rien, et un fichier tronque s'installait dans le cache du navigateur.
D'ou le controle ci-dessous, qui parle.
"""

BLOC = 65536


def ecrire_par_blocs(source, sortie, annonce=None, ou="", tracer=None):
    """Copie `source` dans `sortie` par blocs. Rend le nombre d'octets ecrits.

    `annonce` est la taille dite au client, quand on la connait : une source qui
    s'arrete avant doit laisser une trace, pas un blanc. `tracer` est la fonction
    de journalisation a employer - `debug` chez l'appelant - parce que ce module
    ne doit pas dependre de la sienne.
    """
    ecrits = 0
    try:
        while True:
            bloc = source.read(BLOC)
            if not bloc:
                break
            sortie.write(bloc)
            ecrits += len(bloc)
    except Exception as erreur:
        if tracer:
            tracer("Reponse interrompue apres %d octets sur %s: %s: %s"
                   % (ecrits, ou, type(erreur).__name__, erreur))
        raise

    if annonce is not None and ecrits != annonce and tracer:
        tracer("CORPS TRONQUE sur %s : %d octets ecrits pour %d annonces "
               "(la source s'est arretee avant la fin)" % (ou, ecrits, annonce))
    return ecrits
