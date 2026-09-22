import numpy as np
import matplotlib.pyplot as plt
import math
import os
import sys
from typing import List, Tuple, Optional


class InterpolationEngine:
    def __init__(self, x: List[float], y: List[float]):
        if len(x) != len(y):
            raise ValueError("Длины массивов X и Y должны совпадать.")
        if len(x) < 3:
            raise ValueError("Требуется минимум 3 точки для интерполяции.")
        
        self.x = np.array(x, dtype=float)
        self.y = np.array(y, dtype=float)
        idx = np.argsort(self.x)
        self.x, self.y = self.x[idx], self.y[idx]
        self.n = len(self.x)
        
        h_vals = np.diff(self.x)
        self.h = h_vals[0]
        if np.max(np.abs(h_vals - self.h)) > 1e-7:
            print("Внимание: сетка неравномерна. Методы конечных разностей/Гаусса могут давать погрешность.")
            self.is_uniform = False
        else:
            self.is_uniform = True
            
        self.dd_table = self._build_finite_diff_table()

    def _build_finite_diff_table(self) -> np.ndarray:
        dd = np.zeros((self.n, self.n))
        dd[:, 0] = self.y
        for j in range(1, self.n):
            for i in range(self.n - j):
                dd[i, j] = dd[i+1, j-1] - dd[i, j-1]
        return dd

    def print_table(self):
        print("ТАБЛИЦА КОНЕЧНЫХ РАЗНОСТЕЙ")
        header = f"{'i':>3} | {'x_i':>8} | {'y_i':>10}"
        for j in range(1, self.n):
            header += f" | {'Δ'+str(j)+'y':>8}"
        print(header)
        print("-" * len(header))
        for i in range(self.n):
            row = f"{i:>3} | {self.x[i]:>8.4f} | {self.dd_table[i,0]:>10.4f}"
            for j in range(1, self.n - i):
                row += f" | {self.dd_table[i,j]:>8.4f}"
            print(row)

    def lagrange(self, x_val: float) -> float:
        res = 0.0
        for i in range(self.n):
            term = self.y[i]
            for j in range(self.n):
                if i != j:
                    term *= (x_val - self.x[j]) / (self.x[i] - self.x[j])
            res += term
        return res

    def _binom(self, t: float, k: int) -> float:
        if k == 0: return 1.0
        res = 1.0
        for i in range(k):
            res *= (t - i) / (i + 1)
        return res

    def newton_forward(self, x_val: float) -> float:
        if not self.is_uniform: raise ValueError("Требуется равномерная сетка.")
        t = (x_val - self.x[0]) / self.h
        res = self.dd_table[0, 0]
        for k in range(1, self.n):
            res += self._binom(t, k) * self.dd_table[0, k]
        return res

    def newton_backward(self, x_val: float) -> float:
        if not self.is_uniform: raise ValueError("Требуется равномерная сетка.")
        t = (x_val - self.x[-1]) / self.h
        res = self.dd_table[-1, 0]
        for k in range(1, self.n):
            res += self._binom(t + k - 1, k) * self.dd_table[self.n - 1 - k, k]
        return res

    def newton(self, x_val: float) -> Tuple[float, str]:
        mid = (self.x[0] + self.x[-1]) / 2
        if x_val <= mid:
            return self.newton_forward(x_val), "Ньютон (вперёд)"
        else:
            return self.newton_backward(x_val), "Ньютон (назад)"

    def gauss_forward(self, x_val: float) -> float:
        if not self.is_uniform: 
            raise ValueError("Требуется равномерная сетка.")
        
        k = np.argmin(np.abs(self.x - x_val))
        # Защита: Гаусс требует центральных узлов, не используем крайние
        if k < 2 or k > self.n - 3:
            return self.lagrange(x_val)  # Резервный метод
        
        t = (x_val - self.x[k]) / self.h
        res = self.dd_table[k, 0]
        term = t
        
        for j in range(1, self.n):
            idx = k - (j + 1) // 2
            if idx < 0 or idx >= self.n - j: 
                break
            coeff = term / math.factorial(j)
            res += coeff * self.dd_table[idx, j]
            if j % 2 == 1:
                term *= (t - (j + 1) // 2)
            else:
                term *= (t + j // 2)
        return res

    def gauss_backward(self, x_val: float) -> float:
        if not self.is_uniform: 
            raise ValueError("Требуется равномерная сетка.")
        
        k = np.argmin(np.abs(self.x - x_val))
        if k < 2 or k > self.n - 3:
            return self.lagrange(x_val)
        
        t = (x_val - self.x[k]) / self.h
        res = self.dd_table[k, 0]
        term = t
        
        for j in range(1, self.n):
            idx = k - j // 2 - 1
            if idx < 0 or idx >= self.n - j: 
                break
            coeff = term / math.factorial(j)
            res += coeff * self.dd_table[idx, j]
            if j % 2 == 1:
                term *= (t + (j + 1) // 2)
            else:
                term *= (t - j // 2)
        return res

    def gauss(self, x_val: float) -> Tuple[float, str]:
        if x_val < self.x[0] or x_val > self.x[-1]:
            return self.lagrange(x_val), "Гаусс: экстраполяция (использован Лагранж)"
        k = np.argmin(np.abs(self.x - x_val))
        if x_val <= self.x[k]:
            return self.gauss_backward(x_val), "Гаусс (назад)"
        else:
            return self.gauss_forward(x_val), "Гаусс (вперёд)"

    def stirling(self, x_val: float) -> float:
        if not self.is_uniform: 
            raise ValueError("Требуется равномерная сетка.")
        
        k = np.argmin(np.abs(self.x - x_val))
        if k == 0: k = 1
        if k >= self.n - 1: k = self.n - 2
        
        t = (x_val - self.x[k]) / self.h
        
        if k > 0 and k < self.n - 1:
            res = self.dd_table[k, 0] + t * (self.dd_table[k, 1] + self.dd_table[k-1, 1]) / 2
        else:
            res = self.dd_table[k, 0]
        
        term = t**2
        for j in range(2, self.n):
            idx = k - j//2
            if idx < 0 or idx >= self.n - j:
                break
            val = self.dd_table[idx, j]
            if j % 2 == 0:
                res += (term / math.factorial(j)) * val
                term *= t**2 - (j//2)**2
            else:
                res += (t * term / math.factorial(j)) * val
                term *= t**2 - ((j+1)//2)**2
        return res

    def bessel(self, x_val: float) -> float:
        if not self.is_uniform: 
            raise ValueError("Требуется равномерная сетка.")
        
        k = np.argmin(np.abs(self.x - x_val))
        if k == 0: k = 1
        if k >= self.n - 1: k = self.n - 2
        
        t = (x_val - self.x[k]) / self.h - 0.5
     
        if k + 1 < self.n:
            res = (self.dd_table[k, 0] + self.dd_table[k+1, 0]) / 2 + t * self.dd_table[k, 1]
        else:
            res = self.dd_table[k, 0] + t * self.dd_table[k, 1]
        
        term = t**2 - 0.25
        for j in range(2, self.n):
            idx1, idx2 = k - j//2, k - j//2 + 1
            if 0 <= idx1 < self.n - j and 0 <= idx2 < self.n - j:
                val = (self.dd_table[idx1, j] + self.dd_table[idx2, j]) / 2
            elif 0 <= idx1 < self.n - j:
                val = self.dd_table[idx1, j]
            elif 0 <= idx2 < self.n - j:
                val = self.dd_table[idx2, j]
            else:
                break  
            res += (term / math.factorial(j)) * val
            term *= t**2 - (j//2 + 0.5)**2
        return res


def input_keyboard() -> Tuple[List[float], List[float], str]:
    print("\nВвод данных с клавиатуры (минимум 3 точки, формат: x y)")
    print("Пример: 2.10 3.7587 (пустая строка для завершения)")
    data = []
    while True:
        line = input("  > ").strip()
        if not line: break
        try:
            parts = line.replace(',', '.').split()
            if len(parts) < 2: continue
            x, y = float(parts[0]), float(parts[1])
            data.append((x, y))
        except ValueError:
            print("Некорректный формат. Введите два числа.")
    if len(data) < 3: raise ValueError("Введено менее 3 точек.")
    xs, ys = zip(*data)
    return list(xs), list(ys), "Ввод с клавиатуры"


def input_file(path: str) -> Tuple[List[float], List[float], str]:
    if not os.path.exists(path): 
        raise FileNotFoundError(f"Файл '{path}' не найден.")
    xs, ys = [], []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().replace(',', '.')
            if not line or line.startswith('#') or line.lower().startswith(('x', 'i', '№')): 
                continue
            try:
                parts = line.split()
                if len(parts) >= 2:
                    xs.append(float(parts[0]))
                    ys.append(float(parts[1]))
            except: 
                continue
    if len(xs) < 3: 
        raise ValueError("В файле менее 3 пар данных.")
    return xs, ys, f"Файл: {path}"


def input_function() -> Tuple[List[float], List[float], str]:
    funcs = {
        '1': (lambda x: np.sin(x), "sin(x)"),
        '2': (lambda x: 6*x/(x**4 + 5), "6x/(x^4 + 5)"),
        '3': (lambda x: np.exp(-x), "exp(-x)")
    }
    print("\nВыбор функции:")
    for k, (_, name) in funcs.items(): 
        print(f"  {k}. {name}")
    key = input("Номер (базовое: 2): ").strip() or "2"
    if key not in funcs: 
        raise ValueError("Неверный номер функции.")
    f, name = funcs[key]
    a = float((input("Начало интервала (a) (базовое: 0): ") or "0").replace(',', '.'))
    b = float((input("Конец интервала (b) (базовое: 2): ") or "2").replace(',', '.'))
    n = int(input("Количество точек (≥3) (базовое: 11): ") or "11")
    if n < 3: raise ValueError("Точек должно быть ≥3.")
    if a >= b: raise ValueError("a должно быть < b.")
    x = np.linspace(a, b, n)
    y = f(x)
    return x.tolist(), y.tolist(), f"Функция {name} [{a},{b}]"


def plot_interpolation(engine: InterpolationEngine, x_val: float, res_dict: dict, func_name: str = ""):
    plt.figure(figsize=(10, 6))
    plt.scatter(engine.x, engine.y, color='red', s=60, zorder=5, label='Узлы интерполяции')
    
    x_dense = np.linspace(engine.x[0]-0.2, engine.x[-1]+0.2, 500)
    
    if func_name == "sin(x)": 
        y_true = np.sin(x_dense)
    elif func_name == "6x/(x^4 + 5)": 
        y_true = 6*x_dense/(x_dense**4 + 5)
    elif func_name == "exp(-x)": 
        y_true = np.exp(-x_dense)
    else: 
        y_true = None
    
    if y_true is not None:
        plt.plot(x_dense, y_true, 'k--', linewidth=1, label='Истинная функция', alpha=0.6)
        
    y_poly = np.array([engine.lagrange(xi) for xi in x_dense])
    plt.plot(x_dense, y_poly, 'b-', linewidth=2, label='Интерполяционный многочлен')
    
    if x_val is not None:
        y_calc = engine.lagrange(x_val)
        plt.scatter([x_val], [y_calc], color='green', s=100, zorder=6, label=f'x={x_val}, P(x)={y_calc:.4f}')
        plt.axvline(x_val, color='green', linestyle=':', alpha=0.5)

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Интерполяция функции')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def main():
    
    while True:
        print("\nИсточник данных:")
        print("1. Ввести таблицу с клавиатуры")
        print("2. Загрузить из файла (.txt)")
        print("3. Сгенерировать из функции")
        print("4. Выход")
        
        try:
            choice = input("Ваш выбор (1-4) (базовое: 2): ").strip() or "2"
            if choice == '4': break
            if choice not in ['1','2','3']: 
                print("Неверный выбор.")
                continue
            
            if choice == '1': 
                x, y, src = input_keyboard()
            elif choice == '2': 
                p = input("Путь к файлу (базовое: data_var5.txt): ").strip() or "data_var5.txt"
                x, y, src = input_file(p)
            elif choice == '3': 
                x, y, src = input_function()
                
            engine = InterpolationEngine(x, y)
            engine.print_table()
            
            print("\nВычисление значения для заданного аргумента:")
            x_val_str = input("Введите X (базовое для вар.5: 2.112): ").strip() or "2.112"
            x_val = float(x_val_str.replace(',', '.'))
            
            results = {}
            methods = [
                ("Лагранж", engine.lagrange),
                ("Ньютон ", lambda x: engine.newton(x)[0]),
                ("Гаусс ", lambda x: engine.gauss(x)[0]),
                ("Стирлинг", engine.stirling),
                ("Бессель", engine.bessel)
            ]
            
            print(f"\nРЕЗУЛЬТАТЫ ИНТЕРПОЛЯЦИИ ДЛЯ x = {x_val}")
            if x_val < engine.x[0] or x_val > engine.x[-1]:
                print(f" ВНИМАНИЕ: экстраполяция за пределы узлов [{engine.x[0]}, {engine.x[-1]}]")
            
            for name, func in methods:
                try:
                    res = func(x_val)
                    results[name] = res
                    print(f"{name:<15} | {res:>10.6f}")
                except Exception as e:
                    print(f"{name:<15} |  {e}")
                    results[name] = None
                    
            print("\nВсе методы интерполяции дают один и тот же полином. Расхождения вызваны погрешностью.")
            
            plot_choice = input("\nПостроить график? (y/n) (базовое: y): ").strip().lower() or "y"
            if plot_choice == 'y':
                plot_interpolation(engine, x_val, results, src)
                
        except KeyboardInterrupt:
            print("\nПрограмма остановлена.")
            break
        except Exception as e:
            print(f"\nОшибка: {e}. Попробуйте снова.")
            continue
            


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        sys.exit(0)