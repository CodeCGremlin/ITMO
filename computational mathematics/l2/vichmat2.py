
import os
import math
import numpy as np
import matplotlib.pyplot as plt

# 1. МАТЕМАТИЧЕСКИЕ ФУНКЦИИ И КОНСТАНТЫ

MAX_ITER = 1000
EPS_MIN = 1e-12

def var5_f(x): return -2.7*x**3 - 1.48*x**2 + 19.23*x + 6.35
def var5_df(x): return -8.1*x**2 - 2.96*x + 19.23
def var5_d2f(x): return -16.2*x - 2.96

# Безопасные обёртки для тригонометрии (защита от асимптот и переполнений)
def safe_cos(x):
    c = math.cos(x)
    return c if abs(c) > EPS_MIN else (EPS_MIN if c > 0 else -EPS_MIN)

def safe_tan(x):
    try:
        t = math.tan(x)
        return t if abs(t) < 1e9 else math.copysign(1e9, t)
    except: return math.copysign(1e9, math.sin(x))

# 2. (SOLVER)
class Solver:
    @staticmethod
    def solve(data):
        try:
            return Solver._solve_system(data) if data[0] else Solver._solve_equation(data)
        except Exception as e:
            return f"Критическая ошибка вычислений: {e}"

    @staticmethod
    def _safe_parse(interval_str, precision_str):
        try:
            parts = interval_str.replace(',', '.').split(';')
            if len(parts) != 2: raise ValueError("Ожидается два числа через ';'.")
            a, b = float(parts[0]), float(parts[1])
            eps = float(precision_str.replace(',', '.'))
            if eps <= 0: raise ValueError("Точность должна быть > 0.")
            if a >= b: raise ValueError("Левая граница должна быть < правой.")
            return a, b, eps
        except ValueError as ve:
            raise ve
        except:
            raise ValueError("Неверный формат ввода.")

    @staticmethod
    def _solve_equation(data):
        _, method, interval_str, precision_str = data[1], data[2], data[3], data[4]
        try:
            a, b, eps = Solver._safe_parse(interval_str, precision_str)
        except ValueError as e:
            return f" Ошибка ввода: {e}"

        try:
            fa, fb = var5_f(a), var5_f(b)
        except:
            return " Ошибка вычисления функции на границах."

        if fa * fb > 0:
            return " На интервале нет корня или их несколько (f(a)·f(b) > 0). Изолируйте корень заново."
        if fa == 0: return f" Точный корень найден на границе: x = {a:.6f}"
        if fb == 0: return f" Точный корень найден на границе: x = {b:.6f}"

        if method == "Метод хорд":
            return Solver._chord(var5_f, a, b, eps)
        elif method == "Метод Ньютона":
            return Solver._newton(var5_f, var5_df, var5_d2f, a, b, eps)
        elif method == "Метод простой итерации":
            return Solver._simple_iteration(var5_f, var5_df, a, b, eps)
        return " Неизвестный метод."

    @staticmethod
    def _chord(f, a, b, eps):
        x_prev = a
        denom = f(b) - f(a)
        if abs(denom) < EPS_MIN: return " f(a) ≈ f(b). Метод хорд неприменим."
        x_curr = a - f(a) * (b - a) / denom
        k = 1
        while abs(x_curr - x_prev) > eps and k < MAX_ITER:
            x_prev = x_curr
            if f(a) * f(x_curr) < 0: b = x_curr
            else: a = x_curr
            denom = f(b) - f(a)
            if abs(denom) < EPS_MIN: break
            x_curr = a - f(a) * (b - a) / denom
            k += 1
        return f" Корень: {x_curr:.6f}\nf(x) = {f(x_curr):.2e}\nИтераций: {k}"

    @staticmethod
    def _newton(f, df, d2f, a, b, eps):
        # Правило выбора x0: f(x0)·f''(x0) > 0
        try:
            x = a if f(a)*d2f(a) > 0 else b
        except:
            return " Ошибка вычисления второй производной."
        
        k = 0
        while k < MAX_ITER:
            try:
                fx, dfx = f(x), df(x)
            except:
                return " Ошибка вычисления функции/производной."
            if abs(dfx) < EPS_MIN: return " Производная ≈ 0. Метод расходится."
            
            dx = -fx / dfx
            x_new = x + dx
            
            # Защита от ухода в бесконечность
            if abs(dx) > 1000: return " Сильное расхождение. Смените интервал или метод."
            
            if abs(dx) < eps:
                return f" Корень: {x_new:.6f}\nf(x) = {f(x_new):.2e}\nИтераций: {k+1}"
            x = x_new
            k += 1
        return f" Превышен лимит итераций ({MAX_ITER}). Текущее x={x:.6f}"

    @staticmethod
    def _simple_iteration(f, df, a, b, eps):
        try:
            max_df = max(abs(df(a)), abs(df(b)), abs(df((a+b)/2)))
        except:
            return " Ошибка вычисления производной на интервале."
        if max_df == 0: return " f'(x)=0 на интервале."
        
        lam = -1.0 / max_df
        phi = lambda x: x + lam * f(x)
        dphi = lambda x: 1 + lam * df(x)

        try:
            q = max(abs(dphi(a)), abs(dphi(b)), abs(dphi((a+b)/2)))
        except:
            return " Ошибка проверки условия сходимости."
        if q >= 1: return f" Метод расходится (q={q:.3f} ≥ 1). Уменьшите интервал."

        x = (a+b)/2
        k = 0
        while k < MAX_ITER:
            x_new = phi(x)
            if abs(x_new - x) < eps:
                return f" Корень: {x_new:.6f}\nf(x) = {f(x_new):.2e}\nИтераций: {k+1}\nq = {q:.3f}"
            x = x_new
            k += 1
        return f" Превышен лимит итераций."

    @staticmethod
    def _solve_system(data):
        try:
            x, y = map(float, data[2].replace(",", ".").split(";"))
            eps = float(data[3].replace(",", "."))
        except:
            return " Ошибка парсинга начального приближения или точности."
        if eps <= 0: return " Точность должна быть > 0."

        k, dx, dy = 0, 1.0, 1.0
        while max(abs(dx), abs(dy)) > eps and k < MAX_ITER:
            try:
                c_val = safe_cos(x*y + 0.3)
                F1 = safe_tan(x*y + 0.3) - x**2
                F2 = 0.9*x**2 + 2*y**2 - 1
                
                J11 = y / (c_val**2) - 2*x
                J12 = x / (c_val**2)
                J21 = 1.8 * x
                J22 = 4 * y
                
                det = J11*J22 - J12*J21
                if abs(det) < EPS_MIN: return " Определитель Якоби ≈ 0. Смените начальное приближение."
                
                dx = -(F1*J22 - F2*J12) / det
                dy = -(J11*F2 - J21*F1) / det
                
                if abs(dx) > 100 or abs(dy) > 100:
                    return " Сильное расхождение. Смените начальное приближение."
                    
                x += dx
                y += dy
                k += 1
                
            except OverflowError:
                return " Переполнение (функции ушли в бесконечность). Смените приближение."
            except Exception as e:
                return f" Ошибка вычислений на шаге {k}: {e}"
                
        return (f" Решение: x = {x:.6f}, y = {y:.6f}\n"
                f" Итераций: {k}\n"
                f" Погрешность: |Δx|={dx:.2e}, |Δy|={dy:.2e}\n"
                f" Проверка: F1={safe_tan(x*y+0.3)-x**2:.2e}, F2={0.9*x**2+2*y**2-1:.2e}")

# 3. УТИЛИТЫ: ГРАФИКИ И ФАЙЛЫ

def plot_equation():
    try:
        x = np.linspace(-3, 3, 800)
        y = var5_f(x)
        plt.figure(figsize=(7,5))
        plt.plot(x, y, label=r"$f(x) = -2.7x^3 - 1.48x^2 + 19.23x + 6.35$")
        plt.axhline(0, color='k', lw=1); plt.axvline(0, color='k', lw=1)
        plt.grid(True); plt.legend(); plt.title("График уравнения (Вариант 5)")
        plt.show(block=False)
        plt.pause(0.1) # Предотвращает зависание в некоторых средах
    except Exception as e:
        print(f" Ошибка построения графика: {e}")

def plot_system():
    try:
        x = np.linspace(-1.5, 1.5, 400)
        y = np.linspace(-1.5, 1.5, 400)
        X, Y = np.meshgrid(x, y)
        Z1 = np.tan(X*Y + 0.3) - X**2
        Z2 = 0.9*X**2 + 2*Y**2 - 1
        # Ограничиваем значения для чистого контура
        Z1 = np.clip(Z1, -10, 10)
        Z2 = np.clip(Z2, -10, 10)
        
        plt.figure(figsize=(7,7))
        plt.contour(X, Y, Z1, levels=[0], colors='r', linestyles='--')
        plt.contour(X, Y, Z2, levels=[0], colors='b')
        plt.axhline(0, color='k', lw=0.5); plt.axvline(0, color='k', lw=0.5)
        plt.grid(True); plt.title("Система уравнений (Вариант 5)")
        plt.legend(["tan(xy+0.3)=x²", "0.9x²+2y²=1"])
        plt.show(block=False)
        plt.pause(0.1)
    except Exception as e:
        print(f" Ошибка построения графика: {e}")


# 4. КОНСОЛЬНЫЙ ИНТЕРФЕЙС (100% ОТКАЗОУСТОЙЧИВОСТЬ)

def run_console():
    print("\n  КОНСОЛЬНЫЙ РЕЖИМ | Вариант 5")
    print(" Подсказка: для выхода введите 'exit' или нажмите Ctrl+C.")
    
    while True:
        try:
            cmd = input("\nКоманда (solve / exit): ").strip().lower()
            if cmd in ["exit", "выход", "q"]: break
            if cmd != "solve":
                print(" Доступные команды: solve, exit")
                continue

            t = input("Тип задачи (1-Уравнение, 2-Система): ").strip()
            is_sys = (t == "2")
            
            if not is_sys:
                methods = ["Метод хорд", "Метод Ньютона", "Метод простой итерации"]
                print("\nДоступные методы:")
                for i, m in enumerate(methods, 1): print(f"  {i}. {m}")
                m_in = input("Номер метода (1-3): ").strip()
                if m_in not in ["1","2","3"]: print(" Неверный номер. Использую первый метод."); m_idx = 0
                else: m_idx = int(m_in) - 1
                
                interval = input("Интервал (a;b) (базовое: -2;3): ").strip() or "-2;3"
                precision = input("Точность (базовое: 0.001): ").strip() or "0.001"
                data = False, "Eq5", methods[m_idx], interval, precision
            else:
                init = input("Нач. приближение (x;y) (базовое: 0.5;0.5): ").strip() or "0.5;0.5"
                precision = input("Точность (базовое: 0.001): ").strip() or "0.001"
                data = True, "Sys5", init, precision
                
            print("\n Вычисление...")
            res = Solver.solve(data)
            print("\n" + "="*50)
            print(res)
            print("="*50)
            
            print("\n Отображение графика... (закройте окно для продолжения)")
            if not is_sys: plot_equation()
            else: plot_system()
            
            if input("\nСохранить результат в файл? (y/n): ").strip().lower() == 'y':
                fname = input("Имя файла (result.txt): ").strip() or "result.txt"
                try:
                    with open(fname, "w", encoding="utf-8") as f: f.write(res)
                    print(f" Сохранено в {fname}")
                except PermissionError: print(" Нет прав на запись в файл.")
                except Exception as e: print(f" Ошибка сохранения: {e}")
                
        except KeyboardInterrupt:
            print("\n Программа остановлена пользователем.")
            break
        except EOFError:
            print("\n Ввод завершён.")
            break
        except Exception as e:
            print(f" Непредвиденная ошибка: {e}. Попробуйте снова.")


# 5. ГЛАВНЫЙ ЗАПУСК

if __name__ == "__main__":
    try:
        print(" Запуск Лабораторной работы №2 | Вариант 5")
        run_console()
    except Exception as e:
        print(f" Критическая ошибка запуска: {e}")
    finally:
        print(" Программа завершена.")