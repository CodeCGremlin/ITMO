package org.example.util;

public class AreaChecker {
    public static boolean checkHit(double x, double y, double r) {
        // 2-я четверть круга
        if (x <= 0 && y >= 0) {
            return (x * x + y * y) <= (r * r);
        }
        // 1-я четверть треугольник
        else if (x >= 0 && y >= 0) {
            return (x <= r) && (y <= r / 2.0) && (2 * y <= (r - x));
        }
        // 4-я четверть квадрат
        else if (x >= 0 && y <= 0) {
            return (x <= r) && (y >= -r);
        }
        return false;
    }
}
