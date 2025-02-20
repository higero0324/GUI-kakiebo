const fs = require('fs');
const path = require('path');

// データを JSON として保存する関数（エラーハンドリング付き）
function saveData(data, fileName = 'data.json') {
    const filePath = path.join(__dirname, fileName);
    try {
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
        console.log(`Data saved successfully to ${filePath}`);
    } catch (err) {
        console.error(`Error saving data to ${filePath}:`, err);
    }
}

// 保存された JSON データを読み込む関数（エラーハンドリング付き）
function loadData(fileName = 'data.json') {
    const filePath = path.join(__dirname, fileName);
    try {
        if (fs.existsSync(filePath)) {
            const raw = fs.readFileSync(filePath);
            console.log(`Data loaded successfully from ${filePath}`);
            return JSON.parse(raw);
        } else {
            console.warn(`Data file not found at ${filePath}`);
            return null;
        }
    } catch (err) {
        console.error(`Error loading data from ${filePath}:`, err);
        return null;
    }
}

module.exports = { saveData, loadData };
