package org.example;

import org.example.sample.Point;

public class AreaCheck {

    public static final String VALIDATION_SUCCESS = "Validation successful";
    public static final String INVALID_R = "Invalid R value. Must be between 1 and 3 with step 0.5";
    public static final String INVALID_X = "Invalid X value. Must be between -5 and 3";
    public static final String INVALID_Y = "Invalid Y value. Must be between -3 and 3";

    public static boolean checkHit(Point point) {
        double x = point.getX();
        double y = point.getY();
        double r = point.getR();


        // 2 ч четверть круга
        if (x <= 0 && y >= 0) {
            return (x * x + y * y) <= (r * r);
        }
        // 1 ч треугольник
        else if (x >= 0 && y >= 0) {
            return (x <= r) && (y <= r / 2.0) && (2 * y <= (r - x));
        }
        // 4 ч квадрат
        else if (x >= 0 && y <= 0) {
            return (x <= r) && (y >= -r);
        }
        return false;
    }

    // Валидация
    public static boolean validatePoint(Point point) {
        double x = point.getX();
        double y = point.getY();
        double r = point.getR();

        // R  1, 3   шаг 0.5
        if (r < 1 || r > 3 || (r * 2) % 1 != 0) return false;

        // X -5, 3
        if (x < -5 || x > 3) return false;

        // Y -3, 3
        if (y < -3 || y > 3) return false;

        return true;
    }
}