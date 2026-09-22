package org.coordinate.ejb;

import jakarta.ejb.Stateless;

@Stateless
public class AreaCheckBean {


    public boolean checkHit(double x, double y, double r) {

        if (r <= 0) return false;


        if (x >= 0 && y >= 0) { // I
            return (x * x + y * y) <= r * r;
        }
        if (x <= 0 && y >= 0) { // II
            return (x >= -r) && (x <= 0) && (y >= 0) && (y <= r);
        }
        if (x >= 0 && y <= 0) { // IV
            return (x >= 0) && (x <= r/2) && (y >= -r) && (y <= 0) && (y >= -x/2 - r/2);
        }
        // III
        return false;
    }
}