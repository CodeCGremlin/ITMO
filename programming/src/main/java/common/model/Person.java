package common.model;

import common.model.enums.EyeColor;
import common.model.enums.HairColor;
import java.io.Serializable;

public class Person implements Serializable {
    private Integer height;
    private String passportID;
    private EyeColor eyeColor;
    private HairColor hairColor;

    public Person(Integer height, String passportID, EyeColor eyeColor, HairColor hairColor) {
        this.height = height;
        this.passportID = passportID;
        this.eyeColor = eyeColor;
        this.hairColor = hairColor;
    }

    public Integer getHeight() { return height; }
    public void setHeight(Integer height) { this.height = height; }
    public String getPassportID() { return passportID; }
    public void setPassportID(String passportID) { this.passportID = passportID; }
    public EyeColor getEyeColor() { return eyeColor; }
    public void setEyeColor(EyeColor eyeColor) { this.eyeColor = eyeColor; }
    public HairColor getHairColor() { return hairColor; }
    public void setHairColor(HairColor hairColor) { this.hairColor = hairColor; }

    @Override
    public String toString() {
        return String.format("Person{height=%d, passportID='%s', eyeColor=%s, hairColor=%s}",
                height, passportID, eyeColor, hairColor);
    }
}