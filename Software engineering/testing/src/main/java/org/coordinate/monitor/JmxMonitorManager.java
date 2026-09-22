package org.coordinate.monitor;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import java.lang.management.ManagementFactory;
import javax.management.MBeanServer;
import javax.management.ObjectName;

@ApplicationScoped
public class JmxMonitorManager {
    private MBeanServer mBeanServer;
    private ObjectName statsName;
    private ObjectName intervalName;

    private PointStats pointStats;
    private ClickInterval clickInterval;

    private long lastClickTime = 0;

    @PostConstruct
    public void init() {
        mBeanServer = ManagementFactory.getPlatformMBeanServer();
        pointStats = new PointStats();
        clickInterval = new ClickInterval();

        try {
            statsName = new ObjectName("org.coordinate:type=PointStats");
            intervalName = new ObjectName("org.coordinate:type=ClickInterval");

            mBeanServer.registerMBean(pointStats, statsName);
            mBeanServer.registerMBean(clickInterval, intervalName);
        } catch (Exception e) {
            System.err.println("Ошибка регистрации MBean: " + e.getMessage());
        }
    }

    @PreDestroy
    public void destroy() {
        try {
            if (statsName != null) mBeanServer.unregisterMBean(statsName);
            if (intervalName != null) mBeanServer.unregisterMBean(intervalName);
        } catch (Exception e) {
            System.err.println("Ошибка снятия MBean: " + e.getMessage());
        }
    }


    public synchronized void processClick(boolean isHit) {
        long now = System.currentTimeMillis();

        if (lastClickTime > 0) {
            long interval = now - lastClickTime;
            clickInterval.registerInterval(interval);
        }
        lastClickTime = now;

        pointStats.registerPoint(isHit);
    }
}