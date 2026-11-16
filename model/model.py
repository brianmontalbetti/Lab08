from database.distributore_DAO import DistributoreDAO
from model.distributore_DTO import Distributore

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        risultati = []
        # Ciclo su tutti i distributori caricati nel Model (A e B)
        for distributore in self._distributori:
            # Recupero tutti i prezzi dell'anno di quel distributore tramite il suo metodo ORM
            prezzi = distributore.get_prezzi()
            if prezzi:
                # Filtro solo i prezzi che appartengono al mese selezionato (p.data.month == mese)
                prezzi_mese = []
                for p in prezzi:
                    if p.data.month == mese:
                        prezzi_mese.append(p.prezzo_litro)
                # Calcolo la media aritmetica (evitando la divisione per zero se la lista fosse vuota)
                media = sum(prezzi_mese) / len(prezzi_mese) if prezzi_mese else 0.0
            else:
                media = 0.0
            # Salvo la tupla formattata come richiede il Controller (nome, media arrotondata a 3 decimali)
            risultati.append((distributore.nome, round(media, 3)))
        return risultati


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)
        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)


    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # 🟢 A:
        # Ho già scelto il distributore per tutti i 7 giorni (da giorno 1 a giorno 7),
        # quindi alla chiamata successiva giorno vale 8.
        if giorno > 7:
            # Controllo se ho trovato una sequenza migliore di quella salvata finora
            # (self.__costo_ottimo == -1 indica che questa è la prima sequenza completa che trovo)
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                # Salvo una copia indipendente della lista con .copy() (senza importare nulla):
                # mi serve una copia perché poi il backtracking svuoterà sequenza_parziale.
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        for distributore in self._distributori:
            # 🔵 B:
            # [giorno - 1] perché giorno parte da 1 (fino a 7), mentre gli indici delle liste partono da 0 (fino a 6).
            prezzo_giorno = prezzi_settimana[distributore.id][giorno - 1]
            costo_rifornimento = prezzo_giorno * 100  # Rifornisco sempre 100 litri

            # Calcolo l'eventuale costo fisso di spostamento (5 €):
            # Lo pago solo se non sono al primo giorno (ultimo_distributore is not None)
            # E se oggi scelgo un distributore diverso da quello di ieri (distributore.id != ultimo_distributore).
            costo_spostamento = 0
            if ultimo_distributore is not None and distributore.id != ultimo_distributore:
                costo_spostamento = 5

            nuovo_costo = costo_corrente + costo_rifornimento + costo_spostamento

            # 🟡 C:
            # Siccome i costi si sommano e sono sempre positivi, se nuovo_costo è già maggiore o uguale
            # al miglior costo trovato finora, taglio il ramo e non scendo ulteriormente.
            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:
                # Aggiungo l'id del distributore scelto alla sequenza parziale
                sequenza_parziale.append(distributore.id)
                # Chiamo ricorsivamente per il giorno successivo (giorno + 1), passando il distributore appena usato
                # come nuovo ultimo_distributore e aggiornando il costo accumulato
                self.__ricorsione(sequenza_parziale, giorno + 1, distributore.id, nuovo_costo, prezzi_settimana)
                # 🟣 D:
                # Appena torno indietro dalla chiamata ricorsiva, rimuovo l'ultimo elemento aggiunto
                # così la lista torna pulita per provare il distributore successivo nel ciclo for.
                sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            prezzi_mese = []
            for p in prezzi:
                if p.data.month == mese:
                    prezzi_mese.append(p)
            prezzi_mese.sort(key=lambda p: p.data)

            primi_7_prezzi = []
            for p in prezzi_mese[:7]:
                primi_7_prezzi.append(p.prezzo_litro)

            prezzi_settimana[distributore.id] = primi_7_prezzi
        return prezzi_settimana