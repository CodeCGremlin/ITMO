#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль построения линий уровня функции:
f(x,y) = 0.01 * (8x² + 2xy - 21x - 6y - 9)
Область: x ∈ [-20, 20], y ∈ [-50, 50]
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

def objective_function(x, y):
    """Целевая функция"""
    return 0.01 * (8*x**2 + 2*x*y - 21*x - 6*y - 9)

def plot_contours():
    """
    Построение линий уровня функции с отметкой особых точек
    """
    # Создание сетки
    x = np.linspace(-20, 20, 500)
    y = np.linspace(-50, 50, 500)
    X, Y = np.meshgrid(x, y)
    Z = objective_function(X, Y)
    
    # Настройка графика
    plt.figure(figsize=(14, 10))
    
    # Линии уровня
    levels = np.linspace(-10, 60, 35)
    contour = plt.contour(X, Y, Z, levels=levels, cmap='viridis', alpha=0.8)
    plt.clabel(contour, inline=True, fontsize=8, fmt='%.2f')
    
    # Заполненные контуры
    plt.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.3)
    
    # Отметка седловой точки
    saddle_x, saddle_y = 3, -13.5
    plt.plot(saddle_x, saddle_y, 'r*', markersize=20, 
             label=f'Седловая точка (3, -13.5)', zorder=5)
    
    # Отметка глобального минимума
    min_x, min_y = -4.9375, 50
    plt.plot(min_x, min_y, 'go', markersize=15, 
             label=f'Глоб. минимум (-4.94, 50)', zorder=5)
    
    # Границы области
    plt.plot([-20, 20, 20, -20, -20], [-50, -50, 50, 50, -50], 
             'k-', linewidth=2, label='Граница области')
    
    # Оформление
    plt.xlabel('x', fontsize=12)
    plt.ylabel('y', fontsize=12)
    plt.title('Линии уровня функции\n$f(x,y) = 0.01(8x^2 + 2xy - 21x - 6y - 9)$', 
              fontsize=14, pad=20)
    plt.colorbar(label='Значение функции')
    plt.legend(fontsize=10, loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.xlim(-22, 22)
    plt.ylim(-52, 52)
    
    plt.tight_layout()
    plt.savefig('contour_plot.png', dpi=300, bbox_inches='tight')
    print("✓ График сохранён как 'contour_plot.png'")
    plt.show()

def find_global_minimum():
    """
    Численный поиск глобального минимума на границе
    """
    print("\n=== Поиск глобального минимума ===\n")
    
    # Граница 1: x = -20
    y_vals = np.linspace(-50, 50, 1000)
    z1 = objective_function(-20, y_vals)
    idx1 = np.argmin(z1)
    print(f"x = -20: min = {z1[idx1]:.4f} при y = {y_vals[idx1]:.4f}")
    
    # Граница 2: x = 20
    z2 = objective_function(20, y_vals)
    idx2 = np.argmin(z2)
    print(f"x = 20: min = {z2[idx2]:.4f} при y = {y_vals[idx2]:.4f}")
    
    # Граница 3: y = -50
    x_vals = np.linspace(-20, 20, 1000)
    z3 = objective_function(x_vals, -50)
    idx3 = np.argmin(z3)
    print(f"y = -50: min = {z3[idx3]:.4f} при x = {x_vals[idx3]:.4f}")
    
    # Граница 4: y = 50
    z4 = objective_function(x_vals, 50)
    idx4 = np.argmin(z4)
    print(f"y = 50: min = {z4[idx4]:.4f} при x = {x_vals[idx4]:.4f}")
    
    # Глобальный минимум
    all_mins = [
        (z1[idx1], -20, y_vals[idx1]),
        (z2[idx2], 20, y_vals[idx2]),
        (z3[idx3], x_vals[idx3], -50),
        (z4[idx4], x_vals[idx4], 50)
    ]
    
    global_min = min(all_mins, key=lambda x: x[0])
    print(f"\n Глобальный минимум: f = {global_min[0]:.4f} в точке ({global_min[1]:.4f}, {global_min[2]:.4f})")
    
    return global_min

if __name__ == "__main__":
    # Построение графиков
    plot_contours()
    
    # Поиск минимума
    find_global_minimum()