package org.example.controller;

import org.example.model.ResultBean;
import org.example.util.AreaChecker;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

@WebServlet("/area-check")
public class AreaCheckServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        long startTime = System.nanoTime();

        try {
            // Получаем параметры
            double x = Double.parseDouble(request.getParameter("x"));
            double y = Double.parseDouble(request.getParameter("y"));
            double r = Double.parseDouble(request.getParameter("r"));

            // Валидация
            if (!isValid(x, y, r)) {
                request.setAttribute("error", "Invalid parameters");
                request.getRequestDispatcher("/index.jsp").forward(request, response);
                return;
            }

            // Проверка попадания (переиспользуем логику из первой работы)
            boolean hit = AreaChecker.checkHit(x, y, r);
            long executionTime = System.nanoTime() - startTime;
            String currentTime = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));

            // Создаем результат
            ResultBean result = new ResultBean(x, y, r, hit, currentTime, executionTime);

            // Сохраняем в сессию (или application scope по требованию)
            HttpSession session = request.getSession();
            List<ResultBean> results = (List<ResultBean>) session.getAttribute("results");
            if (results == null) {
                results = new ArrayList<>();
                session.setAttribute("results", results);
            }
            results.add(result);

            // Перенаправляем на страницу результатов
            request.getRequestDispatcher("/result.jsp").forward(request, response);

        } catch (NumberFormatException e) {
            request.setAttribute("error", "Invalid number format");
            request.getRequestDispatcher("/index.jsp").forward(request, response);
        }
    }

    private boolean isValid(double x, double y, double r) {
        return x >= -5 && x <= 3 &&
                y >= -5 && y <= 3 &&
                (r == 1 || r == 1.5 || r == 2 || r == 2.5 || r == 3);
    }
}