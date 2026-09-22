"use strict";

//значения
const state = {
    x: 0,
    y: 0,
    r: 1.0,
};

const table = document.getElementById("result-table");
const error = document.getElementById("error");

const possibleXs = new Set([-3, -2, -1, 0, 1, 2, 3, 4, 5]);
const possibleRs = new Set([1.0, 1.5, 2.0, 2.5, 3.0]);


//валидация
const validateState = (state) => {
    if (isNaN(state.x) || !possibleXs.has(state.x)) {
        error.hidden = false;
        error.innerText = `x must be in [${[...possibleXs].join(" ,")}]`;
        throw new Error("Invalid state");
    }

    if (isNaN(state.y) || state.y < -3 || state.y > 3) {
        error.hidden = false;
        error.innerText = "y must be in range [-3, 3]";
        throw new Error("Invalid state");
    }

    if (isNaN(state.r) || !possibleRs.has(state.r)) {
        error.hidden = false;
        error.innerText = `r must be in [${[...possibleRs].join(" ,")}]`;
        throw new Error("Invalid state");
    }

    error.hidden = true;
}

let selectedBtn = null;


document.addEventListener('DOMContentLoaded', function() {

    const table = document.getElementById("result-table");
    const error = document.getElementById("error");


    // Обр X
    Array.from(document.getElementById("xs").children)
        .filter(c => c.tagName === "INPUT")
        .forEach(btn => {
            btn.style.border = "";
            btn.addEventListener("click", function (ev) {
                if (selectedBtn !== null) {
                    selectedBtn.style.border = "";
                }
                selectedBtn = btn;
                state.x = parseInt(ev.target.value);
                selectedBtn.style.border = "#FF6961 1px solid";
            });
        });

    // обр Y R
    document.getElementById("y").addEventListener("change", (ev) => {
        state.y = parseFloat(ev.target.value);
    });

    document.getElementById("r").addEventListener("change", (ev) => {
        state.r = parseFloat(ev.target.value);
    });

    // submit
    document.getElementById("data-form").addEventListener("submit", async function (ev) {
        ev.preventDefault();

        try {
            validateState(state);

            const params = new URLSearchParams(state);
            const url = "/fcgi-bin/weblab1.jar?" + params.toString();

            console.log("Sending request to:", url);

            const response = await fetch(url);
            console.log("Response status:", response.status);

            if (response.ok) {
                const result = await response.json();
                console.log("Received result:", result);

                // Создаем новую строку в таблице
                const newRow = table.insertRow(-1);
                const rowX = newRow.insertCell(0);
                const rowY = newRow.insertCell(1);
                const rowR = newRow.insertCell(2);
                const rowTime = newRow.insertCell(3);
                const rowExecTime = newRow.insertCell(4);
                const rowResult = newRow.insertCell(5);

                // Заполняем данными
                rowX.innerText = result.x;
                rowY.innerText = result.y;
                rowR.innerText = result.r;
                rowTime.innerText = result.current_time;
                rowExecTime.innerText = result.execution_time + " ns";
                rowResult.innerText = result.hit ? "true" : "false";

                // Сохраняем в localStorage
                const prevResults = JSON.parse(localStorage.getItem("results") || "[]");
                localStorage.setItem("results", JSON.stringify([...prevResults, {
                    x: result.x,
                    y: result.y,
                    r: result.r,
                    time: result.current_time,
                    execTime: result.execution_time + " ns",
                    result: result.hit ? "true" : "false"
                }]));

            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

        } catch (error) {
            console.error("Request failed:", error);
            document.getElementById("error").hidden = false;
            document.getElementById("error").innerText = `Request failed: ${error.message}`;
        }
    });

    // вост истории
    const prevResults = JSON.parse(localStorage.getItem("results") || "[]");

    prevResults.forEach(result => {
        const newRow = table.insertRow(-1);

        const rowX = newRow.insertCell(0);
        const rowY = newRow.insertCell(1);
        const rowR = newRow.insertCell(2);
        const rowTime = newRow.insertCell(3);
        const rowExecTime = newRow.insertCell(4);
        const rowResult = newRow.insertCell(5);

        rowX.innerText = result.x.toString();
        rowY.innerText = result.y.toString();
        rowR.innerText = result.r.toString();
        rowTime.innerText = result.time;
        rowExecTime.innerText = result.execTime;
        rowResult.innerText = result.result;
    });

    // очистка истории
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const resultTable = document.getElementById('result-table'); // Используем table, если она объявлена выше

    if (clearHistoryBtn && resultTable) {
        clearHistoryBtn.addEventListener('click', function() {
            if (confirm('удалить историю?')) {
                while (resultTable.rows.length > 1) {
                    resultTable.deleteRow(1);
                }
                localStorage.removeItem('results');
                console.log("История очищена");
            }
        });
    } else {
        console.warn("Кнопка очистить историю или таблица результатов не найдены в DOM");
    }

    // график
    const canvas = document.getElementById('graph');
    if (!canvas) {
        console.error("график не найден в DOM.");
        return;
    }
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error("Не удалось получить график");
        return;
    }

    const width = canvas.width;
    const height = canvas.height;
    const CANVAS_R = 100;
    const centerX = width / 2;
    const centerY = height / 2;

    ctx.fillStyle = 'rgba(255, 20, 25, 1)';

    // квадр
    ctx.beginPath();

    ctx.rect(centerX, centerY, CANVAS_R, CANVAS_R);
    ctx.fill();

    // окр
    ctx.beginPath();

    ctx.arc(centerX, centerY, CANVAS_R, Math.PI, 3 * Math.PI / 2, false);
    ctx.lineTo(centerX, centerY);
    ctx.fill();

    // треуг
    ctx.beginPath();

    ctx.moveTo(centerX, centerY);

    ctx.lineTo(centerX + CANVAS_R, centerY);

    ctx.lineTo(centerX, centerY - CANVAS_R / 2);
    ctx.closePath();
    ctx.fill();

    // Оси
    ctx.beginPath();
    ctx.moveTo(centerX, 0);  // Y
    ctx.lineTo(centerX, height);
    ctx.moveTo(0, centerY);  // X
    ctx.lineTo(width, centerY);
    ctx.strokeStyle = "black";
    ctx.stroke();

    // Подписи
    ctx.font = "20px monospace";
    ctx.fillStyle = "black";

    ctx.strokeText("0", centerX + 6, centerY - 6);
    ctx.strokeText("R/2", centerX + CANVAS_R / 2 - 6, centerY - 6);
    ctx.strokeText("R", centerX + CANVAS_R - 6, centerY - 6);

    ctx.strokeText("-R/2", centerX - CANVAS_R / 2 - 18, centerY - 6);
    ctx.strokeText("-R", centerX - CANVAS_R - 6, centerY - 6);

    ctx.strokeText("R/2", centerX + 6, centerY - CANVAS_R / 2 + 6);
    ctx.strokeText("R", centerX + 6, centerY - CANVAS_R + 6);

    ctx.strokeText("-R/2", centerX + 6, centerY + CANVAS_R / 2 + 6);
    ctx.strokeText("-R", centerX + 6, centerY + CANVAS_R + 6);

    ctx.strokeText("X", centerX + CANVAS_R + 36, centerY - 6);
    ctx.strokeText("Y", centerX - 16, centerY - CANVAS_R - 36);

});