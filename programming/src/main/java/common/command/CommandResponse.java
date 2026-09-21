package common.command;

import java.io.Serializable;

public class CommandResponse implements Serializable {
    private String message;
    private Object data;
    private boolean success;

    public CommandResponse(String message, Object data, boolean success) {
        this.message = message;
        this.data = data;
        this.success = success;
    }

    public String getMessage() { return message; }
    public Object getData() { return data; }
    public boolean isSuccess() { return success; }
}