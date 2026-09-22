import os
import numpy as np
import copy

def read_matrix():
    choice = ""
    while choice not in ["f", "k", "r"]:
        choice = input("Введите матрицу: f - файл, k - клавиатура, r - случайная: ").strip().lower()

    if choice == "f":
        file_path = input("Путь к файлу: ")
        while not os.path.isfile(file_path):
            file_path = input("Файл не найден. Введите путь снова: ")
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        n = int(lines[0])
        matrix = [list(map(float, line.split())) for line in lines[1:n+1]]
        
    elif choice == "k":
        n = int(input("Введите количество неизвестных(от 1 до 20): "))
        print("Введите коэффициенты при неизвестных и свободные члены в конце каждой строки")
        matrix = []
        for i in range(n):
            row = list(map(float, input().split()))
            while len(row) != n + 1:
                print(f"Ошибка: требуется {n+1} чисел. Повторите ввод строки {i+1}:")
                row = list(map(float, input().split()))
            matrix.append(row)
            
    else:  
        n = int(input("Введите количество неизвестных(от 1 до 20): "))
        import random
        matrix = [[random.uniform(-20, 20) for _ in range(n + 1)] for _ in range(n)]
        
    return matrix, n

def gauss_method(matrix, n):
    original_matrix = copy.deepcopy(matrix)
    swaps = 0

    for col in range(n - 1):
        max_row = col
        for row in range(col + 1, n):
            if abs(matrix[row][col]) > abs(matrix[max_row][col]):
                max_row = row
                
        if max_row != col:
            matrix[col], matrix[max_row] = matrix[max_row], matrix[col]
            swaps += 1
            
        pivot = matrix[col][col]
        if abs(pivot) < 1e-12:
            print("Матрица вырождена. Решение невозможно.")
            return None, None, None, 0

        for row in range(col + 1, n):
            factor = matrix[row][col] / pivot
            for k in range(col, n + 1):
                matrix[row][k] -= factor * matrix[col][k]

    det = (-1) ** swaps
    for i in range(n):
        det *= matrix[i][i]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        sum_known = sum(matrix[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (matrix[i][n] - sum_known) / matrix[i][i]

    residuals = []
    for i in range(n):
        val = sum(original_matrix[i][j] * x[j] for j in range(n)) - original_matrix[i][n]
        residuals.append(val)

    return matrix, x, residuals, det

def compare_with_numpy(matrix, n):
    A = [row[:n] for row in matrix]
    b = [row[n] for row in matrix]
    print("\nСравнение с библиотекой numpy:")
    try:
        x_np = np.linalg.solve(A, b)
        det_np = np.linalg.det(A)
        print("Решение системы:", *[f"{v:.10f}" for v in x_np])
        print(f"Определитель: det = {det_np:.5f}")
    except np.linalg.LinAlgError:
        print("det = 0")

def main():
    matrix, n = read_matrix()
    
    print("\nИсходная матрица:")
    for row in matrix:
        print(" ".join(f"{v:10.5f}" for v in row))

    tri_matrix, solution, residuals, det = gauss_method(copy.deepcopy(matrix), n)

    if tri_matrix is None:
        return

    print("\nРешение методом Гаусса:")
    for i, val in enumerate(solution):
        print(f"x[{i+1}]={val:.25f}")

    print("\nПреобразованная матрица:")
    for row in tri_matrix:
        print(" ".join(f"{v:10.5f}" for v in row))

    print(f"\nОпределитель: {det:.5f}")

    print("\nВектор невязки:")
    for i, val in enumerate(residuals):
        print(f"r[{i+1}]={val:.25f}")

    compare_with_numpy(tri_matrix, n)

if __name__ == "__main__":
    main()