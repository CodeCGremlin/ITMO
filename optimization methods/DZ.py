import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# ============================================================
# ДЗ1.1: Адаптивная кубическая аппроксимация
# ============================================================

def f(x):
    """Целевая функция: f(x) = x² + x + sin(x)"""
    return x**2 + x + np.sin(x)

def cubic_approximation_adaptive(f, a, b, epsilon, max_iter=50):
    """
    Адаптивная аппроксимация кубическим сплайном.
    
    Параметры:
    ----------
    f : функция
        Аппроксимируемая функция
    a, b : float
        Границы интервала
    epsilon : float
        Критерий останова (максимальная допустимая погрешность)
    max_iter : int
        Максимальное число итераций
    
    Возвращает:
    -----------
    iterations : list
        Список словарей с данными каждой итерации
    """
    iterations = []
    
    # Начальные узлы (минимум 4 для кубического сплайна)
    n_nodes = 4
    x_nodes = np.linspace(a, b, n_nodes)
    y_nodes = f(x_nodes)
    
    for iteration in range(max_iter):
        # Построение кубического сплайна
        cs = CubicSpline(x_nodes, y_nodes, bc_type='natural')
        
        # Оценка погрешности на мелкой сетке
        x_eval = np.linspace(a, b, 2000)
        y_exact = f(x_eval)
        y_approx = cs(x_eval)
        errors = np.abs(y_exact - y_approx)
        max_error = np.max(errors)
        
        # Сохранение данных итерации
        iterations.append({
            'iter': iteration,
            'x_nodes': x_nodes.copy(),
            'y_nodes': y_nodes.copy(),
            'spline': cs,
            'x_eval': x_eval,
            'y_exact': y_exact,
            'y_approx': y_approx,
            'errors': errors,
            'max_error': max_error
        })
        
        print(f"Iter {iteration:2d}: nodes={len(x_nodes):2d}, max_err={max_error:.2e}")
        
        # Проверка критерия останова
        if max_error < epsilon:
            print(f"\n✓ Сходимость достигнута за {iteration + 1} итераций!")
            break
        
        # Адаптивное уточнение: добавление узла в точке макс. погрешности
        if iteration < max_iter - 1:
            idx_max = np.argmax(errors)
            x_new = x_eval[idx_max]
            insert_pos = np.searchsorted(x_nodes, x_new)
            x_nodes = np.insert(x_nodes, insert_pos, x_new)
            y_nodes = f(x_nodes)
    
    return iterations


# ============================================================
# ДЗ1.2: Визуализация
# ============================================================

def plot_approximation(iterations, iteration_indices, save_path=None):
    """Визуализация исходной и аппроксимирующей функций"""
    n_plots = len(iteration_indices)
    cols = 2
    rows = (n_plots + 1) // 2
    
    fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 4*rows))
    if n_plots == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    for ax, iter_idx in zip(axes, iteration_indices):
        if iter_idx >= len(iterations):
            continue
        data = iterations[iter_idx]
        
        # Исходная функция
        ax.plot(data['x_eval'], data['y_exact'], 'b-', linewidth=2, 
                label='f(x) = x² + x + sin(x)')
        # Аппроксимация
        ax.plot(data['x_eval'], data['y_approx'], 'r--', linewidth=1.5, 
                label='Cubic Spline')
        # Узлы
        ax.plot(data['x_nodes'], data['y_nodes'], 'ko', markersize=4, 
                label=f'Nodes (n={len(data["x_nodes"])})')
        
        # Погрешность (дополнительная ось)
        ax2 = ax.twinx()
        ax2.plot(data['x_eval'], data['errors'], 'g:', linewidth=0.5, alpha=0.7)
        ax2.set_ylabel('Error', color='green', fontsize=9)
        ax2.tick_params(axis='y', labelcolor='green', labelsize=8)
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title(f'Iteration {data["iter"]}: max_err = {data["max_error"]:.2e}', 
                    fontweight='bold')
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(-1.05, 0.05)
    
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_convergence(iterations):
    """График сходимости погрешности"""
    max_errors = [it['max_error'] for it in iterations]
    iters = [it['iter'] for it in iterations]
    
    plt.figure(figsize=(8, 5))
    plt.semilogy(iters, max_errors, 'bo-', linewidth=2, markersize=6)
    plt.axhline(y=0.0001, color='r', linestyle='--', label='ε = 0.0001')
    plt.xlabel('Iteration')
    plt.ylabel('Max Error (log scale)')
    plt.title('Convergence of Cubic Approximation', fontweight='bold')
    plt.grid(True, alpha=0.3, which='both')
    plt.legend()
    plt.tight_layout()
    plt.show()


# ============================================================
# Запуск программы
# ============================================================

if __name__ == "__main__":
    # Параметры варианта 14
    a, b = -1, 0
    epsilon = 0.0001
    
    print("=" * 60)
    print("ДЗ1.1-1.2: Кубическая аппроксимация")
    print("Вариант 14: f(x) = x² + x + sin(x), [a,b] = [-1, 0]")
    print(f"Критерий останова: ε = {epsilon}")
    print("=" * 60)
    
    # Запуск алгоритма
    print("\nЗапуск аппроксимации...")
    iterations = cubic_approximation_adaptive(f, a, b, epsilon)
    
    # Итоговые результаты
    final = iterations[-1]
    print(f"\n Результаты:")
    print(f"   • Итераций: {len(iterations)}")
    print(f"   • Узлов: {len(final['x_nodes'])}")
    print(f"   • Макс. погрешность: {final['max_error']:.6f}")
    print(f"   • Узлы: {np.round(final['x_nodes'], 4)}")
    
    # Визуализация (ДЗ1.2)
    print(f"\n Построение графиков...")
    n = len(iterations)
    indices = [0, 1, n//2, n-1] if n > 4 else list(range(n))
    
    plot_approximation(iterations, indices, save_path='cubic_approx.png')
    plot_convergence(iterations)
    
    # Детальный анализ последней итерации
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(final['x_eval'], final['y_exact'], 'b-', label='f(x)', linewidth=2)
    plt.plot(final['x_eval'], final['y_approx'], 'r--', label='Spline', linewidth=1.5)
    plt.plot(final['x_nodes'], final['y_nodes'], 'ko', label='Nodes')
    plt.xlabel('x'); plt.ylabel('y'); plt.title('Final Approximation')
    plt.legend(); plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(final['x_eval'], final['errors'], 'g-', linewidth=1)
    plt.axhline(y=epsilon, color='r', linestyle='--', label=f'ε')
    plt.xlabel('x'); plt.ylabel('|error|'); plt.title('Error Distribution')
    plt.legend(); plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('final_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n✓ Задания выполнены!")