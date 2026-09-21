package client;

import client.network.TcpClient;
import client.ui.InteractiveClient;
import java.util.Locale;

public class ClientMain {
    private static final String DEFAULT_HOST = "localhost";
    private static final int DEFAULT_PORT = 24242;

    public static void main(String[] args) {
        System.setProperty("file.encoding", "UTF-8");
        Locale.setDefault(Locale.ENGLISH);

        String host = DEFAULT_HOST;
        int port = DEFAULT_PORT;

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--host") && i + 1 < args.length) {
                host = args[i + 1];
            }
            if (args[i].equals("--port") && i + 1 < args.length) {
                port = Integer.parseInt(args[i + 1]);
            }
        }
        TcpClient client = new TcpClient(host, port);
        if (client.connect()) {
            InteractiveClient ui = new InteractiveClient(client);
            ui.start();
        } else {
            System.out.println("Не удалось подключиться к серверу " + host + ":" + port);
        }
    }
}