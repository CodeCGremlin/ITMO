package org.example;


import com.fastcgi.FCGIInterface;
import java.io.*;
import java.util.*;
import java.time.LocalDateTime;
import org.example.sample.Point;
import org.example.sample.Result;

public class FastCGISRV {
    private static List<Result> history = Collections.synchronizedList(new ArrayList<>());
    private static final int RESULTS_PER_PAGE = 10;

    public static void main(String[] args) {
        System.err.println("Starting FastCGI server");

        FCGIInterface fcgi = new FCGIInterface();
        while (fcgi.FCGIaccept() >= 0) {
            try {
                handleRequest();
            } catch (Exception e) {
                System.err.println("Error handling request: " + e.getMessage());
                e.printStackTrace();
                sendErrorResponse("Internal Server Error");
            }
        }
    }

    private static void handleRequest() throws IOException {
        long startTime = System.nanoTime();

        String queryString = System.getProperty("QUERY_STRING");
        System.err.println("Raw QUERY_STRING: " + queryString);

        if (queryString == null || queryString.isEmpty()) {
            System.err.println("No QUERY_STRING found");
            sendErrorResponse("Missing QUERY_STRING");
            return;
        }

        // Парc парам
        Map<String, String> params = parseQueryString(queryString);
        System.err.println("Parsed params: " + params);

        String xStr = params.get("x");
        String yStr = params.get("y");
        String rStr = params.get("r");
        String pageStr = params.get("page");

        // Если запрос на получение истории
        if ("history".equals(params.get("action"))) {
            int page = pageStr != null ? Integer.parseInt(pageStr) : 1;
            sendHistoryResponse(page);
            return;
        }

        // Если запрос на очистку истории
        if ("clear".equals(params.get("action"))) {
            history.clear();
            sendJsonResponse("{\"status\": \"success\", \"message\": \"History cleared\"}");
            return;
        }

        if (xStr == null || yStr == null || rStr == null) {
            System.err.println("Missing parameters. Found: " + params.keySet());
            sendErrorResponse("Parameters x, y, r are required");
            return;
        }

        try {
            double x = Double.parseDouble(xStr);
            double y = Double.parseDouble(yStr);
            double r = Double.parseDouble(rStr);
            Point point = new Point(x, y, r);

            System.err.println("Parsed point: " + point);

            // Валидация
            if (!AreaCheck.validatePoint(point)) {
                System.err.println("Validation failed for point: " + point);
                sendErrorResponse("Invalid parameters");
                return;
            }

            // Проверка попадания
            boolean hit = AreaCheck.checkHit(point);
            System.err.println("Hit result: " + hit);

            long executionTime = System.nanoTime() - startTime;

            Result result = new Result(point, hit, LocalDateTime.now(), executionTime);
            history.add(0, result);

            sendJsonResponse(result);

        } catch (NumberFormatException e) {
            System.err.println("Number format exception: " + e.getMessage());
            sendErrorResponse("Invalid number format");
        }
    }

    private static Map<String, String> parseQueryString(String queryString) {
        Map<String, String> params = new HashMap<>();
        if (queryString == null || queryString.isEmpty()) {
            return params;
        }
        String[] pairs = queryString.split("&");
        for (String pair : pairs) {
            String[] keyValue = pair.split("=");
            if (keyValue.length == 2) {
                try {
                    String key = java.net.URLDecoder.decode(keyValue[0], "UTF-8");
                    String value = java.net.URLDecoder.decode(keyValue[1], "UTF-8");
                    params.put(key, value);
                } catch (UnsupportedEncodingException e) {

                }
            }
        }
        return params;
    }


    private static void sendJsonResponse(Object data) {
        String json;
        if (data instanceof Result) {
            json = ((Result) data).toJson();
        } else {
            json = data.toString();
        }

        System.out.println("Content-Type: application/json");
        System.out.println("Access-Control-Allow-Origin: *");
        System.out.println();
        System.out.println(json);
        System.out.flush();
    }

    private static void sendHistoryResponse(int page) {
        int totalResults = history.size();
        int totalPages = (int) Math.ceil((double) totalResults / RESULTS_PER_PAGE);
        int startIndex = (page - 1) * RESULTS_PER_PAGE;
        int endIndex = Math.min(startIndex + RESULTS_PER_PAGE, totalResults);

        List<Result> pageResults = history.subList(startIndex, endIndex);

        StringBuilder json = new StringBuilder();
        json.append("{\"page\":").append(page)
                .append(",\"totalPages\":").append(totalPages)
                .append(",\"totalResults\":").append(totalResults)
                .append(",\"results\":[");

        for (int i = 0; i < pageResults.size(); i++) {
            if (i > 0) json.append(",");
            json.append(pageResults.get(i).toJson());
        }

        json.append("]}");

        System.out.println("Content-Type: application/json");
        System.out.println("Access-Control-Allow-Origin: *");
        System.out.println();
        System.out.println(json.toString());
        System.out.flush();
    }

    private static void sendErrorResponse(String message) {
        String json = "{\"error\": \"" + message.replace("\"", "\\\"") + "\"}";
        System.out.println("Status: 400 Bad Request");
        System.out.println("Content-Type: application/json");
        System.out.println("Access-Control-Allow-Origin: *");
        System.out.println();
        System.out.println(json);
        System.out.flush();
    }

}