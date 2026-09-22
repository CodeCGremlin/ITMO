//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package org.coordinate.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.io.Serializable;
import java.time.LocalDateTime;

@Entity
@Table(
        name = "check_results"
)
public class Result implements Serializable {
    @Id
    @GeneratedValue(
            strategy = GenerationType.IDENTITY
    )
    private Long id;
    @Column(
            nullable = false
    )
    private Double x;
    @Column(
            nullable = false
    )
    private Double y;
    @Column(
            nullable = false
    )
    private Double r;
    @Column(
            nullable = false
    )
    private Boolean hit;
    @Column(
            name = "check_time",
            nullable = false
    )
    private LocalDateTime checkTime;
    @Column(
            name = "execution_time"
    )
    private Long executionTime;

    public Result() {
    }

    public Result(Double x, Double y, Double r, Boolean hit, LocalDateTime checkTime, Long executionTime) {
        this.x = x;
        this.y = y;
        this.r = r;
        this.hit = hit;
        this.checkTime = checkTime;
        this.executionTime = executionTime;
    }

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Double getX() {
        return this.x;
    }

    public void setX(Double x) {
        this.x = x;
    }

    public Double getY() {
        return this.y;
    }

    public void setY(Double y) {
        this.y = y;
    }

    public Double getR() {
        return this.r;
    }

    public void setR(Double r) {
        this.r = r;
    }

    public Boolean getHit() {
        return this.hit;
    }

    public LocalDateTime getCheckTime() {
        return this.checkTime;
    }

    public Long getExecutionTime() {
        return this.executionTime;
    }

    public void setExecutionTime(Long executionTime) {
        this.executionTime = executionTime;
    }
}
