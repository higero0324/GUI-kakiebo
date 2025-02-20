const fs = require('fs');
const path = require('path');

// データを JSON として保存する関数
function saveData(data, fileName = 'data.json') {
    const filePath = path.join(__dirname, fileName);
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

// 保存された JSON データを読み込む関数
function loadData(fileName = 'data.json') {
    const filePath = path.join(__dirname, fileName);
    if (fs.existsSync(filePath)) {
        const raw = fs.readFileSync(filePath);
        return JSON.parse(raw);
    }
    return null;
}

module.exports = { saveData, loadData };
