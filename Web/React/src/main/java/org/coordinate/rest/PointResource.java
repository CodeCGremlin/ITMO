package org.coordinate.rest;

import jakarta.ejb.EJB;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.stream.Collectors;

import org.coordinate.entity.Result;
import org.coordinate.rest.AuthResource;
import org.coordinate.ejb.PointService;

@Path("/points")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class PointResource {

    private static final Logger LOGGER = Logger.getLogger(PointResource.class.getName());

    @EJB
    private PointService pointService;

    public static class PointData {
        private double x;
        private double y;
        private double r;

        public double getX() { return x; }
        public void setX(double x) { this.x = x; }
        public double getY() { return y; }
        public void setY(double y) { this.y = y; }
        public double getR() { return r; }
        public void setR(double r) { this.r = r; }
    }

    @POST
    @Path("/check")
    public Response checkPoint(PointData data, @HeaderParam("Authorization") String authHeader) {
        String token = extractToken(authHeader);
        if (token == null) {
            return Response.status(Response.Status.UNAUTHORIZED)
                    .entity(Map.of("error", "Invalid or missing token")).build();
        }
        Long userId = AuthResource.sessions.get(token);
        if (userId == null) {
            return Response.status(Response.Status.UNAUTHORIZED)
                    .entity(Map.of("error", "Session expired or invalid")).build();
        }


        if (data.getX() < -4 || data.getX() > 4 || data.getY() < -3 || data.getY() > 3 || data.getR() <= 0 || data.getR() > 10) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Map.of("error", "Invalid coordinates or radius")).build();
        }

        try {
            Result result = pointService.checkPoint(data.getX(), data.getY(), data.getR(), userId);
            Map<String, Object> resultDto = new HashMap<>();
            resultDto.put("id", result.getId());
            resultDto.put("x", result.getX());
            resultDto.put("y", result.getY());
            resultDto.put("r", result.getR());
            resultDto.put("hit", result.isHit());
            resultDto.put("timestamp", result.getCheckTime().toString());
            return Response.ok(resultDto).build();
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error in checkPoint", e);
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity(Map.of("error", "Internal server error: " + e.getMessage()))
                    .build();
        }
    }

    @GET
    @Path("/history")
    public Response getHistory(@HeaderParam("Authorization") String authHeader) {
        String token = extractToken(authHeader);
        if (token == null) {
            return Response.status(Response.Status.UNAUTHORIZED).build();
        }
        Long userId = AuthResource.sessions.get(token);
        if (userId == null) {
            return Response.status(Response.Status.UNAUTHORIZED).build();
        }

        try {
            List<Result> results = pointService.getHistory(userId);
            List<Map<String, Object>> dtos = results.stream().map(r -> {
                Map<String, Object> dto = new HashMap<>();
                dto.put("id", r.getId());
                dto.put("x", r.getX());
                dto.put("y", r.getY());
                dto.put("r", r.getR());
                dto.put("hit", r.isHit());
                dto.put("timestamp", r.getCheckTime().toString());
                return dto;
            }).collect(Collectors.toList());

            return Response.ok(dtos).build();
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error in getHistory", e);
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity(Map.of("error", "Internal server error"))
                    .build();
        }
    }

    @DELETE
    @Path("/history")
    public Response clearHistory(@HeaderParam("Authorization") String authHeader) {
        String token = extractToken(authHeader);
        if (token == null) {
            return Response.status(Response.Status.UNAUTHORIZED).build();
        }
        Long userId = AuthResource.sessions.get(token);
        if (userId == null) {
            return Response.status(Response.Status.UNAUTHORIZED).build();
        }

        try {
            pointService.clearHistory(userId);
            return Response.noContent().build();
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error in clearHistory", e);
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity(Map.of("error", "Internal server error"))
                    .build();
        }
    }

    private String extractToken(String authHeader) {
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            return authHeader.substring(7).trim();
        }
        return null;
    }
}

