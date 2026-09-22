
import math
import sys

# 1. НАСТРОЙКИ И КОНСТАНТЫ
MAX_RUNGE_STEPS = 25       
MAX_N = 2**18              
EPS_MIN = 1e-12            
DIVERGENCE_THRESHOLD = 1e6 

# 2. ВВОД И ВАЛИДАЦИЯ

def get_valid_input(prompt, type_cast=float, validators=None, default=None):
    """Универсальный безопасный ввод с обработкой ошибок и Ctrl+C"""
    while True:
        try:
            raw = input(prompt).strip()
            if not raw and default is not None:
                return default
            
            val = type_cast(raw)
            if validators and not all(v(val) for v in validators):
                print(" Значение не соответствует требованиям. Попробуйте снова.")
                continue
            return val
        except ValueError:
            print(f" Ошибка формата. Ожидается число ({type_cast.__name__}).")
        except KeyboardInterrupt:
            print("\n Ввод прерван. Завершение программы.")
            sys.exit(0)
        except EOFError:
            print("\n Поток ввода закрыт. Завершение программы.")
            sys.exit(0)

# Валидаторы
is_positive = lambda x: x > 0
is_valid_range = lambda a_b: a_b[0] < a_b[1]


# 3. ПОДЫНТЕГРАЛЬНЫЕ ФУНКЦИИ

def f_variant5(x): return -2*x**3 - 3*x**2 + x + 5
def f_test1(x): return x**2
def f_test2(x): return math.sin(x) + x
def f_test3(x): return math.exp(-x)

FUNCTIONS = {
    '1': (f_variant5, "Вариант 5: -2x³ - 3x² + x + 5"),
    '2': (f_test1, "Тест 1: x²"),
    '3': (f_test2, "Тест 2: sin(x) + x"),
    '4': (f_test3, "Тест 3: exp(-x)")
}


# 4. ЧИСЛЕННЫЕ МЕТОДЫ
def _safe_eval(f, x):
    """Безопасное вычисление f(x) с проверкой на бесконечность/NaN"""
    try:
        val = f(x)
        return val if math.isfinite(val) else None
    except (OverflowError, ValueError, ZeroDivisionError):
        return None

def rect_left(f, a, b, n):
    h = (b - a) / n
    total = sum(_safe_eval(f, a + i*h) for i in range(n))
    return h * total if all(v is not None for v in [total]) else None

def rect_right(f, a, b, n):
    h = (b - a) / n
    total = sum(_safe_eval(f, a + (i+1)*h) for i in range(n))
    return h * total if all(v is not None for v in [total]) else None

def rect_mid(f, a, b, n):
    h = (b - a) / n
    total = sum(_safe_eval(f, a + (i + 0.5)*h) for i in range(n))
    return h * total if all(v is not None for v in [total]) else None

def trapezoidal(f, a, b, n):
    h = (b - a) / n
    fa, fb = _safe_eval(f, a), _safe_eval(f, b)
    if fa is None or fb is None: return None
    mid_sum = sum(_safe_eval(f, a + i*h) for i in range(1, n))
    return h * (0.5*fa + mid_sum + 0.5*fb) if all(v is not None for v in [mid_sum]) else None

def simpson(f, a, b, n):
    if n % 2 != 0: n += 1  # Симпсон требует четного n
    h = (b - a) / n
    fa, fb = _safe_eval(f, a), _safe_eval(f, b)
    if fa is None or fb is None: return None
    s1 = sum(_safe_eval(f, a + i*h) for i in range(1, n, 2))
    s2 = sum(_safe_eval(f, a + i*h) for i in range(2, n-1, 2))
    res = h/3 * (fa + fb + 4*s1 + 2*s2)
    return res if all(v is not None for v in [s1, s2, res]) else None

METHODS = {
    '1': (rect_left, "Левые прямоугольники", 1),
    '2': (rect_right, "Правые прямоугольники", 1),
    '3': (rect_mid, "Средние прямоугольники", 2),
    '4': (trapezoidal, "Трапеции", 2),
    '5': (simpson, "Симпсон", 4)
}


# 5. ПРАВИЛО РУНГЕ
def runge_adaptive(f, a, b, eps, method_func, p):
    """Вычисление интеграла с автоматическим подбором n по правилу Рунге"""
    n = 4
    I_prev = method_func(f, a, b, n)
    if I_prev is None:
        return None, n, float('inf'), "Ошибка вычисления на начальном шаге (особая точка?)"

    for step in range(MAX_RUNGE_STEPS):
        n *= 2
        if n > MAX_N:
            return I_prev, n//2, float('inf'), "Превышен лимит разбиений. Точность не достигнута."

        I_curr = method_func(f, a, b, n)
        if I_curr is None:
            return I_prev, n//2, float('inf'), "Возникла особая точка при увеличении n."

        err = abs(I_curr - I_prev) / (2**p - 1)
        if err < eps:
            return I_curr, n, err, " Точность достигнута."
        
        I_prev = I_curr

    return I_prev, n, err, " Лимит итераций. Результат может быть неточным."


# 6. НЕСОБСТВЕННЫЕ ИНТЕГРАЛЫ 2 РОДА С ПРОВЕРКОЙ СХОДИМОСТИ

def compute_improper(f, a, b, sing_type, eps):
    deltas = [1e-4, 1e-6, 1e-8]
    results = []
    
    for d in deltas:
        try:
            if sing_type == 'a':
                res, _, err, _ = runge_adaptive(f, a+d, b, eps, trapezoidal, 2)
            elif sing_type == 'b':
                res, _, err, _ = runge_adaptive(f, a, b-d, eps, trapezoidal, 2)
            elif sing_type == 'mid':
                mid = (a + b) / 2
                r1, _, _, _ = runge_adaptive(f, a, mid-d, eps, trapezoidal, 2)
                r2, _, _, _ = runge_adaptive(f, mid+d, b, eps, trapezoidal, 2)
                res = (r1 if r1 is not None else 0) + (r2 if r2 is not None else 0)
            else:
                return None, "Неверный тип особенности."
                
            if res is None or not math.isfinite(res):
                return None, " Вычисление прервано из-за расходимости или ошибки."
            results.append(res)
        except:
            return None, " Ошибка вычислений при проверке сходимости."

    # Проверка стабилизации
    if len(results) == 3 and abs(results[-1] - results[-2]) < 0.01 * abs(results[-2]) and abs(results[-1]) < DIVERGENCE_THRESHOLD:
        return results[-1], " Интеграл сходится."
    else:
        return None, " Интеграл не существует (расходится)."


# 7. ГЛАВНОЕ МЕНЮ И УПРАВЛЕНИЕ

def main():
    print("\n" + "="*60)
    print(" ЛАБОРАТОРНАЯ РАБОТА №3: ЧИСЛЕННОЕ ИНТЕГРИРОВАНИЕ")
    print("="*60)
    
    while True:
        print("\n1. Собственный интеграл (обязательное)")
        print("2. Несобственный интеграл 2 рода (дополнительное)")
        print("3. Выход")
        
        task = get_valid_input("Выберите задачу (1/2/3): ", type_cast=str, default="3")
        if task == "3": break
        if task not in ["1", "2"]:
            print(" Доступны только варианты 1, 2 или 3.")
            continue

        try:
            if task == "1":
                print("\n Выберите функцию:")
                for k, (_, name) in FUNCTIONS.items(): print(f"  {k}. {name}")
                f_key = get_valid_input("Номер функции: ", type_cast=str)
                if f_key not in FUNCTIONS: print(" Неверный номер."); continue
                f, f_name = FUNCTIONS[f_key]

                print("\n Выберите метод:")
                for k, (_, m_name, _) in METHODS.items(): print(f"  {k}. {m_name}")
                m_key = get_valid_input("Номер метода: ", type_cast=str)
                if m_key not in METHODS: print(" Неверный номер."); continue
                method_func, m_name, p = METHODS[m_key]

                a = get_valid_input("Нижний предел (a) (базовое: 1.0): ", default=1.0)
                b = get_valid_input("Верхний предел (b) (базовое: 4.0): ", default=4.0)
                if a >= b:
                    print(" Нижний предел должен быть строго меньше верхнего.")
                    continue
                    
                eps = get_valid_input("Точность eps (базовое: 0.001): ", validators=[is_positive], default=0.001)

                print("\n Вычисление по правилу Рунге (старт n=4)...")
                I, n_final, err, status = runge_adaptive(f, a, b, eps, method_func, p)

                print(" РЕЗУЛЬТАТЫ")
                print(f"Функция: {f_name}")
                print(f"Метод: {m_name}")
                print(f"Пределы: [{a}, {b}]")
                if I is not None:
                    print(f"Значение интеграла: {I:.8f}")
                print(f"Разбиений n: {n_final}")
                print(f"Оценка погрешности (Рунге): {err:.2e}")
                print(f"Статус: {status}")
                print("="*50)

            elif task == "2":
                print("\n Несобственные интегралы 2 рода (проверка сходимости):")
                print("  1. ∫(1/√(x-1))dx на [1, 2]  (разрыв в a)")
                print("  2. ∫(1/(2-x))dx на [0, 2]   (разрыв в b)")
                print("  3. ∫(1/|x-1.5|)dx на [0, 3] (разрыв внутри)")
                ex = get_valid_input("Номер примера: ", type_cast=str)
                eps = get_valid_input("Точность: ", validators=[is_positive], default=0.01)

                res, msg = None, "Неверный выбор."
                if ex == "1":
                    res, msg = compute_improper(lambda x: 1/math.sqrt(x-1), 1, 2, 'a', eps)
                    print(f"\n Результат: {res if res is not None else 'Не определено'} (Точно: 2.0)")
                elif ex == "2":
                    res, msg = compute_improper(lambda x: 1/(2-x), 0, 2, 'b', eps)
                    print(f"\n Результат: {res if res is not None else 'Не определено'} (Расходится логарифмически)")
                elif ex == "3":
                    res, msg = compute_improper(lambda x: 1/abs(x-1.5), 0, 3, 'mid', eps)
                    print(f"\n Результат: {res if res is not None else 'Не определено'} (Сильная расходимость)")
                else:
                    print(" Неверный номер примера.")
                    continue

                print(f" Статус: {msg}")
                if res is not None:
                    print(f" Приближенное значение: {res:.6f}")
                else:
                    print(" Интеграл не существует (расходится).")

        except Exception as e:
            print(f"\n Критическая ошибка: {e}. Программа продолжит работу.")
            continue

    print("\n  Программа завершена.")

# 8. ЗАПУСК
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Программа остановлена пользователем.")
    except EOFError:
        print("\n Поток ввода закрыт.")
    except Exception as e:
        print(f"\n Неожиданная ошибка: {e}")
    finally:
        print(" Выполнение завершено.")
    
    

