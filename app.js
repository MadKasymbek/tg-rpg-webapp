const tg = window.Telegram.WebApp;
tg.expand();

// ВАЖНО: Замени на свой URL от ngrok (см. инструкцию)
const API_URL = "https://a8204d7cc2ba48.lhr.life";

const elHp = document.getElementById('stat-hp');
const elDmg = document.getElementById('stat-dmg');
const elArmor = document.getElementById('stat-armor');
const elWeaponSlot = document.querySelector('#slot-weapon .slot-content');
const elArmorSlot = document.querySelector('#slot-armor .slot-content');
const elInventory = document.getElementById('inventory-grid');

// Загрузка данных с бэкенда
async function fetchPlayerData() {
    try {
        const response = await fetch(`${API_URL}/player`);
        const data = await response.json();
        renderUI(data);
    } catch (e) {
        tg.showAlert("Ошибка связи с сервером!");
    }
}

// Отправка команды на надевание предмета
async function equipItem(itemId) {
    try {
        tg.HapticFeedback.impactOccurred('light');
        await fetch(`${API_URL}/equip`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId })
        });
        // После надевания запрашиваем обновленные статы
        fetchPlayerData();
    } catch (e) {
        tg.showAlert("Не удалось надеть предмет.");
    }
}

// Отрисовка интерфейса
function renderUI(data) {
    // 1. Обновляем статы
    elHp.innerText = data.stats.hp;
    elDmg.innerText = data.stats.damage;
    elArmor.innerText = data.stats.armor;

    // 2. Обновляем экипировку
    elWeaponSlot.innerText = data.equipped.weapon ? data.equipped.weapon.icon : "Пусто";
    elArmorSlot.innerText = data.equipped.armor ? data.equipped.armor.icon : "Пусто";

    // 3. Обновляем рюкзак
    elInventory.innerHTML = "";
    data.inventory.forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `
            <div class="item-icon">${item.icon}</div>
            <div class="item-name">${item.name}</div>
        `;
        div.onclick = () => equipItem(item.id);
        elInventory.appendChild(div);
    });
}

// Запуск
fetchPlayerData();
