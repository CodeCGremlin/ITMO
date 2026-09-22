package org.coordinate.monitor;

public interface PointStatsMBean {
    int getTotalPoints();
    int getTotalHits();
    int getConsecutiveMisses();
    void registerPoint(boolean isHit);
}