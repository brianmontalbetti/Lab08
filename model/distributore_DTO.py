from dataclasses import dataclass
from database import prezzo_DAO
from database.prezzo_DAO import PrezzoDAO

'''
    DTO (Data Transfer Object) dell'entità Distributore
'''

@dataclass()
class Distributore:
    id: int
    nome: str
    indirizzo: str

    # RELAZIONI
    lista_prezzi: list = None

    def get_prezzi(self):
        """ Aggiorna e Restituisce la lista di prezzi (self.lista_prezzi) associati al distributore"""
        # Controllo se ho già scaricato i prezzi di questo distributore dal DB.
        # Se lista_prezzi è None, è la prima volta che mi servono: chiamo il DAO e li salvo.
        if self.lista_prezzi is None:
            self.lista_prezzi = PrezzoDAO.get_prezzi(self.id)
        # Se invece li avevo già scaricati in precedenza, li restituisco subito dalla memoria
        # senza rifare una query al database (tecnica del "lazy loading").
        return self.lista_prezzi

    def __eq__(self, other):
        return isinstance(other, Distributore) and self.id == other.id

    def __str__(self):
        return f"{self.id} | {self.nome} | Indirizzo: {self.indirizzo}"

    def __repr__(self):
        return f"{self.id} | {self.nome} | Indirizzo: {self.indirizzo}"
