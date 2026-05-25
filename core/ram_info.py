# from os import system
import psutil
class RamInfo:
    def __init__(self):
        self.factor = 1024
    def get_size(self, bytes, suffix='B'):
            for unit in ['','K','M','G','T','P']:
                if bytes < self.factor:
                    return f'{bytes:.2f}{unit}{suffix}'
                bytes /= self.factor

    def ram_info(self):
            # Get the swap memory details (if exists)
            system = psutil.virtual_memory()
            print(f'Total :{self.get_size(system.total)} ')
            print(f'Available :{self.get_size(system.available)}')
            print(f'Used :{self.get_size(system.used)}')
            print(f'Percentage :{system.percent}%')
            swap = psutil.swap_memory()
            print('\nSwap partition:')
            print(f'Total: {self.get_size(swap.total)}')
            print(f'Free: {self.get_size(swap.free)}')
            print(f'Used: {self.get_size(swap.used)}')
            print(f'Percentage: {swap.percent}%')
    def info(self):
        system = psutil.virtual_memory()
        return f"Total RAM: {self.get_size(system.total)}"
    
if __name__ == "__main__":
    RamInfo().ram_info()