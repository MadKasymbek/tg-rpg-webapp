const tg = window.Telegram.WebApp;
tg.expand();

const API_URL = "https://8c6cde8bfadd4c.lhr.life/api";

// Получаем реальный ID пользователя из Telegram. Если тестируем в браузере — даем фейковый.
const USER_ID = tg.initDataUnsafe?.user?.id || 123456789;

const elHp = document.getElementById('stat-hp');
const elDmg = document.getElementById('stat-dmg');
const elArmor = document.getElementById('stat-armor');
const elWeaponSlot = document.querySelector('#slot-weapon .slot-content');
const elArmorSlot = document.querySelector('#slot-armor .slot-content');
const elInventory = document.getElementById('inventory-grid');

async function fetchPlayerData() {
    try {
        // Передаем USER_ID как параметр
        const response = await fetch(`${API_URL}/player?user_id=${USER_ID}`);
        const data = await response.json();
        renderUI(data);
    } catch (e) {
        tg.showAlert("Ошибка связи с сервером!");
    }
}

async function equipItem(itemId) {
    try {
        tg.HapticFeedback.impactOccurred('light');
        // Отправляем на сервер и предмет, и кто его надевает
        await fetch(`${API_URL}/equip`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: USER_ID, item_id: itemId })
        });
        fetchPlayerData();
    } catch (e) {
        tg.showAlert("Не удалось надеть предмет.");
    }
}

function renderUI(data) {
    elHp.innerText = data.stats.hp;
    elDmg.innerText = data.stats.damage;
    elArmor.innerText = data.stats.armor;

    elWeaponSlot.innerText = data.equipped.weapon ? data.equipped.weapon.icon : "Пусто";
    elArmorSlot.innerText = data.equipped.armor ? data.equipped.armor.icon : "Пусто";

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

fetchPlayerData();
