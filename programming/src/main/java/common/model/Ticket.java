package common.model;

import common.model.enums.TicketType;
import java.io.Serializable;
import java.time.ZonedDateTime;


public class Ticket implements Comparable<Ticket>, Serializable {

    private Long id;
    private String name;
    private Coordinates coordinates;
    private ZonedDateTime creationDate;
    private Long price;
    private Boolean refundable;
    private TicketType type;
    private Person person;
    private String creatorLogin;

    public Ticket() {}

    public Ticket(String name, Coordinates coordinates, Long price, Boolean refundable,
                  TicketType type, Person person, String creatorLogin) {
        this.name = name;
        this.coordinates = coordinates;
        this.price = price;
        this.refundable = refundable;
        this.type = type;
        this.person = person;
        this.creatorLogin = creatorLogin;
        this.creationDate = ZonedDateTime.now();
    }

    @Override
    public int compareTo(Ticket other) {
        if (this.name == null && other.name == null) return 0;
        if (this.name == null) return -1;
        if (other.name == null) return 1;
        return this.name.compareTo(other.name);
    }


    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public Coordinates getCoordinates() { return coordinates; }
    public void setCoordinates(Coordinates coordinates) { this.coordinates = coordinates; }
    public ZonedDateTime getCreationDate() { return creationDate; }
    public void setCreationDate(ZonedDateTime creationDate) { this.creationDate = creationDate; }
    public Long getPrice() { return price; }
    public void setPrice(Long price) { this.price = price; }
    public Boolean getRefundable() { return refundable; }
    public void setRefundable(Boolean refundable) { this.refundable = refundable; }
    public TicketType getType() { return type; }
    public void setType(TicketType type) { this.type = type; }
    public Person getPerson() { return person; }
    public void setPerson(Person person) { this.person = person; }
    public String getCreatorLogin() { return creatorLogin; }
    public void setCreatorLogin(String creatorLogin) { this.creatorLogin = creatorLogin; }

    public boolean isValid() {
        return name != null && !name.isEmpty() &&
                coordinates != null && coordinates.isValid() &&
                price != null && price > 0 &&
                type != null &&
                person != null && person.getHeight() != null && person.getHeight() > 0 &&
                person.getPassportID() != null && !person.getPassportID().isEmpty() &&
                person.getEyeColor() != null;
    }

    @Override
    public String toString() {
        return String.format("Ticket{id=%d, name='%s', price=%d, type=%s, person=%s}",
                id, name, price, type, person);
    }
}