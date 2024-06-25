import time
import subprocess

def run_tests():
    start_time = time.time()

    result = subprocess.run(['pytest', '-n', '15'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nTiempo total de ejecución: {elapsed_time:.2f} segundos")
    
    print("\nSalida de pytest:")
    print(result.stdout.decode('utf-8'))
    print(result.stderr.decode('utf-8'))

if __name__ == "__main__":
    run_tests()