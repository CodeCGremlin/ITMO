package common.command;

import java.io.Serializable;


public class CommandRequest implements Serializable {
    private static final long serialVersionUID = 1L;
    private CommandType type;
    private Object argument;
    private String login;
    private String password;

    public CommandRequest(CommandType type, Object argument, String login, String password) {
        this.type = type;
        this.argument = argument;
        this.login = login;
        this.password = password;
    }

    public CommandType getType() { return type; }
    public Object getArgument() { return argument; }
    public String getLogin() { return login; }
    public String getPassword() { return password; }
}