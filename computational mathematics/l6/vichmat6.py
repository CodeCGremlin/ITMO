import numpy as np
import matplotlib.pyplot as plt
import math
import sys
from typing import Callable, Tuple, Optional, Dict

EPS_MIN = 1e-12
STEP_MIN = 1e-6
STEP_MAX = 10.0


def ode_variant5(x: float, y: float) -> float:
    return x + y

def ode_test1(x: float, y: float) -> float:
    return y

def ode_test2(x: float, y: float) -> float:
    return -2 * x * y

def ode_test3(x: float, y: float) -> float:
    return math.sin(x) + y


def exact_variant5(x: float, x0: float, y0: float) -> float:
    return (y0 + x0 + 1) * math.exp(x - x0) - x - 1

def exact_test1(x: float, x0: float, y0: float) -> float:
    return y0 * math.exp(x - x0)

def exact_test2(x: float, x0: float, y0: float) -> float:
    return y0 * math.exp(-(x**2 - x0**2))

def exact_test3(x: float, x0: float, y0: float) -> float:
    C = (y0 + 0.5 * (math.sin(x0) + math.cos(x0))) * math.exp(-x0)
    return C * math.exp(x) - 0.5 * (math.sin(x) + math.cos(x))

ODES = {
    '1': (ode_variant5, exact_variant5, "y' = x + y"),
    '2': (ode_test1, exact_test1, "Тест 1: y' = y"),
    '3': (ode_test2, exact_test2, "Тест 2: y' = -2xy"),
    '4': (ode_test3, exact_test3, "Тест 3: y' = sin(x) + y")
}



class ODESolver:

    
    def __init__(self, f: Callable[[float, float], float], 
                 exact: Optional[Callable[[float, float, float], float]] = None):
        self.f = f
        self.exact = exact
    
    def improved_euler(self, x0: float, y0: float, xn: float, h: float) -> Tuple[np.ndarray, np.ndarray]:
        if h <= 0: raise ValueError("Шаг должен быть положительным.")
        n = max(2, int((xn - x0) / h) + 1)
        h_adj = (xn - x0) / (n - 1)
        x = np.zeros(n)
        y = np.zeros(n)
        x[0], y[0] = x0, y0
        
        for i in range(n - 1):
            try:
                k1 = self.f(x[i], y[i])
                k2 = self.f(x[i] + h_adj, y[i] + h_adj * k1)
                y[i+1] = y[i] + h_adj * (k1 + k2) / 2
                x[i+1] = x[i] + h_adj
            except (OverflowError, ValueError, ZeroDivisionError) as e:
                raise RuntimeError(f"Ошибка на шаге {i}: {e}")
        return x, y
    
    def runge_kutta4(self, x0: float, y0: float, xn: float, h: float) -> Tuple[np.ndarray, np.ndarray]:
        if h <= 0: raise ValueError("Шаг должен быть положительным.")
        n = max(2, int((xn - x0) / h) + 1)
        h_adj = (xn - x0) / (n - 1)
        x = np.zeros(n)
        y = np.zeros(n)
        x[0], y[0] = x0, y0
        
        for i in range(n - 1):
            try:
                k1 = self.f(x[i], y[i])
                k2 = self.f(x[i] + h_adj/2, y[i] + h_adj/2 * k1)
                k3 = self.f(x[i] + h_adj/2, y[i] + h_adj/2 * k2)
                k4 = self.f(x[i] + h_adj, y[i] + h_adj * k3)
                y[i+1] = y[i] + h_adj * (k1 + 2*k2 + 2*k3 + k4) / 6
                x[i+1] = x[i] + h_adj
            except (OverflowError, ValueError, ZeroDivisionError) as e:
                raise RuntimeError(f"Ошибка на шаге {i}: {e}")
        return x, y
    
    def milne_predictor(self, x: np.ndarray, y: np.ndarray, h: float, i: int) -> float:
        """Предиктор Милна"""
        f_im3 = self.f(x[i-3], y[i-3])
        f_im2 = self.f(x[i-2], y[i-2])
        f_im1 = self.f(x[i-1], y[i-1])
        return y[i-3] + 4*h/3 * (2*f_im1 - f_im2 + 2*f_im3)
    
    def milne_corrector(self, x: np.ndarray, y: np.ndarray, h: float, i: int, y_pred: float) -> float:
        """Корректор Милна"""
        f_im1 = self.f(x[i-1], y[i-1])
        f_i = self.f(x[i], y[i])
        f_ip1_pred = self.f(x[i+1], y_pred)
        return y[i-1] + h/3 * (f_im1 + 4*f_i + f_ip1_pred)
    
    def milne(self, x0: float, y0: float, xn: float, h: float) -> Tuple[np.ndarray, np.ndarray]:

        if h <= 0: raise ValueError("Шаг должен быть положительным.")
        n = max(5, int((xn - x0) / h) + 1) 
        h_adj = (xn - x0) / (n - 1)
        x = np.zeros(n)
        y = np.zeros(n)
        x[0], y[0] = x0, y0
        
        for i in range(3):
            xi, yi = x[i], y[i]
            k1 = self.f(xi, yi)
            k2 = self.f(xi + h_adj/2, yi + h_adj/2 * k1)
            k3 = self.f(xi + h_adj/2, yi + h_adj/2 * k2)
            k4 = self.f(xi + h_adj, yi + h_adj * k3)
            y[i+1] = yi + h_adj * (k1 + 2*k2 + 2*k3 + k4) / 6
            x[i+1] = xi + h_adj
        
        for i in range(3, n - 1):
            try:
                y_pred = self.milne_predictor(x, y, h_adj, i)
                y[i+1] = self.milne_corrector(x, y, h_adj, i, y_pred)
                x[i+1] = x[i] + h_adj
            except (OverflowError, ValueError, ZeroDivisionError) as e:
                raise RuntimeError(f"Ошибка метода Милна на шаге {i}: {e}")
        return x, y
    
    def runge_error_estimate(self, y_h: np.ndarray, y_h2: np.ndarray, p: int) -> np.ndarray:
        n = len(y_h)
        error = np.zeros(n)
        for i in range(n):
            idx = i * 2
            if idx < len(y_h2):
                error[i] = abs(y_h2[idx] - y_h[i]) / (2**p - 1)
            else:
                error[i] = abs(y_h2[-1] - y_h[i]) / (2**p - 1)
        return error
    
    def compute_exact_error(self, x: np.ndarray, y: np.ndarray, 
                        x0: float, y0: float) -> Tuple[Optional[float], Optional[np.ndarray]]:
        if self.exact is None:
            return None, None
        try:
            y_exact = []
            for xi in x:
                val = self.exact(xi, x0, y0)
                if val is None or not math.isfinite(val):
                    return None, None  
                y_exact.append(val)
            y_exact = np.array(y_exact)
            errors = np.abs(y_exact - y)
            return float(np.max(errors)), errors
        except Exception as e:
            return None, None
    
    def solve_all(self, x0: float, y0: float, xn: float, h: float) -> Dict[str, Dict]:
        results = {}
        
        # Эйлер (p=2)
        try:
            x_e, y_e = self.improved_euler(x0, y0, xn, h)
            x_e2, y_e2 = self.improved_euler(x0, y0, xn, h/2)
            err_e_runge = self.runge_error_estimate(y_e, y_e2, p=2)
            max_err_e, errs_e_exact = self.compute_exact_error(x_e, y_e, x0, y0)
            results['euler_improved'] = {
                'x': x_e, 'y': y_e, 'max_error': max_err_e, 
                'runge_errors': err_e_runge, 'exact_errors': errs_e_exact,
                'order': 2, 'status': 'OK'
            }
        except Exception as e:
            results['euler_improved'] = {'status': f'ERROR: {e}'}
        
        # Рунге-Кутта 4-го порядка (p=4)
        try:
            x_rk, y_rk = self.runge_kutta4(x0, y0, xn, h)
            x_rk2, y_rk2 = self.runge_kutta4(x0, y0, xn, h/2)
            err_rk_runge = self.runge_error_estimate(y_rk, y_rk2, p=4)
            max_err_rk, errs_rk_exact = self.compute_exact_error(x_rk, y_rk, x0, y0)
            results['runge_kutta4'] = {
                'x': x_rk, 'y': y_rk, 'max_error': max_err_rk,
                'runge_errors': err_rk_runge, 'exact_errors': errs_rk_exact,
                'order': 4, 'status': 'OK'
            }
        except Exception as e:
            results['runge_kutta4'] = {'status': f'ERROR: {e}'}
        
        # Метод Милна
        try:
            x_m, y_m = self.milne(x0, y0, xn, h)
            max_err_m, errs_m_exact = self.compute_exact_error(x_m, y_m, x0, y0)
            results['milne'] = {
                'x': x_m, 'y': y_m, 'max_error': max_err_m,
                'exact_errors': errs_m_exact, 'status': 'OK'
            }
        except Exception as e:
            results['milne'] = {'status': f'ERROR: {e}'}
        
        return results


# безопасность 

def safe_input_float(prompt: str, default: Optional[float] = None, 
                     min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
    while True:
        try:
            raw = input(prompt).strip()
            if not raw and default is not None:
                val = default
            else:
                val = float(raw.replace(',', '.'))
            if min_val is not None and val < min_val:
                print(f"Значение должно быть >= {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Значение должно быть <= {max_val}.")
                continue
            return val
        except ValueError:
            print("Ошибка: введите корректное число.")
        except KeyboardInterrupt:
            print("\nПрограмма остановлена.")
            sys.exit(0)

#  ВЫВОД И ГРАФИКИ
def print_results_table(results: Dict[str, Dict], method_name: str):
    res = results.get(method_name)
    if not res or res.get('status') != 'OK':
        print(f"{method_name}: {res.get('status', 'Нет данных')}")
        return
    
    x, y = res['x'], res['y']
    print(f"\n{method_name.upper()}:")
    print(f"{'x':>10} {'y_approx':>12} {'y_exact':>12} {'|error|':>12}")
    print("-" * 50)
    
    step = max(1, len(x) // 10)
    for i in range(0, len(x), step):
        y_ex = None
        err = None
        if res.get('exact_errors') is not None and i < len(res['exact_errors']):
            exact_val = y[i] + (res['exact_errors'][i] if y[i] <= y[i] + res['exact_errors'][i] else -res['exact_errors'][i])
            y_ex = exact_val
            err = res['exact_errors'][i]
        
        y_ex_str = f"{y_ex:.6f}" if y_ex is not None and isinstance(y_ex, (int, float)) else "N/A"
        err_str = f"{err:.2e}" if err is not None and isinstance(err, (int, float)) else "N/A"
        print(f"{x[i]:10.4f} {y[i]:12.6f} {y_ex_str:>12} {err_str:>12}")
    
    print("-" * 50)
    max_err = res.get('max_error')
    if max_err is not None and isinstance(max_err, (int, float)):
        print(f"Максимальная погрешность: {max_err:.2e}")
    elif max_err is not None:
        print(f"Максимальная погрешность: {max_err}")

def plot_solutions(results: Dict[str, Dict], x0: float, xn: float, 
                   y0: float, exact_func: Optional[Callable] = None):
    plt.figure(figsize=(12, 7))
    
    y_exact = None
    if exact_func:
        x_dense = np.linspace(x0, xn, 500)
        try:
            y_exact_vals = [exact_func(xi, x0, y0) for xi in x_dense]
            y_exact = np.array([v for v in y_exact_vals if v is not None and math.isfinite(v)])
            if len(y_exact) > 0:
                plt.plot(x_dense[:len(y_exact)], y_exact, 'k-', linewidth=2, label='Точное решение')
        except Exception as e:
            print(f" Не удалось вычислить точное решение: {e}")
    
    colors = {'euler_improved': 'blue', 'runge_kutta4': 'green', 'milne': 'red'}
    styles = {'euler_improved': '--', 'runge_kutta4': '-.', 'milne': ':'}
    
    for name, res in results.items():
        if res.get('status') == 'OK' and 'x' in res and 'y' in res:
            label = f"{name}"
            if res.get('max_error') is not None:
                label += f" (max_err={res['max_error']:.2e})"
            plt.plot(res['x'], res['y'], color=colors.get(name, 'gray'), 
                    linestyle=styles.get(name, '-'), linewidth=1.5, label=label)
    
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Численное решение ОДУ (Вариант 5)')
    plt.legend(fontsize=9)
    plt.grid(True, alpha=0.3)
    

    all_y = []
    for res in results.values():
        if res.get('status') == 'OK' and 'y' in res:
            for val in res['y']:
                if isinstance(val, (int, float)) and math.isfinite(val):
                    all_y.append(val)
    if y_exact is not None and len(y_exact) > 0:
        for val in y_exact:
            if isinstance(val, (int, float)) and math.isfinite(val):
                all_y.append(val)
    
    if all_y:
        y_min, y_max = min(all_y), max(all_y)
        if y_max != y_min:
            margin = 0.1 * (y_max - y_min)
            plt.ylim(y_min - margin, y_max + margin)
        else:
            plt.ylim(y_min - 1, y_max + 1)
    
    plt.tight_layout()
    plt.show()






def main():
    while True:
        print("\nВыбор уравнения:")
        for k, (_, _, name) in ODES.items():
            print(f"  {k}. {name}")
        
        key = input(f"Номер ОДУ (базовое: 1): ").strip() or "1"
        if key not in ODES:
            print("Неверный номер. Попробуйте снова.")
            continue
        
        f, exact, name = ODES[key]
        solver = ODESolver(f, exact)
        
        print(f"\nПараметры для {name}:")
        x0 = safe_input_float(f"Начало интервала x0 (базовое: 0): ", default=0.0)
        y0 = safe_input_float(f"Начальное условие y({x0}) (базовое: 1): ", default=1.0)
        xn = safe_input_float(f"Конец интервала xn (базовое: 2): ", default=2.0, min_val=x0 + STEP_MIN)
        h = safe_input_float(f"Шаг h (базовое: 0.2): ", default=0.2, min_val=STEP_MIN, max_val=STEP_MAX)
        
        n_steps = int((xn - x0) / h) + 1
        if n_steps < 5:
            print(f"Предупреждение: для метода Милна требуется минимум 5 точек.")
            h = (xn - x0) / 5
            print(f"Шаг автоматически изменён на: {h:.4f}")
        
        print("\nВычисление...")
        try:
            results = solver.solve_all(x0, y0, xn, h)
        except Exception as e:
            print(f"Ошибка вычислений: {e}")
            continue
        
        print("\n" + "=" * 60)
        print("ТАБЛИЦЫ РЕЗУЛЬТАТОВ")
        print("=" * 60)
        for method in ['euler_improved', 'runge_kutta4', 'milne']:
            print_results_table(results, method)
        
        plot_choice = input("\nПостроить графики? (y/n) (базовое: y): ").strip().lower() or "y"
        if plot_choice == 'y':
            try:
                plot_solutions(results, x0, xn, y0, exact)
            except Exception as e:
                print(f"Ошибка построения графика: {e}")
        
        print("\nАНАЛИЗ РЕЗУЛЬТАТОВ:")
        for method, res in results.items():
            if res.get('status') == 'OK' and res.get('max_error') is not None:
                print(f"  {method}: max|error| = {res['max_error']:.2e}")
        
        valid = {k: v for k, v in results.items() 
                if v.get('status') == 'OK' and v.get('max_error') is not None}
        if valid:
            best = min(valid, key=lambda k: valid[k]['max_error'])
            print(f"\nНаилучший метод по точности: {best}")
        
        cont = input("\nПродолжить? (y/n) (базовое: n): ").strip().lower() or "n"
        if cont != 'y':
            break
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        sys.exit(0)