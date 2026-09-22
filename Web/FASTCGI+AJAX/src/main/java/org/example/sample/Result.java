package org.example.sample;

import java.time.LocalDateTime;

public class Result {
    private Point point;
    private boolean hit;
    private LocalDateTime requestTime;
    private long executionTime;

    public Result(Point point, boolean hit, LocalDateTime requestTime, long executionTime) {
        this.point = point;
        this.hit = hit;
        this.requestTime = requestTime;
        this.executionTime = executionTime;
    }

    public String toJson() {

        java.text.DecimalFormat df = new java.text.DecimalFormat("0.00");
        df.setDecimalFormatSymbols(new java.text.DecimalFormatSymbols(java.util.Locale.US));

        return String.format(
                "{\"x\":%s,\"y\":%s,\"r\":%s,\"hit\":%s,\"current_time\":\"%s\",\"execution_time\":%d}",
                df.format(point.getX()),
                df.format(point.getY()),
                df.format(point.getR()),
                hit ? "true" : "false",
                requestTime.format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")),
                executionTime
        );
    }

    public Point getPoint() { return point; }
    public boolean isHit() { return hit; }
    public LocalDateTime getRequestTime() { return requestTime; }
    public long getExecutionTime() { return executionTime; }
}