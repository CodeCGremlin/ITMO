package server.network;

import server.handler.ClientHandler;
import server.manager.CollectionManager;
import server.manager.AuthManager;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.ForkJoinPool;






public class TcpServer {
    private final int port;
    private final ExecutorService readPool;
    private final ForkJoinPool processPool;
    private final CollectionManager collectionManager;
    private final AuthManager authManager;

    public TcpServer(int port, ExecutorService readPool, ForkJoinPool processPool,
                     CollectionManager cm, AuthManager am) {
        this.port = port;
        this.readPool = readPool;
        this.processPool = processPool;
        this.collectionManager = cm;
        this.authManager = am;
    }

    public void start() {
        try (ServerSocket serverSocket = new ServerSocket(port)) {
            System.out.println(" Ожидание подключений на порту " + port + "...");

            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println(" Подключился клиент: " + clientSocket.getRemoteSocketAddress());

                new Thread(() -> {
                    ClientHandler handler = new ClientHandler(
                            clientSocket, collectionManager, authManager, readPool, processPool);
                    handler.run();
                }).start();
            }
        } catch (IOException e) {
            System.err.println("xxx Ошибка сервера: " + e.getMessage());
            e.printStackTrace();
        }
    }
}