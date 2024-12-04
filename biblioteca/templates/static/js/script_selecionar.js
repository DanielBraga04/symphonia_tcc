        const canvas = document.getElementById("canvas");
        const ctx = canvas.getContext("2d");
        
        // Variáveis para a seleção de ROIs
        let rois = [];
        let startX, startY, isSelecting = false;

        // Carrega e desenha a imagem no canvas
        const img = new Image();
        img.src = imgUrl;
        img.onload = function() {
            canvas.width = img.width; // Tamanho original da imagem
            canvas.height = img.height; // Tamanho original da imagem
            ctx.drawImage(img, 0, 0);
        };

        // Evento de mouse para começar a seleção
        canvas.addEventListener("mousedown", (e) => {
            const rect = canvas.getBoundingClientRect();
            startX = e.clientX - rect.left;
            startY = e.clientY - rect.top;
            isSelecting = true;
        });

        // Evento de mouse para desenhar o ROI durante a seleção
        canvas.addEventListener("mousemove", (e) => {
            if (isSelecting) {
                const rect = canvas.getBoundingClientRect();
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0); // Redesenha a imagem

                const currentX = e.clientX - rect.left;
                const currentY = e.clientY - rect.top;

                // Desenha todos os ROIs
                ctx.strokeStyle = "red";
                ctx.lineWidth = 2;
                rois.forEach((roi) => {
                    ctx.strokeRect(roi.x, roi.y, roi.width, roi.height);
                });

                // Desenha o novo ROI sendo selecionado
                ctx.strokeStyle = "red"; // Cor diferente para o novo ROI
                ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
            }
        });

        // Evento de mouse para finalizar o ROI
        canvas.addEventListener("mouseup", (e) => {
            isSelecting = false;
            const rect = canvas.getBoundingClientRect();
            const x = startX;
            const y = startY;
            const width = e.clientX - rect.left - startX;
            const height = e.clientY - rect.top - startY;

            // Adiciona o ROI à lista
            if (width > 0 && height > 0) { // Verifica se o ROI tem dimensões válidas
                rois.push({ x, y, width, height });
            }

            // Redesenha a imagem e todos os ROIs
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
            ctx.strokeStyle = "red";
            ctx.lineWidth = 2;
            rois.forEach((roi) => {
                ctx.strokeRect(roi.x, roi.y, roi.width, roi.height);
            });
        });

        // Evento para retroceder a última seleção
        window.addEventListener("keydown", (e) => {
            if (e.ctrlKey) { // Verifica se a tecla CTRL está pressionada
                rois.pop(); // Remove a última seleção
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0);
                ctx.strokeStyle = "red";
                ctx.lineWidth = 2;
                rois.forEach((roi) => {
                    ctx.strokeRect(roi.x, roi.y, roi.width, roi.height);
                });
            }
        });

        // Envia os ROIs para o servidor ao submeter o formulário
        document.getElementById("roiForm").addEventListener("submit", (e) => {
            document.getElementById("roisInput").value = JSON.stringify(rois);
        });