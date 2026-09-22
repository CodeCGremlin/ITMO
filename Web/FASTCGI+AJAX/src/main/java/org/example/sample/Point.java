package org.example.sample;

public class Point{
    private  double x;
    private  double y;
    private  double r;

    public Point(double x,double y, double r){
        this.x = x;
        this.y = y;
        this.r = r;
    }




    public double getX() {
        return x;
    }
    public double getY() {
        return y;
    }
    public double getR() {
        return r;
    }

    public void setX(double x) {
        this.x = x;
    }
    public void setY(double y) {
        this.y = y;
    }
    public void setR(double r)
    {
        this.r = r;
    }

    @Override
    public String toString() {
        return String.format("Point{x=%.2f, y=%.2f, r=%.2f}", x, y, r);
    }
}

