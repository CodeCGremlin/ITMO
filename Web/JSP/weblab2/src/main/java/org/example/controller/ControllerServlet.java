package org.example.controller;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@WebServlet("/controller")
public class ControllerServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String x = request.getParameter("x");
        String y = request.getParameter("y");
        String r = request.getParameter("r");

        // Если параметры присутствуют - делегируем AreaCheckServlet
        if (x != null && y != null && r != null) {
            request.getRequestDispatcher("/area-check").forward(request, response);
        }
        // Иначе показываем форму
        else {
            request.getRequestDispatcher("/index.jsp").forward(request, response);
        }
    }
}