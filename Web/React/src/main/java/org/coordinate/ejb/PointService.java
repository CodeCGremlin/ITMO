package org.coordinate.ejb;

import jakarta.ejb.Stateless;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.TypedQuery;

import org.coordinate.entity.Result;
import org.coordinate.entity.User;

import java.time.LocalDateTime;
import java.util.List;

@Stateless
public class PointService {

    @PersistenceContext(unitName = "CoordinatePU")
    private EntityManager em;

    public Result checkPoint(double x, double y, double r, Long userId) {
        boolean hit = checkArea(x, y, r);

        Result result = new Result();
        result.setX(x);
        result.setY(y);
        result.setR(r);
        result.setHit(hit);
        result.setCheckTime(LocalDateTime.now());

        User user = em.find(User.class, userId);
        if (user != null) {
            result.setUser(user);
            em.persist(result);
        }

        return result;
    }

    private boolean checkArea(double x, double y, double r) {
        if (r <= 0) return false;

        // I
        if (x >= 0 && y >= 0) {
            return (x * x + y * y) <= (r * r);
        }

        //II
        else if (x <= 0 && y >= 0) {
            return (x >= -r) && (y <= x + r);
        }

        //III
        else if (x <= 0 && y <= 0) {
            return (x >= -r/2.0) && (x <= 0) &&
                    (y >= -r) && (y <= 0);
        }
        else {
            return false;
        }
    }


    public List<Result> getHistory(Long userId) {
        TypedQuery<Result> query = em.createQuery(
                "SELECT r FROM Result r WHERE r.user.id = :userId ORDER BY r.checkTime DESC",
                Result.class);
        query.setParameter("userId", userId);
        return query.getResultList();
    }

    public void clearHistory(Long userId) {
        em.createQuery("DELETE FROM Result r WHERE r.user.id = :userId")
                .setParameter("userId", userId)
                .executeUpdate();
    }
}