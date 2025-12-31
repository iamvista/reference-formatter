// 學術文獻格式整理工具 - 前端邏輯
// Academic Reference Formatter - Frontend Logic

let processedReferences = [];
let currentFormat = 'apa'; // 當前選擇的格式

// DOM 元素
const inputText = document.getElementById('input-text');
const parseBtn = document.getElementById('parse-btn');
const clearBtn = document.getElementById('clear-btn');
const loading = document.getElementById('loading');
const resultsContainer = document.getElementById('results-container');
const resultsTable = document.getElementById('results-table');
const resultCount = document.getElementById('result-count');
const exportBtns = document.querySelectorAll('.export-btn');
const formatBtns = document.querySelectorAll('.format-btn');
const formatDisplay = document.getElementById('format-display');

// 格式名稱映射
const formatNames = {
    'apa': 'APA 7th',
    'mla': 'MLA 9th',
    'chicago': 'Chicago 17th',
    'harvard': 'Harvard'
};

// 格式選擇按鈕點擊事件
formatBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const format = btn.dataset.format;

        // 更新按鈕樣式
        formatBtns.forEach(b => {
            b.classList.remove('active', 'bg-blue-600', 'text-white');
            b.classList.add('bg-gray-200', 'text-gray-800');
        });
        btn.classList.remove('bg-gray-200', 'text-gray-800');
        btn.classList.add('active', 'bg-blue-600', 'text-white');

        // 更新當前格式
        currentFormat = format;

        // 更新表格標題
        if (formatDisplay) {
            formatDisplay.textContent = formatNames[format];
        }

        // 如果已有結果，更新顯示
        if (processedReferences.length > 0) {
            updateReferencesFormat(format);
        }
    });
});

// 解析按鈕點擊事件
parseBtn.addEventListener('click', async () => {
    const text = inputText.value.trim();

    if (!text) {
        alert('請輸入文獻資料');
        return;
    }

    // 顯示載入中
    loading.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    parseBtn.disabled = true;

    try {
        const response = await fetch('/parse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                format: currentFormat,
                enrich: true
            })
        });

        const data = await response.json();

        if (data.success) {
            processedReferences = data.references;
            displayResults(data.references);
            resultCount.textContent = data.count;
            resultsContainer.classList.remove('hidden');
        } else {
            alert('處理失敗：' + data.error);
        }
    } catch (error) {
        alert('發生錯誤：' + error.message);
    } finally {
        loading.classList.add('hidden');
        parseBtn.disabled = false;
    }
});

// 清除按鈕點擊事件
clearBtn.addEventListener('click', () => {
    inputText.value = '';
    processedReferences = [];
    resultsContainer.classList.add('hidden');
});

// 顯示結果
function displayResults(references) {
    resultsTable.innerHTML = '';

    references.forEach((ref, index) => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';

        // 狀態圖標
        let statusIcon = '';
        let statusClass = '';

        switch (ref.status) {
            case 'complete':
                statusIcon = '✓';
                statusClass = 'text-green-600';
                break;
            case 'enriched':
                statusIcon = '⚠';
                statusClass = 'text-yellow-600';
                break;
            case 'failed':
                statusIcon = '✗';
                statusClass = 'text-red-600';
                break;
            default:
                statusIcon = '○';
                statusClass = 'text-gray-400';
        }

        row.innerHTML = `
            <td class="border border-gray-300 px-4 py-2">${index + 1}</td>
            <td class="border border-gray-300 px-4 py-2 text-center">
                <span class="${statusClass} text-xl">${statusIcon}</span>
            </td>
            <td class="border border-gray-300 px-4 py-2 text-sm text-gray-600">
                ${escapeHtml(ref.original)}
            </td>
            <td class="border border-gray-300 px-4 py-2">
                ${escapeHtml(ref.formatted)}
            </td>
        `;

        resultsTable.appendChild(row);
    });
}

// 匯出按鈕點擊事件
exportBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
        const format = btn.dataset.format;

        if (processedReferences.length === 0) {
            alert('請先解析文獻');
            return;
        }

        btn.disabled = true;
        const originalText = btn.textContent;
        btn.textContent = '處理中...';

        try {
            const response = await fetch(`/export/${format}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    references: processedReferences,
                    style: currentFormat
                })
            });

            if (response.ok) {
                if (format === 'html') {
                    // HTML 格式在新視窗開啟
                    const htmlContent = await response.text();
                    const newWindow = window.open();
                    newWindow.document.write(htmlContent);
                } else {
                    // 其他格式下載檔案
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `references.${format}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    a.remove();
                }
            } else {
                const error = await response.json();
                alert('匯出失敗：' + (error.error || '未知錯誤'));
            }
        } catch (error) {
            alert('發生錯誤：' + error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    });
});

// HTML 跳脫函數
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 更新文獻格式顯示
function updateReferencesFormat(format) {
    // 更新每個文獻的格式化顯示
    processedReferences.forEach((ref, index) => {
        // 使用已經在後端生成的所有格式版本
        if (ref.formatted_all && ref.formatted_all[format]) {
            ref.formatted = ref.formatted_all[format];
        }
    });

    // 重新顯示結果
    displayResults(processedReferences);
}
