
package org.coordinate.ejb;

import jakarta.ejb.Stateless;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.TypedQuery;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import jakarta.persistence.NoResultException;

import org.coordinate.entity.User;

@Stateless
public class AuthService {

    @PersistenceContext(unitName = "CoordinatePU")
    private EntityManager em;

    public String hashPassword(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hashedBytes = md.digest(password.getBytes());
            return Base64.getEncoder().encodeToString(hashedBytes);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("Error hashing password", e);
        }
    }

    public boolean authenticate(String username, String password) {
        try {
            TypedQuery<User> query = em.createQuery(
                    "SELECT u FROM User u WHERE u.username = :username", User.class);
            query.setParameter("username", username);
            User user = query.getSingleResult();
            String hashedInput = hashPassword(password);
            return hashedInput.equals(user.getPasswordHash());
        } catch (NoResultException e) {
            return false;
        }
    }

    public User getUserByUsername(String username) {
        try {
            TypedQuery<User> query = em.createQuery(
                    "SELECT u FROM User u WHERE u.username = :username", User.class);
            query.setParameter("username", username);
            return query.getSingleResult();
        } catch (Exception e) {
            return null;
        }
    }

    public User registerUser(String username, String password) {
        TypedQuery<User> existingUserQuery = em.createQuery(
                "SELECT u FROM User u WHERE u.username = :username", User.class);
        existingUserQuery.setParameter("username", username);
        if (!existingUserQuery.getResultList().isEmpty()) {
            throw new RuntimeException("Username already exists");
        }

        String hashedPassword = hashPassword(password);
        User newUser = new User(username, hashedPassword);
        em.persist(newUser);
        em.flush();
        return newUser;
    }
}