// Исправленный AuthResource.java

package org.coordinate.rest;

import jakarta.ejb.EJB;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;


import org.coordinate.entity.User;
import org.coordinate.entity.Result;
import org.coordinate.ejb.AuthService;

@Path("/auth")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class AuthResource {

    @EJB
    private AuthService authService;

    public static final Map<String, Long> sessions = new ConcurrentHashMap<>();

    @POST
    @Path("/login")
    public Response login(Credentials credentials) {
        if (authService.authenticate(credentials.getUsername(), credentials.getPassword())) {
            String token = UUID.randomUUID().toString();
            User user = authService.getUserByUsername(credentials.getUsername());
            if (user != null) {
                sessions.put(token, user.getId());

                Map<String, Object> response = new HashMap<>();
                response.put("success", true);
                response.put("token", token);
                response.put("user", credentials.getUsername());
                response.put("userId", user.getId());
                return Response.ok(response).build();
            }
        }
        return Response.status(Response.Status.UNAUTHORIZED)
                .entity(Map.of("success", false, "message", "Invalid credentials"))
                .build();
    }

    @POST
    @Path("/logout")
    public Response logout(@HeaderParam("Authorization") String authHeader) {
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            sessions.remove(token);
            return Response.ok().build();
        }
        return Response.status(Response.Status.UNAUTHORIZED).build();
    }

    @POST
    @Path("/register")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)

    public Response register(Credentials credentials) {
        try {

            if (credentials.getUsername() == null || credentials.getUsername().isEmpty() ||
                    credentials.getPassword() == null || credentials.getPassword().isEmpty()) {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Map.of("success", false, "message", "Username and password are required"))
                        .build();
            }

            User newUser = authService.registerUser(credentials.getUsername(), credentials.getPassword());

            return Response.status(Response.Status.CREATED)
                    .entity(Map.of("success", true, "message", "User registered", "userId", newUser.getId()))
                    .build();
        } catch (RuntimeException ex) {

            return Response.status(Response.Status.CONFLICT)
                    .entity(Map.of("success", false, "message", ex.getMessage()))
                    .build();
        } catch (Exception ex) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity(Map.of("success", false, "message", "Registration failed"))
                    .build();
        }
    }


    public static class Credentials {
        private String username;
        private String password;

        public String getUsername() { return username; }
        public void setUsername(String username) { this.username = username; }
        public String getPassword() { return password; }
        public void setPassword(String password) { this.password = password; }
    }
}