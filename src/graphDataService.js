const fs = require('fs');
const path = require('path');

// グラフデータを JSON として保存する関数
function saveGraphData(graphData, fileName = 'graphData.json') {
    const filePath = path.join(__dirname, fileName);
    fs.writeFileSync(filePath, JSON.stringify(graphData, null, 2));
}

// 保存された JSON グラフデータを読み込む関数
function loadGraphData(fileName = 'graphData.json') {
    const filePath = path.join(__dirname, fileName);
    if (fs.existsSync(filePath)) {
        const raw = fs.readFileSync(filePath);
        return JSON.parse(raw);
    }
    return null;
}

module.exports = { saveGraphData, loadGraphData };
