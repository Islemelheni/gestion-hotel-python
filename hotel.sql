DROP TABLE IF EXISTS Reservation;
DROP TABLE IF EXISTS Chambre;
DROP TABLE IF EXISTS Client;

CREATE TABLE Client (
    id_client INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    telephone TEXT NOT NULL
);

CREATE TABLE Chambre (
    num_chambre INTEGER PRIMARY KEY,
    type TEXT CHECK(type IN ('simple','double','suite')),
    prix_nuit REAL NOT NULL,
    statut TEXT CHECK(statut IN ('libre','occupée'))
);

CREATE TABLE Reservation (
    id_res INTEGER PRIMARY KEY AUTOINCREMENT,
    id_client INTEGER NOT NULL,
    num_chambre INTEGER NOT NULL,
    date_debut TEXT NOT NULL,
    date_fin TEXT NOT NULL,
    FOREIGN KEY (id_client) REFERENCES Client(id_client),
    FOREIGN KEY (num_chambre) REFERENCES Chambre(num_chambre)
);
