

const MESSAGES = {
    INVALID_X: 'X must be one of: -5, -4, -3, -2, -1, 0, 1, 2, 3',
    INVALID_Y: 'Y must be a number between -3 and 3',
    INVALID_R: 'R must be one of: 1.0, 1.5, 2.0, 2.5, 3.0',
    REQUEST_FAILED: 'Request failed: ',
    HISTORY_CLEARED: 'History cleared successfully'
};

const state = {
    x: 0,
    y: 0,
    r: 1.0,
};

const possibleXs = new Set([-5, -4, -3, -2, -1, 0, 1, 2, 3]);
const possibleRs = new Set([1.0, 1.5, 2.0, 2.5, 3.0]);

let currentPage = 1;
let totalPages = 1;
let selectedBtn = null;

// Валидация
const validateState = (state) => {
    if (isNaN(state.x) || !possibleXs.has(state.x)) {
        showError(MESSAGES.INVALID_X);
        throw new Error("Invalid X");
    }

    if (isNaN(state.y) || state.y < -3 || state.y > 3) {
        showError(MESSAGES.INVALID_Y);
        throw new Error("Invalid Y");
    }

    if (isNaN(state.r) || !possibleRs.has(state.r)) {
        showError(MESSAGES.INVALID_R);
        throw new Error("Invalid R");
    }

    hideError();
};

const showError = (message) => {
    const error = document.getElementById("error");
    error.hidden = false;
    error.innerText = message;
};

const hideError = () => {
    const error = document.getElementById("error");
    error.hidden = true;
};

const addResultToTable = (result, prepend = false) => {
    const table = document.getElementById("result-table");
    const position = prepend ? 1 : -1;
    const newRow = table.insertRow(position);

    const rowX = newRow.insertCell(0);
    const rowY = newRow.insertCell(1);
    const rowR = newRow.insertCell(2);
    const rowTime = newRow.insertCell(3);
    const rowExecTime = newRow.insertCell(4);
    const rowResult = newRow.insertCell(5);

    rowX.innerText = result.x;
    rowY.innerText = result.y;
    rowR.innerText = result.r;
    rowTime.innerText = result.current_time;
    rowExecTime.innerText = result.execution_time + " ns";
    rowResult.innerText = result.hit ? "Hit" : "Miss";
    rowResult.className = result.hit ? "hit" : "miss";
};

const loadHistoryPage = async (page) => {
    try {
        const url = `/fcgi-bin/weblab1.jar?action=history&page=${page}`;
        const response = await fetch(url);

        if (response.ok) {
            const data = await response.json();

            // Очищаем таблицу (кроме заголовка)
            const table = document.getElementById("result-table");
            while (table.rows.length > 1) {
                table.deleteRow(1);
            }

            // Добавляем результаты (новые сверху)
            data.results.forEach(result => {
                addResultToTable(result, false);
            });

            // Обновляем пагинацию
            currentPage = data.page;
            totalPages = data.totalPages;
            updatePagination();
        }
    } catch (error) {
        console.error("Failed to load history:", error);
    }
};

const updatePagination = () => {
    const pageInfo = document.getElementById("page-info");
    const prevBtn = document.getElementById("prev-page");
    const nextBtn = document.getElementById("next-page");

    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
};

document.addEventListener('DOMContentLoaded', function() {
    // Обработка X
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

    // Обработка Y и R
    document.getElementById("y").addEventListener("change", (ev) => {
        state.y = parseFloat(ev.target.value);
    });

    document.getElementById("r").addEventListener("change", (ev) => {
        state.r = parseFloat(ev.target.value);
    });

    // Submit формы
    document.getElementById("data-form").addEventListener("submit", async function (ev) {
        ev.preventDefault();

        try {
            validateState(state);

            const params = new URLSearchParams(state);
            const url = `/fcgi-bin/weblab1.jar?${params.toString()}`;

            console.log("Sending request to:", url);

            const response = await fetch(url);
            console.log("Response status:", response.status);

            if (response.ok) {
                const result = await response.json();
                console.log("Received result:", result);

                // Добавляем новый результат в начало таблицы
                addResultToTable(result, true);

                // Перезагружаем первую страницу для обновления пагинации
                await loadHistoryPage(1);

            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

        } catch (error) {
            console.error("Request failed:", error);
            showError(MESSAGES.REQUEST_FAILED + error.message);
        }
    });

    // Очистка истории
    document.getElementById("clear-history-btn").addEventListener("click", async function() {
        if (confirm('Are you sure you want to clear history?')) {
            try {
                const response = await fetch('/fcgi-bin/weblab1.jar?action=clear');
                if (response.ok) {
                    // Очищаем таблицу (кроме заголовка)
                    const table = document.getElementById("result-table");
                    while (table.rows.length > 1) {
                        table.deleteRow(1);
                    }
                    showError(MESSAGES.HISTORY_CLEARED);
                    setTimeout(hideError, 3000);
                    currentPage = 1;
                    totalPages = 1;
                    updatePagination();
                }
            } catch (error) {
                console.error("Failed to clear history:", error);
                showError("Failed to clear history");
            }
        }
    });

    // Пагинация
    document.getElementById("prev-page").addEventListener("click", () => {
        if (currentPage > 1) {
            loadHistoryPage(currentPage - 1);
        }
    });

    document.getElementById("next-page").addEventListener("click", () => {
        if (currentPage < totalPages) {
            loadHistoryPage(currentPage + 1);
        }
    });

    // Загрузка начальной истории
    loadHistoryPage(1);

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