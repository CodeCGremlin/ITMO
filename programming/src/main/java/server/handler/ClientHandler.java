package server.handler;

import common.command.CommandRequest;
import common.command.CommandResponse;
import common.command.CommandType;
import common.model.Ticket;
import server.manager.CollectionManager;
import server.manager.AuthManager;

import java.io.*;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.ForkJoinPool;

public class ClientHandler implements Runnable {
    private final Socket socket;
    private final CollectionManager collectionManager;
    private final AuthManager authManager;
    private final ExecutorService readPool;
    private final ForkJoinPool processPool;

    public ClientHandler(Socket socket, CollectionManager cm, AuthManager am,
                         ExecutorService readPool, ForkJoinPool processPool) {
        this.socket = socket;
        this.collectionManager = cm;
        this.authManager = am;
        this.readPool = readPool;
        this.processPool = processPool;
    }

    @Override
    public void run() {
        try (ObjectInputStream in = new ObjectInputStream(socket.getInputStream());
             ObjectOutputStream out = new ObjectOutputStream(socket.getOutputStream())) {

            while (true) {
                //чтение
                CommandRequest request = readPool.submit(() -> {
                    try {
                        return (CommandRequest) in.readObject();
                    } catch (ClassNotFoundException | IOException e) {
                        return null;
                    }
                }).get();

                if (request == null) {
                    System.out.println("Клиент отключился: " + socket.getRemoteSocketAddress());
                    break;
                }

                //бработка
                CommandResponse response = processPool.submit(() ->
                        processRequest(request)
                ).get();

                //отправка
                new Thread(() -> {
                    try {
                        out.writeObject(response);
                        out.flush();
                        out.reset();
                    } catch (IOException e) {
                        System.err.println("xxx ошибка отправки: " + e.getMessage());
                    }
                }).start();
                if (request.getType() == CommandType.EXIT) {
                    System.out.println("клиент завершил работу: " + socket.getRemoteSocketAddress());
                    break;
                }
            }
        } catch (Exception e) {
            System.out.println("ошибка обработки: " + e.getMessage());
        } finally {
            try { socket.close(); } catch (IOException ignored) {}
        }
    }




    //обраб запр
    private CommandResponse processRequest(CommandRequest request) {

        if (!authManager.authenticate(request.getLogin(), request.getPassword())) {
            return new CommandResponse("Ошибка аутентификации", null, false);
        }

        String login = request.getLogin();
        CommandType type = request.getType();
        Object arg = request.getArgument();

        try {
            switch (type) {
                case HELP:
                    return new CommandResponse(getHelpText(), null, true);
                case INFO:
                    return new CommandResponse(collectionManager.getInfo(), null, true);
                case SHOW:
                    return new CommandResponse("Коллекция:", collectionManager.getSortedCollection(), true);
                case INSERT:
                    if (arg instanceof Ticket) {
                        boolean res = collectionManager.insert((Ticket) arg, login);
                        return new CommandResponse(res ? "Добавлено" : "Ошибка добавления", null, res);
                    }
                    break;
                case UPDATE:
                    if (arg instanceof Ticket) {
                        boolean res = collectionManager.update((Ticket) arg, login);
                        return new CommandResponse(res ? "Обновлено" : "Ошибка обновления", null, res);
                    }
                    break;
                case REMOVE_KEY:
                    if (arg instanceof Long) {
                        boolean res = collectionManager.removeKey((Long) arg, login);
                        return new CommandResponse(res ? "Удалено" : "Ошибка удаления", null, res);
                    }
                    break;
                case CLEAR:
                    collectionManager.clear(login);
                    return new CommandResponse("Коллекция очищена ", null, true);
                case REMOVE_LOWER:
                    if (arg instanceof Ticket) {
                        boolean res = collectionManager.removeLower((Ticket) arg, login);
                        return new CommandResponse(res ? "Удалены меньшие" : "Ничего не удалено", null, true);
                    }
                    break;
                case REPLACE_IF_GREATER:
                    if (arg instanceof Ticket) {
                        Ticket t = (Ticket) arg;
                        boolean res = collectionManager.replaceIfGreater(t.getId(), t, login);
                        return new CommandResponse(res ? "Заменено" : "Не заменено", null, res);
                    }
                    break;
                case AVERAGE_OF_PRICE:
                    return new CommandResponse("Средняя цена: " + collectionManager.averageOfPrice(), null, true);
                case FILTER_LESS_THAN_PRICE:
                    if (arg instanceof Long) {
                        return new CommandResponse(collectionManager.filterLessThanPrice((Long) arg), null, true);
                    }
                    break;
                case EXECUTE_SCRIPT:
                    return new CommandResponse("Ошибка: execute_script выполняется на клиенте", null, false);
                case EXIT:
                    return new CommandResponse("Выход", null, true);
                default:
                    return new CommandResponse("Неизвестная команда", null, false);
            }
        } catch (Exception e) {
            return new CommandResponse("Ошибка сервера: " + e.getMessage(), null, false);
        }
        return new CommandResponse("Неверный аргумент", null, false);
    }

    private String getHelpText() {
        return "help, info, show, insert, update, remove_key, clear, remove_lower, " +
                "replace_if_greater, average_of_price, filter_less_than_price, execute_script, exit";
    }
}