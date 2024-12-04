class RAM:
    
    def __init__(self, indice, nbits):
        self.indice = indice
        self.nbits = nbits

        self.bits = [0] * 2 ** nbits