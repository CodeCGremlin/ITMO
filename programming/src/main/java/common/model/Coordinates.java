package common.model;

import java.io.Serializable;


public class Coordinates implements Serializable {
;

    private Integer x;
    private Double y;


    public Coordinates(Integer x, Double y) {
        this.x = x;
        this.y = y;
    }


    public Integer getX() { return x; }
    public void setX(Integer x) { this.x = x; }

    public Double getY() { return y; }
    public void setY(Double y) { this.y = y; }

    public boolean isValid() {
        return x != null && x <= 630 && y != null;
    }

    @Override
    public String toString() {
        return String.format("Coordinates{x=%d, y=%.2f}", x, y);
    }
}