<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<html>
<head>
    <title>Area Check - Web Lab 2</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/resources/css/main.css">
</head>
<body>
    <header>
        <div id="info">
            <h1>Web Lab №2</h1>
            <p>Anton Davidyuk Yurievich</p>
            <p>Group: P3210</p>
            <p>Variant: 503517</p>
        </div>
    </header>

    <main class="container">
        <section class="input-section">
            <form action="controller" method="GET" id="data-form">
                <label for="x">X (от -5 до 3):</label>
                <input type="text" id="x" name="x" value="${param.x}" required>

                <fieldset id="ys">
                    <legend>Select Y:</legend>
                    <input type="button" name="y" value="-5">
                    <input type="button" name="y" value="-4">
                    <input type="button" name="y" value="-3">
                    <input type="button" name="y" value="-2">
                    <input type="button" name="y" value="-1">
                    <input type="button" name="y" value="0">
                    <input type="button" name="y" value="1">
                    <input type="button" name="y" value="2">
                    <input type="button" name="y" value="3">
                </fieldset>

                <label for="r">Select R:</label>
                <select id="r" name="r" required>
                    <option value="1.0" ${param.r == '1.0' ? 'selected' : ''}>1.0</option>
                    <option value="1.5" ${param.r == '1.5' ? 'selected' : ''}>1.5</option>
                    <option value="2.0" ${param.r == '2.0' ? 'selected' : ''}>2.0</option>
                    <option value="2.5" ${param.r == '2.5' ? 'selected' : ''}>2.5</option>
                    <option value="3.0" ${param.r == '3.0' ? 'selected' : ''}>3.0</option>
                </select>

                <button type="submit">Submit</button>
            </form>

            <div id="error">
                <c:if test="${not empty error}">
                    ${error}
                </c:if>
            </div>

            <canvas id="graph" width="300" height="300"></canvas>
        </section>

        <section class="results-section">
            <h2>Results History</h2>
            <table id="result-table">
                <tr>
                    <th>x</th>
                    <th>y</th>
                    <th>r</th>
                    <th>time</th>
                    <th>execution time</th>
                    <th>result</th>
                </tr>
                <c:forEach var="result" items="${sessionScope.results}">
                <tr>
                    <td>${result.x}</td>
                    <td>${result.y}</td>
                    <td>${result.r}</td>
                    <td>${result.currentTime}</td>
                    <td>${result.executionTime} ns</td>
                    <td>${result.hit ? 'true' : 'false'}</td>
                </tr>
                </c:forEach>
            </table>
        </section>
    </main>

    <script src="${pageContext.request.contextPath}/resources/js/index.js"></script>
</body>
</html>