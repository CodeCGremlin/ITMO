package client.ui;

import client.network.TcpClient;
import common.command.*;
import common.model.*;
import common.model.enums.*;

import java.io.File;
import java.io.FileNotFoundException;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;
import java.util.Stack;


public class InteractiveClient {
    private final TcpClient client;
    private final Scanner consoleScanner;
    private static final int MAX_SCRIPT_DEPTH = 5;
    private final Stack<String> scriptStack = new Stack<>();

    public InteractiveClient(TcpClient client) {
        this.client = client;
        this.consoleScanner = new Scanner(System.in, StandardCharsets.UTF_8);
    }

    public void start() {
        System.out.println("Авторизация");
        System.out.print("Введите логин: ");
        String login = consoleScanner.nextLine().trim();
        System.out.print("Введите пароль: ");
        String password = consoleScanner.nextLine().trim();
        client.setCredentials(login, password);

        System.out.println("\nВведите 'help' для справки.");

        while (true) {
            System.out.print("> ");
            String line = consoleScanner.nextLine().trim();
            if (line.isEmpty()) continue;

            if (!processCommand(line)) {
                break;
            }
        }
    }

    public boolean processCommand(String line) {
        String[] parts = line.split("\\s+", 2);
        String cmdName = parts[0].toUpperCase();
        String argStr = parts.length > 1 ? parts[1].trim() : null;

        CommandType type;
        try {
            type = CommandType.valueOf(cmdName);
        } catch (IllegalArgumentException e) {
            System.out.println("xxx неизвестная команда: " + cmdName);
            return true;
        }
        if (type == CommandType.EXIT) {
            client.close();
            System.out.println("работа клиента завершена");
            return false;
        }
        if (type == CommandType.EXECUTE_SCRIPT) {
            if (argStr == null || argStr.isEmpty()) {
                System.out.println("xxx eкажите имя файла скрипта");
                return true;
            }
            executeScript(argStr);
            return true;
        }
        Object arg = parseArgument(type, argStr, client.getLogin());
        if (arg == null && requiresArgument(type)) {
            if (type != CommandType.INSERT && type != CommandType.UPDATE && type != CommandType.REMOVE_LOWER && type != CommandType.REPLACE_IF_GREATER) {
                System.out.println("xxx ошибка ввода аргумента");
                return true;
            }
        }

        CommandRequest request = new CommandRequest(type, arg, client.getLogin(), client.getPassword());
        CommandResponse response = client.send(request);

        printResponse(response);
        return true;
    }

    private void executeScript(String fileName) {
        //защита от рекурсии
        if (scriptStack.size() >= MAX_SCRIPT_DEPTH) {
            System.out.println("xxx Превышена максимальная глубина вложенности скриптов (" + MAX_SCRIPT_DEPTH + ").");
            return;
        }
        //защита от зацикливания на тот же файл
        if (scriptStack.contains(fileName)) {
            System.out.println("xxx Обнаружена циклическая ссылка на скрипт: " + fileName);
            return;
        }

        File file = new File(fileName);
        if (!file.exists()) {
            System.out.println("xxx Файл не найден: " + fileName);
            return;
        }
        if (!file.canRead()) {
            System.out.println("xxx нет прав на чттение файла: " + fileName);
            return;
        }

        System.out.println("скрипт: " + fileName);
        scriptStack.push(fileName);

        try (Scanner fileScanner = new Scanner(file, StandardCharsets.UTF_8)) {
            while (fileScanner.hasNextLine()) {
                String cmd = fileScanner.nextLine().trim();

                //пропуск пустых строк и комментариев
                if (cmd.isEmpty() || cmd.startsWith("#")) {
                    continue;
                }
                //вывод комманды
                System.out.println("   >> " + cmd);

                if (!processCommand(cmd)) {
                    System.out.println("exit");
                    break;
                }
            }
        } catch (FileNotFoundException e) {
            System.out.println("xxx ошибка файл не найден");
        } catch (Exception e) {
            System.out.println("xxx ошибка чтения скрипта: " + e.getMessage());
        } finally {
            scriptStack.pop();
            System.out.println("мкрипт завершен");
        }
    }

    //парсинг
    private Object parseArgument(CommandType type, String argStr, String login) {
        try {
            switch (type) {
                case INSERT:
                case UPDATE:
                case REMOVE_LOWER:
                case REPLACE_IF_GREATER:
                    return readTicketFromConsole(login);
                case REMOVE_KEY:
                    if (argStr == null) return null;
                    return Long.parseLong(argStr);
                case FILTER_LESS_THAN_PRICE:
                    if (argStr == null) return null;
                    return Long.parseLong(argStr); // Теперь price — Long, а не Float!
                case REMOVE_GREATER_KEY:
                    if (argStr == null) return null;
                    return Long.parseLong(argStr);
                default:
                    return argStr;
            }
        } catch (NumberFormatException e) {
            System.out.println("xxx неверный формат числа.");
            return null;
        } catch (Exception e) {
            System.out.println("xxx ошибка ввода: " + e.getMessage());
            return null;
        }
    }

    private boolean requiresArgument(CommandType type) {
        return type == CommandType.INSERT || type == CommandType.UPDATE ||
                type == CommandType.REMOVE_KEY || type == CommandType.REMOVE_LOWER ||
                type == CommandType.REPLACE_IF_GREATER || type == CommandType.FILTER_LESS_THAN_PRICE ||
                type == CommandType.REMOVE_GREATER_KEY;
    }


    private void printResponse(CommandResponse response) {
        if (response == null) {
            System.out.println("xxx нет ответа от сервера.");
            return;
        }
        if (response.isSuccess()) {
            System.out.println("+++ " + response.getMessage());
        } else {
            System.out.println("xxx " + response.getMessage());
        }
        if (response.getData() != null) {
            System.out.println("файл " + response.getData().toString());
        }
    }


    private Ticket readTicketFromConsole(String login) {
        System.out.println("--- Данные билета ---");

        System.out.print("Введите имя: ");
        String name = consoleScanner.nextLine().trim();
        if (name.isEmpty()) return null;

        Long price = readLong("Введите цену > 0: ");
        if (price == null || price <= 0) {
            if (price != null) System.out.println("xxx цена должна быть > 0");
            return null;
        }

        System.out.println("Введите тип билета (VIP, USUAL, CHEAP): ");
        TicketType type = readEnum(TicketType.class);
        if (type == null) return null;


        System.out.print("Возвращаемый билетили нет (true/false) или пустую строку для null: ");
        String refundableStr = consoleScanner.nextLine().trim();
        Boolean refundable = null;
        if (!refundableStr.isEmpty()) {
            refundable = Boolean.parseBoolean(refundableStr);
        }

        Integer x = readInteger("Введите координаты ивента по x coordinates.x (макс. 630): ");
        if (x == null) return null;
        if (x > 630) {
            System.out.println("xxx coordinates.x не может превышать 630");
            return null;
        }

        Double y = readDouble("Введите координаты ивента по y coordinates.y: ");
        if (y == null) return null;
        Coordinates coords = new Coordinates(x, y);

        Integer height = readInteger("Введите рост человека (> 0): ");
        if (height == null) return null;
        if (height <= 0) {
            System.out.println("xxx рост должен быть больше 0");
            return null;
        }

        System.out.print("Введите номер паспорта ");
        String passportID = consoleScanner.nextLine().trim();
        if (passportID.isEmpty()) return null;

        System.out.println("Введите цвет глаз (GREEN, BLACK, BROWN): ");
        EyeColor eyeColor = readEnum(EyeColor.class);
        if (eyeColor == null) return null;

        System.out.print("Введите цвет волоr (RED, BLUE, ORANGE, BROWN) или пустую строку для null: ");
        String hairColorStr = consoleScanner.nextLine().trim();
        HairColor hairColor = hairColorStr.isEmpty() ? null : HairColor.valueOf(hairColorStr.toUpperCase());

        Person person = new Person(height, passportID, eyeColor, hairColor);

        return new Ticket(name, coords, price, refundable, type, person, login);
    }


    private Float readFloat(String prompt) {
        while (true) {
            System.out.print(prompt);
            String line = consoleScanner.nextLine().trim();
            if (line.isEmpty()) return null;
            try {
                return Float.parseFloat(line);
            } catch (NumberFormatException e) {
                System.out.println("xxx неверный формат числа.");
            }
        }
    }

    private Long readLong(String prompt) {
        while (true) {
            System.out.print(prompt);
            String line = consoleScanner.nextLine().trim();
            if (line.isEmpty()) return null;
            try {
                return Long.parseLong(line);
            } catch (NumberFormatException e) {
                System.out.println("xxx неверный формат числа.");
            }
        }
    }

    private Integer readInteger(String prompt) {
        while (true) {
            System.out.print(prompt);
            String line = consoleScanner.nextLine().trim();
            if (line.isEmpty()) return null;
            try {
                return Integer.parseInt(line);
            } catch (NumberFormatException e) {
                System.out.println("xxx неверный формат числа.");
            }
        }
    }

    private Double readDouble(String prompt) {
        while (true) {
            System.out.print(prompt);
            String line = consoleScanner.nextLine().trim();
            if (line.isEmpty()) return null;
            try {
                return Double.parseDouble(line);
            } catch (NumberFormatException e) {
                System.out.println("xxx Неверный формат числа.");
            }
        }
    }

    private <T extends Enum<T>> T readEnum(Class<T> clazz) {
        System.out.print("Доступные значения: ");
        T[] constants = clazz.getEnumConstants();
        for (int i = 0; i < constants.length; i++) {
            System.out.print(constants[i].name());
            if (i < constants.length - 1) System.out.print(", ");
        }
        System.out.println();

        while (true) {
            String line = consoleScanner.nextLine().trim();
            if (line.isEmpty()) return null;
            try {
                return Enum.valueOf(clazz, line.toUpperCase());
            } catch (IllegalArgumentException e) {
                System.out.println("xxx Неверное значение. Попробуйте снова.");
            }
        }
    }
}