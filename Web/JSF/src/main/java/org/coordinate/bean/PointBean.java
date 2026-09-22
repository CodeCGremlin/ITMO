//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package org.coordinate.bean;

import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.SessionScoped;
import jakarta.faces.application.FacesMessage;
import jakarta.faces.context.FacesContext;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import java.io.Serializable;
import java.util.Map;
import org.coordinate.service.AreaCheck;
//
import jakarta.inject.Inject;
import org.coordinate.monitor.JmxMonitorManager;

@Named("PointBean")
@SessionScoped
public class PointBean implements Serializable {

    @Inject
    private JmxMonitorManager jmxMonitor;

    private Double x = null;
    private Double y = null;
    private Double r = null;
    @Inject
    private AreaCheck areaCheckService;
    @Inject
    private ResultBean resultBean;

    @PostConstruct
    public void init() {
    }

    public void keepValues() {
        FacesContext fc = FacesContext.getCurrentInstance();
        Map<String, String> params = fc.getExternalContext().getRequestParameterMap();
        if (params.containsKey("hiddenX") && params.containsKey("hiddenY")) {
            String hx = (String)params.get("hiddenX");
            String hy = (String)params.get("hiddenY");
            if (hx != null && !hx.trim().isEmpty() && hy != null && !hy.trim().isEmpty()) {
                try {
                    this.x = Double.valueOf(hx);
                    this.y = Double.valueOf(hy);
                    return;
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }

    }

    public String checkPoint() {
        this.keepValues();
        if (this.x == null) {
            FacesContext.getCurrentInstance().addMessage("pointForm:xInput", new FacesMessage(FacesMessage.SEVERITY_ERROR, "⚠️ Please select X", (String)null));
            return null;
        } else if (this.y == null) {
            FacesContext.getCurrentInstance().addMessage("pointForm:yInput", new FacesMessage(FacesMessage.SEVERITY_ERROR, "⚠️ Please enter Y coordinate", (String)null));
            return null;
        } else if (!(this.y < (double)-5.0F) && !(this.y > (double)3.0F)) {
            if (this.r == null) {
                FacesContext.getCurrentInstance().addMessage("pointForm:rInput", new FacesMessage(FacesMessage.SEVERITY_ERROR, "⚠️ Please select R", (String)null));
                return null;
            } else {
                this.processSinglePoint(this.x);
                return null;
            }
        } else {
            FacesContext.getCurrentInstance().addMessage("pointForm:yInput", new FacesMessage(FacesMessage.SEVERITY_ERROR, "⚠️ Y must be between -5 and 3", (String)null));
            return null;
        }
    }

    private void processSinglePoint(Double xVal) {
        if (this.validate(xVal, this.y, this.r)) {
            boolean hit = this.areaCheckService.checkHit(xVal, this.y, this.r);
            this.jmxMonitor.processClick(hit);
            this.resultBean.addResult(xVal, this.y, this.r, hit);
        }

    }

    private boolean validate(Double curX, Double curY, Double curR) {
        return curX != null && curY != null && curR != null && curY >= (double)-5.0F && curY <= (double)3.0F;
    }

    public void clearForm() {
        this.x = null;
        this.y = null;
        this.r = null;
        FacesContext.getCurrentInstance().addMessage((String)null, new FacesMessage(FacesMessage.SEVERITY_INFO, "✓ Form cleared successfully", (String)null));
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
}
