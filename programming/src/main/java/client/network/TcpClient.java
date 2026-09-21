package client.network;

import common.command.CommandRequest;
import common.command.CommandResponse;
import java.io.*;
import java.net.Socket;
import java.net.ConnectException;


public class TcpClient {
    private final String host;
    private final int port;
    private Socket socket;
    private ObjectOutputStream out;
    private ObjectInputStream in;
    private String login;
    private String password;

    public TcpClient(String host, int port) {
        this.host = host;
        this.port = port;
    }
    public boolean connect() {
        int attempts = 3;
        while (attempts > 0) {
            try {
                socket = new Socket(host, port);
                out = new ObjectOutputStream(socket.getOutputStream());
                in = new ObjectInputStream(socket.getInputStream());
                return true;
            } catch (ConnectException e) {
                System.out.println("сервер недоступен, попытка подключения... (" + attempts + ")");
                attempts--;
                try { Thread.sleep(2000); } catch (InterruptedException ignored) {}
            } catch (IOException e) {
                e.printStackTrace();
                return false;
            }
        }
        return false;
    }
    public void setCredentials(String login, String password) {
        this.login = login;
        this.password = password;
    }
    public CommandResponse send(CommandRequest request) {
        try {
            out.writeObject(request);
            out.flush();
            return (CommandResponse) in.readObject();
        } catch (IOException | ClassNotFoundException e) {
            return new CommandResponse("ошибка соединения", null, false);
        }
    }
    public void close() {
        try {
            if (socket != null) socket.close();
        } catch (IOException e) { e.printStackTrace(); }
    }

    public String getLogin() { return login; }
    public String getPassword() { return password; }
}