package server.manager;

import common.model.Ticket;
import common.model.Coordinates;
import common.model.Person;
import common.model.enums.*;
import java.sql.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;



public class DatabaseManager {
    private final String url;
    private final String user;
    private final String password;

    public DatabaseManager(String url, String user, String password) {
        this.url = url;
        this.user = user;
        this.password = password;
    }

    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(url, user, password);
    }

    public String hashPassword(String pass) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(pass.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) sb.append(String.format("%02x", b));
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    public boolean authenticate(String login, String password) {

        String sql = "SELECT password_hash FROM lab7_users WHERE username = ?";
        try (Connection conn = getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, login);
            ResultSet rs = ps.executeQuery();
            if (rs.next()) {
                return rs.getString("password_hash").equals(hashPassword(password));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }

    public List<Ticket> loadAll() {
        List<Ticket> list = new ArrayList<>();
        String sql = "SELECT * FROM ticket";
        try (Connection conn = getConnection();
             Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery(sql)) {

            while (rs.next()) {
                Ticket t = new Ticket();
                t.setId(rs.getLong("id"));
                t.setName(rs.getString("name"));
                t.setCoordinates(new Coordinates(
                        rs.getObject("coordinates_x") != null ? rs.getInt("coordinates_x") : null,
                        rs.getDouble("coordinates_y")
                ));

                t.setCreationDate(rs.getTimestamp("creation_date").toLocalDateTime().atZone(java.time.ZoneId.of("UTC")));
                t.setPrice(rs.getLong("price"));
                t.setRefundable(rs.getObject("refundable") != null ? rs.getBoolean("refundable") : null);
                t.setType(TicketType.valueOf(rs.getString("type")));
                t.setPerson(new Person(
                        rs.getObject("person_height") != null ? rs.getInt("person_height") : null,
                        rs.getString("person_passport_id"),
                        EyeColor.valueOf(rs.getString("person_eye_color")),
                        rs.getString("person_hair_color") != null ? HairColor.valueOf(rs.getString("person_hair_color")) : null
                ));
                t.setCreatorLogin(rs.getString("creator_login"));
                list.add(t);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    public long insertTicket(Ticket ticket) {
        String sql = "INSERT INTO ticket (name, coordinates_x, coordinates_y, creation_date, price, refundable, type, " +
                "person_height, person_passport_id, person_eye_color, person_hair_color, creator_login) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
        try (Connection conn = getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {

            ps.setString(1, ticket.getName());
            ps.setInt(2, ticket.getCoordinates().getX());
            ps.setDouble(3, ticket.getCoordinates().getY());
            ps.setTimestamp(4, Timestamp.from(ticket.getCreationDate().toInstant()));
            ps.setLong(5, ticket.getPrice());
            ps.setObject(6, ticket.getRefundable());
            ps.setString(7, ticket.getType().name());
            ps.setObject(8, ticket.getPerson().getHeight());
            ps.setString(9, ticket.getPerson().getPassportID());
            ps.setString(10, ticket.getPerson().getEyeColor().name());
            ps.setString(11, ticket.getPerson().getHairColor() != null ? ticket.getPerson().getHairColor().name() : null);
            ps.setString(12, ticket.getCreatorLogin());

            ps.executeUpdate();
            ResultSet rs = ps.getGeneratedKeys();
            if (rs.next()) return rs.getLong(1);
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return -1;
    }

    public boolean deleteTicket(Long id) {
        String sql = "DELETE FROM ticket WHERE id = ?";
        try (Connection conn = getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, id);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }

    public boolean updateTicket(Ticket ticket) {
        String sql = "UPDATE ticket SET name=?, coordinates_x=?, coordinates_y=?, price=?, refundable=?, type=?, " +
                "person_height=?, person_passport_id=?, person_eye_color=?, person_hair_color=? WHERE id=?";
        try (Connection conn = getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, ticket.getName());
            ps.setInt(2, ticket.getCoordinates().getX());
            ps.setDouble(3, ticket.getCoordinates().getY());
            ps.setLong(4, ticket.getPrice());
            ps.setObject(5, ticket.getRefundable());
            ps.setString(6, ticket.getType().name());
            ps.setObject(7, ticket.getPerson().getHeight());
            ps.setString(8, ticket.getPerson().getPassportID());
            ps.setString(9, ticket.getPerson().getEyeColor().name());
            ps.setString(10, ticket.getPerson().getHairColor() != null ? ticket.getPerson().getHairColor().name() : null);
            ps.setLong(11, ticket.getId());
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }
}