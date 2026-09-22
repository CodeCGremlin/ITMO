package org.coordinate.monitor;

import javax.management.MBeanNotificationInfo;
import javax.management.Notification;
import javax.management.NotificationBroadcasterSupport;

public class PointStats extends NotificationBroadcasterSupport implements PointStatsMBean {
    private int totalPoints = 0;
    private int totalHits = 0;
    private int consecutiveMisses = 0;
    private int notificationSequence = 1;

    @Override
    public synchronized int getTotalPoints() {
        return totalPoints;
    }

    @Override
    public synchronized int getTotalHits() {
        return totalHits;
    }

    @Override
    public synchronized int getConsecutiveMisses() {
        return consecutiveMisses;
    }

    @Override
    public synchronized void registerPoint(boolean isHit) {
        totalPoints++;
        if (isHit) {
            totalHits++;
            consecutiveMisses = 0; // Сброс счётчика промахов при попадании
        } else {
            consecutiveMisses++;
            // Отправка оповещения при 3 промахах подряд
            if (consecutiveMisses == 3) {
                Notification notification = new Notification(
                        "lab3.miss.alert",
                        this,
                        notificationSequence++,
                        System.currentTimeMillis(),
                        "Внимание: совершено 3 промаха подряд!"
                );
                sendNotification(notification);
            }
        }
    }

    @Override
    public MBeanNotificationInfo[] getNotificationInfo() {
        String[] types = new String[]{"lab3.miss.alert"};
        String name = Notification.class.getName();
        String description = "Оповещение о серии из 3 промахов";
        return new MBeanNotificationInfo[]{new MBeanNotificationInfo(types, name, description)};
    }
}