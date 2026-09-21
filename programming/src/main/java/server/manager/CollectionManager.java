package server.manager;

import common.model.Ticket;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.stream.Collectors;

public class CollectionManager {
    private final Map<Long, Ticket> collection = new LinkedHashMap<>();
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    private final LocalDateTime initializationDate = LocalDateTime.now();
    private DatabaseManager dbManager;

    public CollectionManager(DatabaseManager dbManager) {
        this.dbManager = dbManager;
        loadFromDb();
    }

    private void loadFromDb() {
        lock.writeLock().lock();
        try {
            List<Ticket> tickets = dbManager.loadAll();
            for (Ticket t : tickets) {
                collection.put(t.getId(), t);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public Collection<Ticket> getSortedCollection() {
        lock.readLock().lock();
        try {
            return collection.values().stream()
                    .sorted()
                    .collect(Collectors.toList());
        } finally {
            lock.readLock().unlock();
        }
    }

    public String getInfo() {
        lock.readLock().lock();
        try {
            return "Тип: " + collection.getClass().getSimpleName() +
                    ", Дата инициализации: " + initializationDate +
                    ", Размер: " + collection.size();
        } finally {
            lock.readLock().unlock();
        }
    }

    public boolean insert(Ticket ticket, String login) {
        lock.writeLock().lock();
        try {
            long id = dbManager.insertTicket(ticket);
            if (id != -1) {
                ticket.setId(id);
                collection.put(id, ticket);
                return true;
            }
            return false;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public boolean update(Ticket ticket, String login) {
        lock.writeLock().lock();
        try {
            Ticket existing = collection.get(ticket.getId());
            if (existing != null && existing.getCreatorLogin().equals(login)) {
                ticket.setCreatorLogin(login);
                if (dbManager.updateTicket(ticket)) {
                    collection.put(ticket.getId(), ticket);
                    return true;
                }
            }
            return false;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public boolean removeKey(Long key, String login) {
        lock.writeLock().lock();
        try {
            Ticket t = collection.get(key);
            if (t != null && t.getCreatorLogin().equals(login)) {
                if (dbManager.deleteTicket(key)) {
                    collection.remove(key);
                    return true;
                }
            }
            return false;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void clear(String login) {
        lock.writeLock().lock();
        try {

            List<Long> toRemove = collection.values().stream()
                    .filter(t -> t.getCreatorLogin().equals(login))
                    .map(Ticket::getId)
                    .collect(Collectors.toList());

            for (Long id : toRemove) {
                dbManager.deleteTicket(id);
                collection.remove(id);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public boolean removeLower(Ticket ticket, String login) {
        lock.writeLock().lock();
        try {
            List<Long> toRemove = collection.values().stream()
                    .filter(t -> t.getCreatorLogin().equals(login) && t.compareTo(ticket) < 0)
                    .map(Ticket::getId)
                    .collect(Collectors.toList());
            boolean changed = false;
            for (Long id : toRemove) {
                if (dbManager.deleteTicket(id)) {
                    collection.remove(id);
                    changed = true;
                }
            }
            return changed;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public Double averageOfPrice() {
        lock.readLock().lock();
        try {
            return collection.values().stream()
                    .mapToLong(Ticket::getPrice)
                    .average()
                    .orElse(0.0);
        } finally {
            lock.readLock().unlock();
        }
    }

    public String filterLessThanPrice(Long value) {
        lock.readLock().lock();
        try {
            return collection.values().stream()
                    .filter(t -> t.getPrice() != null && t.getPrice() < value)
                    .map(Ticket::getName)
                    .collect(Collectors.joining(", "));
        } finally {
            lock.readLock().unlock();
        }
    }
    public boolean replaceIfGreater(Long key, Ticket newTicket, String login) {
        lock.writeLock().lock();
        try {
            Ticket old = collection.get(key);
            if (old != null && old.getCreatorLogin().equals(login) && newTicket.compareTo(old) > 0) {
                newTicket.setId(key);
                newTicket.setCreatorLogin(login);
                if (dbManager.updateTicket(newTicket)) {
                    collection.put(key, newTicket);
                    return true;
                }
            }
            return false;
        } finally {
            lock.writeLock().unlock();
        }
    }
}