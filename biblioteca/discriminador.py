from .ram import RAM
class Discriminador:

    def __init__(self):
        self.rams = []

    def adicionar_ram(self, ram):
        self.rams.append(ram)

    def incluir_endereco(self, endereco):
        for i, end in enumerate(endereco):
            if i < len(self.rams):
                self.rams[i].bits[end] += 1
            else:
                print(f"Aviso: Endereço {end} não pôde ser incluído, RAM correspondente não encontrada.")

    def criar_e_adicionar_rams(self, total_bits, nBits):
        for i in range(total_bits):
            ram = RAM(indice=i + 1, nbits=nBits)
            self.adicionar_ram(ram)

    def imprimir_rams(self):
        for ram in self.rams:
            print("RAM: ", ram.indice)
            print("Array de Bits: ", ram.bits)
            print()

    def calcular_similaridade(self, discri_sol):
        similaridade_sol = 0
        total_rams = len(self.rams)
        rams_similares_sol = 0

        for i in range(total_rams):
            ram_roi = self.rams[i].bits
            ram_sol = discri_sol.rams[i].bits

            # Verificar se há alguma correspondência na RAM
            if any(ram_roi[j] != 0 and ram_sol[j] != 0 for j in range(len(ram_roi))):
                rams_similares_sol += 1

        similaridade_sol = (rams_similares_sol / total_rams) * 100

        print(f"SIMI SOL: {similaridade_sol:.1f}%")

        return similaridade_sol

    def comparar_rams(discri_teste, discri_sol, discri_fa):
        # Definindo o número de RAMs para comparar
        num_rams = 5
        for i in range(num_rams):
            ram_teste = discri_teste.rams[i].bits
            ram_sol = discri_sol.rams[i].bits
            ram_fa = discri_fa.rams[i].bits

            # Verificando se há algum número na mesma posição das RAMs
            for j in range(len(ram_teste)):
                if ram_teste[j] != 0 and ram_sol[j] != 0:
                    print(
                        f"Na RAM {i + 1} do discriminador SOL, há um número na mesma posição que na RAM do discriminador de teste.")
                if ram_teste[j] != 0 and ram_fa[j] != 0:
                    print(
                        f"Na RAM {i + 1} do discriminador FA, há um número na mesma posição que na RAM do discriminador de teste.")

    def limpar_rams(self):
        # Esvazia as RAMs (endereços)
        self.rams = []