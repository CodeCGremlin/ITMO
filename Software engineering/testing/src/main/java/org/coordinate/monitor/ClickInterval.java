package org.coordinate.monitor;

public class ClickInterval implements ClickIntervalMBean {
    private long totalIntervalSum = 0;
    private long totalIntervals = 0;

    @Override
    public synchronized double getAverageIntervalMs() {
        if (totalIntervals == 0) return 0.0;
        return (double) totalIntervalSum / totalIntervals;
    }

    @Override
    public synchronized long getTotalIntervalsRecorded() {
        return totalIntervals;
    }

    @Override
    public synchronized void registerInterval(long intervalMs) {
        if (intervalMs >= 0) {
            totalIntervalSum += intervalMs;
            totalIntervals++;
        }
    }
}