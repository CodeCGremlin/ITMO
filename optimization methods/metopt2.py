import numpy as np
import matplotlib.pyplot as plt
import torch

# ==========================================
# Определение функции и её градиента
# ==========================================

def f(x, y):
    """Целевая функция"""
    return 0.01 * (8*x**2 + 2*x*y - 21*x - 6*y - 9)

def grad_f(x, y):
    """Градиент функции"""
    dx = 0.01 * (16*x + 2*y - 21)
    dy = 0.01 * (2*x - 6)
    return np.array([dx, dy])

def plot_trajectory(x_traj, y_traj, title, domain, 
                    highlight_saddle=True, highlight_start=True):
    """
    Вспомогательная функция для визуализации.
    domain: кортеж (x_min, x_max, y_min, y_max)
    """
    x_min, x_max, y_min, y_max = domain
    
    # Сетка для линий уровня
    x = np.linspace(x_min, x_max, 200)
    y = np.linspace(y_min, y_max, 200)
    X, Y = np.meshgrid(x, y)
    Z = f(X, Y)
    
    plt.figure(figsize=(8, 6))
    
    # Линии уровня
    levels = np.linspace(Z.min(), Z.max(), 30)
    contour = plt.contour(X, Y, Z, levels=levels, cmap='viridis', alpha=0.6)
    plt.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.2)
    # Подписи только для некоторых уровней, чтобы не засорять
    plt.clabel(contour, inline=True, fontsize=8, fmt='%.1f')
    
    # Траектория
    plt.plot(x_traj, y_traj, 'r-o', markersize=4, linewidth=1.5, label='Траектория')
    
    if highlight_start:
        plt.plot(x_traj[0], y_traj[0], 'yo', markersize=12, markeredgecolor='black', 
                 label='Старт', zorder=5)
    
    if highlight_saddle:
        # Рисуем седловую точку, только если она попадает в область отображения
        if x_min <= 3 <= x_max and y_min <= -13.5 <= y_max:
            plt.plot(3, -13.5, 'r*', markersize=15, label='Седловая точка', zorder=5)
        
    plt.title(title, fontsize=12)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.tight_layout()
    plt.show()

# ==========================================
# ЗАДАНИЕ 1: Градиентный спуск
# ==========================================

def task_1_gradient_descent():
    print("Запуск Задания 1...")
    x, y = -5.0, 40.0
    alpha = 0.3
    epsilon = 1e-5
    
    x_hist, y_hist = [x], [y]
    
    for i in range(100):
        grad = grad_f(x, y)
        x_new = x - alpha * grad[0]
        y_new = y - alpha * grad[1]
        
        delta_f = abs(f(x_new, y_new) - f(x, y))
        if delta_f < epsilon:
            print(f"Критерий останова выполнен на итерации {i+1}.")
            break
            
        x, y = x_new, y_new
        x_hist.append(x)
        y_hist.append(y)
        
    # Область: Видно и старт (вверху), и седло (внизу), но траектория короткая
    domain = (-10, 10, -20, 50)
    plot_trajectory(x_hist, y_hist, 
                    f"GD: Останов на ит. {len(x_hist)-1} (Движение к минимуму на границе)", 
                    domain=domain)

# ==========================================
# ЗАДАНИЕ 2: RMSProp
# ==========================================

def task_2_rmsprop():
    print("Запуск Задания 2...")
    x, y = -5.0, 40.0
    alpha = 0.3
    gamma = 0.75
    eps = 1e-8
    s_x, s_y = 0.0, 0.0
    
    x_hist, y_hist = [x], [y]
    
    for i in range(100):
        grad = grad_f(x, y)
        s_x = gamma * s_x + (1 - gamma) * grad[0]**2
        s_y = gamma * s_y + (1 - gamma) * grad[1]**2
        x -= alpha * grad[0] / (np.sqrt(s_x) + eps)
        y -= alpha * grad[1] / (np.sqrt(s_y) + eps)
        x_hist.append(x)
        y_hist.append(y)
        
    # Область: Сдвинута вверх, так как RMSProp улетает к y=50
    domain = (-10, 10, 35, 55) 
    plot_trajectory(x_hist, y_hist, 
                    "RMSProp: Движение к глобальному минимуму (gamma=0.75)", 
                    domain=domain, highlight_saddle=False) # Седло далеко внизу, не рисуем

# ==========================================
# ЗАДАНИЕ 3: Подбор гиперпараметров (RMSProp)
# ==========================================

def task_3_visualization():
    print("Запуск Задания 3...")
    # Область из задания
    domain = (-7.0, 7.0, -10.0, 60.0)
    
    # 1. Пилообразная (gamma=0.1)
    x, y = -5.0, 40.0
    alpha, gamma = 0.3, 0.1
    s_x, s_y = 0.0, 0.0
    hist1 = [(-5.0, 40.0)]
    for _ in range(100):
        grad = grad_f(x, y)
        s_x = gamma * s_x + (1 - gamma) * grad[0]**2
        s_y = gamma * s_y + (1 - gamma) * grad[1]**2
        x -= alpha * grad[0] / (np.sqrt(s_x) + 1e-8)
        y -= alpha * grad[1] / (np.sqrt(s_y) + 1e-8)
        hist1.append((x, y))
        
    plot_trajectory([p[0] for p in hist1], [p[1] for p in hist1], 
                    "RMSProp: Пилообразная ломаная (gamma=0.1)", 
                    domain=domain)

    # 2. Четкое движение (gamma=0.99)
    x, y = -5.0, 40.0
    alpha, gamma = 0.3, 0.99
    s_x, s_y = 0.0, 0.0
    hist2 = [(-5.0, 40.0)]
    for _ in range(100):
        grad = grad_f(x, y)
        s_x = gamma * s_x + (1 - gamma) * grad[0]**2
        s_y = gamma * s_y + (1 - gamma) * grad[1]**2
        x -= alpha * grad[0] / (np.sqrt(s_x) + 1e-8)
        y -= alpha * grad[1] / (np.sqrt(s_y) + 1e-8)
        hist2.append((x, y))
        
    plot_trajectory([p[0] for p in hist2], [p[1] for p in hist2], 
                    "RMSProp: Четкое движение (gamma=0.99)", 
                    domain=domain)

# ==========================================
# ЗАДАНИЕ 4: PyTorch AdaGrad
# ==========================================

def task_4_pytorch_adagrad():
    print("Запуск Задания 4 (PyTorch Adagrad)...")
    
    x = torch.tensor([-5.0], requires_grad=True)
    y = torch.tensor([40.0], requires_grad=True)
    optimizer = torch.optim.Adagrad([x, y], lr=0.3)
    
    x_hist, y_hist = [-5.0], [40.0]
    
    for i in range(100):
        optimizer.zero_grad()
        loss = 0.01 * (8*x**2 + 2*x*y - 21*x - 6*y - 9)
        loss.backward()
        optimizer.step()
        x_hist.append(x.item())
        y_hist.append(y.item())
        
    # Область: Сильный зум на старт, так как Adagrad там "застревает"
    domain = (-5.5, -4.5, 39.5, 40.5)
    plot_trajectory(x_hist, y_hist, 
                    "PyTorch Adagrad: Застревание на старте (Zoom)", 
                    domain=domain, highlight_saddle=False)

if __name__ == "__main__":
    task_1_gradient_descent()
    task_2_rmsprop()
    task_3_visualization()
    task_4_pytorch_adagrad()