package server;

import server.manager.DatabaseManager;
import server.manager.CollectionManager;
import server.manager.AuthManager;
import server.network.TcpServer;

import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ForkJoinPool;


public class ServerMain {
    //бд
    private static final String DB_URL = "jdbc:postgresql://helios:5432/studs";
    private static final String DB_USER = "s503517";
    private static final String DB_PASS = "oFhLBheeWeX4HGbu";

    //сервер
    private static final int PORT = 32318;

    //потоки чтен и обраб
    private static final int READ_POOL_SIZE = 4;
    private static final int PROCESS_POOL_SIZE = 8;
    private static final ExecutorService READ_POOL = Executors.newFixedThreadPool(READ_POOL_SIZE);
    private static final ForkJoinPool PROCESS_POOL = new ForkJoinPool(PROCESS_POOL_SIZE);

    public static void main(String[] args) {
        System.setProperty("file.encoding", "UTF-8");
        Locale.setDefault(Locale.ENGLISH);

        System.out.println("Запуск сервера");
        System.out.println("порт: " + PORT);
        System.out.println("БД: " + DB_URL + " user: " + DB_USER);
        System.out.println("пул чтения: FixedThreadPool(" + READ_POOL_SIZE + ")");
        System.out.println("пул обработки: ForkJoinPool(" + PROCESS_POOL_SIZE + ")");

        try {
            DatabaseManager dbManager = new DatabaseManager(DB_URL, DB_USER, DB_PASS);
            CollectionManager collectionManager = new CollectionManager(dbManager);
            AuthManager authManager = new AuthManager(dbManager);

            TcpServer tcpServer = new TcpServer(PORT, READ_POOL, PROCESS_POOL, collectionManager, authManager);

            System.out.println("сервер готов к приему соединений на порту " + PORT);
            tcpServer.start();

        } catch (Exception e) {
            System.err.println("xxx критическая ошибка при запуске сервера:");
            e.printStackTrace();
            System.exit(1);
        }
    }
}