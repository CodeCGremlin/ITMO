<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="org.example.model.ResultBean" %>
<%@ page import="java.util.List" %>
<%
    List<ResultBean> results = (List<ResultBean>) session.getAttribute("results");
    ResultBean lastResult = results != null && !results.isEmpty() ?
        results.get(results.size() - 1) : null;
%>
<html>
<head>
    <title>Result</title>
</head>
<body>
    <h1>Результат проверки</h1>

    <% if (lastResult != null) { %>
    <table border="1">
        <tr><th>Параметр</th><th>Значение</th></tr>
        <tr><td>X</td><td><%= lastResult.getX() %></td></tr>
        <tr><td>Y</td><td><%= lastResult.getY() %></td></tr>
        <tr><td>R</td><td><%= lastResult.getR() %></td></tr>
        <tr><td>Результат</td><td><%= lastResult.isHit() ? "Попадание" : "Промах" %></td></tr>
        <tr><td>Время</td><td><%= lastResult.getCurrentTime() %></td></tr>
        <tr><td>Время выполнения</td><td><%= lastResult.getExecutionTime() %> ns</td></tr>
    </table>
    <% } %>

    <br>
    <a href="controller">Вернуться к форме</a>

    <h2>Вся история</h2>
    <table border="1">
        <tr>
            <th>x</th><th>y</th><th>r</th><th>time</th><th>execution time</th><th>result</th>
        </tr>
        <% if (results != null) {
            for (ResultBean result : results) { %>
        <tr>
            <td><%= result.getX() %></td>
            <td><%= result.getY() %></td>
            <td><%= result.getR() %></td>
            <td><%= result.getCurrentTime() %></td>
            <td><%= result.getExecutionTime() %> ns</td>
            <td><%= result.isHit() ? "true" : "false" %></td>
        </tr>
        <% }
        } %>
    </table>
</body>
</html>