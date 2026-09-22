package org.coordinate.monitor;

public interface ClickIntervalMBean {
    double getAverageIntervalMs();
    long getTotalIntervalsRecorded();
    void registerInterval(long intervalMs);
}