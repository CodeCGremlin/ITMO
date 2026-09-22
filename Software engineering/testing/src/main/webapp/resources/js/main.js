(function () {
    'use strict';

    window.addEventListener('load', init);

    function init() {
        const canvas = document.getElementById('areaCanvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;
        const cx = W / 2;
        const cy = H / 2;
        const PADDING = 30;
        const ppu = (W / 2 - PADDING) / 5;

        function getR() {
            const rRadios = document.getElementsByName('pointForm:rInput');
            for (let i = 0; i < rRadios.length; i++) {
                if (rRadios[i].checked) {
                    return parseFloat(rRadios[i].value);
                }
            }
            return 1.0;
        }

        function draw() {
            const r = getR();

            ctx.clearRect(0, 0, W, H);
            ctx.fillStyle = '#fcf8f0';
            ctx.fillRect(0, 0, W, H);

            ctx.fillStyle = 'rgba(141, 110, 99, 0.25)';
            ctx.strokeStyle = '#5d4037';
            ctx.lineWidth = 1.5;

            const rPix = r * ppu;
            const halfRPix = (r / 2) * ppu;

            // Квадрат (-R < X < 0, 0 < Y < R)
            ctx.beginPath();
            ctx.rect(cx - rPix, cy - rPix, rPix, rPix);
            ctx.fill();
            ctx.stroke();

            // Четверть круга (0 < X < R, 0 < Y < R)


            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.arc(cx, cy, rPix, 0, -Math.PI/2, true);
            ctx.lineTo(cx, cy);
            ctx.fill();
            ctx.stroke();
            // Треугольник (0 < X < R/2, -R < Y < 0)
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + halfRPix, cy);
            ctx.lineTo(cx, cy + rPix);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            drawAxes(r);
            drawHistoryPoints();
        }

        function drawAxes(r) {
            ctx.strokeStyle = '#5d4037';
            ctx.lineWidth = 1.2;
            ctx.fillStyle = '#5d4037';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            ctx.beginPath();
            ctx.moveTo(PADDING, cy); ctx.lineTo(W - PADDING, cy);
            ctx.moveTo(cx, PADDING); ctx.lineTo(cx, H - PADDING);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(W - PADDING, cy); ctx.lineTo(W - PADDING - 10, cy - 5);
            ctx.lineTo(W - PADDING, cy); ctx.lineTo(W - PADDING - 10, cy + 5);
            ctx.moveTo(cx, PADDING); ctx.lineTo(cx - 5, PADDING + 10);
            ctx.lineTo(cx, PADDING); ctx.lineTo(cx + 5, PADDING + 10);
            ctx.stroke();

            const labels = [
                { val: r, text: 'R' },
                { val: r/2, text: 'R/2' }
            ];

            labels.forEach(mark => {
                const px = mark.val * ppu;
                if (px === 0) return;

                ctx.beginPath(); ctx.moveTo(cx + px, cy - 3); ctx.lineTo(cx + px, cy + 3); ctx.stroke();
                ctx.fillText(mark.text, cx + px, cy + 15);

                ctx.beginPath(); ctx.moveTo(cx - px, cy - 3); ctx.lineTo(cx - px, cy + 3); ctx.stroke();
                ctx.fillText("-" + mark.text, cx - px, cy + 15);

                ctx.beginPath(); ctx.moveTo(cx - 3, cy - px); ctx.lineTo(cx + 3, cy - px); ctx.stroke();
                ctx.fillText(mark.text, cx - 20, cy - px);

                ctx.beginPath(); ctx.moveTo(cx - 3, cy + px); ctx.lineTo(cx + 3, cy + px); ctx.stroke();
                ctx.fillText("-" + mark.text, cx - 20, cy + px);
            });

            ctx.fillText('X', W - 10, cy - 10);
            ctx.fillText('Y', cx + 10, 10);
        }
function drawHistoryPoints() {
    const allPointsContainer = document.getElementById('pointForm:allPointsContainer');
    if (!allPointsContainer) {
        console.warn("allPointsContainer not found in DOM");
        return;
    }

    const allPoints = allPointsContainer.querySelectorAll('.point-data');

    allPoints.forEach(pointEl => {
        const x = parseFloat(pointEl.getAttribute('data-x'));
        const y = parseFloat(pointEl.getAttribute('data-y'));
        const pointR = parseFloat(pointEl.getAttribute('data-r'));
        const hit = pointEl.getAttribute('data-hit') === 'true';

        if (!isNaN(x) && !isNaN(y) && !isNaN(pointR)) {
            const currentR = getR();
            const scale = currentR / pointR;
            const displayX = x * scale;
            const displayY = y * scale;

            ctx.beginPath();
            ctx.arc(cx + displayX * ppu, cy - displayY * ppu, 4, 0, Math.PI * 2);
            ctx.fillStyle = hit ? '#2e7d32' : '#c62828';
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.stroke();
        }
    });
}

        window.redrawGraph = draw;

   canvas.addEventListener('click', function(e) {
       const rect = canvas.getBoundingClientRect();
       const xRaw = (e.clientX - rect.left - cx) / ppu;
       const yRaw = (cy - (e.clientY - rect.top)) / ppu;

       // X ДОЛЖЕН БЫТЬ ЦЕЛЫМ (как в селекте)
       const xVal = Math.round(xRaw);
       const yVal = parseFloat(yRaw.toFixed(2));

       // Валидация
       if (xVal < -4 || xVal > 4 || yVal < -5 || yVal > 3) {s
           return;
       }

       // Устанавливаем ТОЛЬКО в скрытые поля
       document.getElementById('pointForm:hiddenX').value = xVal;
       document.getElementById('pointForm:hiddenY').value = yVal;

       // Нажимаем кнопку (отправит ТОЛЬКО скрытые поля и R)
       document.getElementById('pointForm:canvasBtn').click();
   });

        const rRadios = document.getElementsByName('pointForm:rInput');
        rRadios.forEach(radio => {
            radio.addEventListener('change', draw);
        });

        draw();
    }

    window.handleAjaxEvent = function(data) {
        if (data.status === "success") {
            if (window.redrawGraph) window.redrawGraph();
        }
    }

    window.handleClearEvent = function(data) {
        if (data.status === "success" && window.redrawGraph) window.redrawGraph();
    }

    window.prepareSubmit = function(isCanvas) {
        if (!isCanvas) {
            document.getElementById('pointForm:hiddenX').value = "";
            document.getElementById('pointForm:hiddenY').value = "";
        }
        return true;
    }
})();